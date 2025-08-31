import os
import re
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import db_manager
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
import nltk
import csv
from flask import send_file

# Inisialisasi Aplikasi Flask
app = Flask(__name__)
app.secret_key = 'ini-adalah-kunci-rahasia-yang-sangat-aman'

# Konfigurasi & Pemuatan Model
MODEL_PATH = os.path.join('model', 'lstm_hoax_detector.h5')
TOKENIZER_PATH = os.path.join('model', 'tokenizer.pickle')
MAX_SEQUENCE_LENGTH = 250

print("Memuat model dan tokenizer...")
try:
    model = load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("Model dan tokenizer berhasil dimuat.")
except Exception as e:
    print(f"Error saat memuat model atau tokenizer: {e}")
    model = None
    tokenizer = None

# --- Fungsi Pra-pemrosesan & Validasi Teks ---
def preprocess_text(text):
    try:
        stop_words = set(stopwords.words('indonesian'))
    except LookupError:
        nltk.download('stopwords')
        stop_words = set(stopwords.words('indonesian'))
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I | re.A)
    text = text.lower()
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

def is_mostly_gibberish(text, tokenizer_vocab, threshold=0.3):
    words = text.lower().split()
    if not words:
        return True
    known_words = sum(1 for word in words if word in tokenizer_vocab)
    recognition_ratio = known_words / len(words)
    return recognition_ratio < threshold

# --- ROUTE HALAMAN UTAMA & ABOUT ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- ROUTE PREDIKSI ---
@app.route('/predict', methods=['POST'])
def predict():
    if model is None or tokenizer is None:
        return jsonify({'error': 'Model tidak tersedia'}), 500
    try:
        data = request.get_json()
        if not data or 'news_text' not in data:
            return jsonify({'error': 'Teks berita tidak ditemukan'}), 400
        
        news_text = data['news_text']

        if not news_text.strip() or len(news_text.split()) < 7:
            return jsonify({'error': 'Teks terlalu pendek untuk dianalisis.'}), 400

        if is_mostly_gibberish(news_text, tokenizer.word_index):
            return jsonify({'error': 'Sumber belum pasti, akurasi rendah/hoax.'}), 400

        processed_text = preprocess_text(news_text)
        seq = tokenizer.texts_to_sequences([processed_text])
        padded_seq = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH)
        prediction_array = model.predict(padded_seq)
        
        confidence = float(np.max(prediction_array) * 100)
        CONFIDENCE_THRESHOLD = 75.0 

        if confidence < CONFIDENCE_THRESHOLD:
            prediction_text = 'FAKE'
            full_text_message = 'Hoax (Pola Teks Tidak Dikenali)'
        else:
            is_fake = np.argmax(prediction_array) == 0
            prediction_text = 'FAKE' if is_fake else 'REAL'
            full_text_message = 'Berita Terdeteksi Hoaks' if is_fake else 'Berita Terdeteksi Valid'
        
        db_manager.add_history(news_text, prediction_text, confidence)
        
        return jsonify({
            'prediction': prediction_text,
            'confidence': f"{confidence:.2f}",
            'full_text': full_text_message
        })

    except Exception as e:
        print(f"Terjadi error saat prediksi: {e}")
        return jsonify({'error': 'Terjadi kesalahan internal saat analisis'}), 500

# --- ROUTE HISTORY PUBLIK ---
@app.route('/history')
def public_history():
    """Menampilkan riwayat prediksi untuk semua pengguna."""
    history = db_manager.get_all_history()
    return render_template('history.html', history=history)

# --- ROUTE ADMIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = db_manager.get_admin_by_username(username)
        # Login tanpa hash password
        if admin and admin['password'] == password:
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau Password Salah!', 'error')
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    history = db_manager.get_all_history()
    return render_template('admin_dashboard.html', history=history)

# --- TAMBAH ADMIN ---
@app.route('/admin/add', methods=['GET', 'POST'])
def add_admin():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username dan password wajib diisi.', 'error')
            return render_template('add_admin.html')
        success = db_manager.add_admin(username, password)
        if success:
            flash('Admin baru berhasil ditambahkan.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Gagal menambah admin. Username mungkin sudah digunakan.', 'error')
    return render_template('add_admin.html')

# --- CRUD HISTORY ---
@app.route('/admin/history/edit/<int:id>', methods=['GET', 'POST'])
def edit_history(id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    data = db_manager.get_history_by_id(id)
    if not data:
        flash('Data tidak ditemukan.', 'error')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        text = request.form['text']
        prediction = request.form['prediction']
        confidence = request.form['confidence']
        db_manager.update_history(id, text, prediction, confidence)
        flash('Data berhasil diupdate.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_history.html', data=data)

# --- EXPORT HISTORY TO CSV ---
@app.route('/admin/export/csv')
def export_history_csv():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    filepath = 'history_export.csv'
    success = db_manager.export_history_to_csv(filepath)
    if not success:
        flash('Tidak ada data untuk diexport.', 'error')
        return redirect(url_for('admin_dashboard'))
    return send_file(filepath, as_attachment=True)

@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_history(id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    db_manager.delete_history_by_id(id)
    flash('Riwayat berhasil dihapus.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('home'))


# --- JALANKAN APP ---
if __name__ == '__main__':
    app.run(port=5000, debug=True)
