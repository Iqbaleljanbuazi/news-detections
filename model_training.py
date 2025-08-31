import os
import re
import pandas as pd
import numpy as np
import pickle
from nltk.corpus import stopwords
import nltk

from sklearn.model_selection import train_test_split
# PERUBAHAN: Mengimpor langsung dari tensorflow.keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

# --- Konfigurasi Global ---
MAX_NB_WORDS = 50000  # Ukuran maksimum vocabulary
MAX_SEQUENCE_LENGTH = 250  # Panjang maksimum setiap kalimat/judul
EMBEDDING_DIM = 100  # Dimensi vektor untuk setiap kata
MODEL_DIR = 'model'
MODEL_PATH = os.path.join(MODEL_DIR, 'lstm_hoax_detector.h5')
TOKENIZER_PATH = os.path.join(MODEL_DIR, 'tokenizer.pickle')

# --- Fungsi Pra-pemrosesan Teks ---
def preprocess_text(text):
    """Membersihkan dan memproses teks input."""
    # Pastikan stopwords sudah diunduh
    try:
        stop_words = set(stopwords.words('indonesian'))
    except LookupError:
        print("Stopwords NLTK untuk Bahasa Indonesia belum diunduh. Mengunduh sekarang...")
        nltk.download('stopwords')
        stop_words = set(stopwords.words('indonesian'))
        
    # Hilangkan karakter selain huruf dan spasi
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    text = text.lower()
    # Hapus stopwords (kata-kata umum seperti 'dan', 'di', 'yang')
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

def train():
    """Fungsi utama untuk melatih dan menyimpan model."""
    print("Memulai proses training model...")

    # 1. Muat dan Gabungkan Data
    # Pastikan nama file sesuai dengan yang Anda miliki
    try:
        df_fake = pd.read_csv('hoax_data.csv') # Ganti jika nama file berbeda
        df_real = pd.read_csv('real_data.csv') # Ganti jika nama file berbeda
    except FileNotFoundError as e:
        print(f"Error: File data tidak ditemukan. Pastikan file 'hoax_data.csv' dan 'real_data.csv' ada di direktori yang sama.")
        print(e)
        return

    df = pd.concat([df_fake, df_real], ignore_index=True)
    df = df.sample(frac=1).reset_index(drop=True) # Acak data
    print(f"Total data yang dimuat: {len(df)} baris.")
    print("Contoh data:")
    print(df.head())
    
    # 2. Pra-pemrosesan Data Teks
    print("\nMelakukan pra-pemrosesan teks...")
    df['title'] = df['title'].astype(str).apply(preprocess_text)
    
    # 3. Tokenisasi dan Padding
    print("Melakukan tokenisasi dan padding sekuens...")
    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
    tokenizer.fit_on_texts(df['title'].values)
    
    X = tokenizer.texts_to_sequences(df['title'].values)
    X = pad_sequences(X, maxlen=MAX_SEQUENCE_LENGTH)
    
    # 4. Siapkan Label
    # Mengubah label 'fake'/'real' menjadi format numerik [1,0] untuk fake dan [0,1] untuk real
    Y = pd.get_dummies(df['label'], columns=['fake', 'real']).values
    
    # 5. Split Data Training dan Testing
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42, stratify=Y)
    print(f"Ukuran data training: {X_train.shape[0]}")
    print(f"Ukuran data testing: {X_test.shape[0]}")

    # 6. Bangun Arsitektur Model LSTM
    print("\nMembangun model LSTM...")
    model = Sequential()
    model.add(Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=X.shape[1]))
    model.add(Dropout(0.2))
    model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(2, activation='softmax')) # 2 neuron output: 'fake' dan 'real'
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    
    # 7. Latih Model
    print("\nMemulai training...")
    epochs = 5
    batch_size = 64
    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, Y_test))
    
    # 8. Evaluasi Model
    accr = model.evaluate(X_test, Y_test)
    print(f'Akurasi pada data tes: {accr[1]*100:.2f}%')

    # 9. Simpan Model dan Tokenizer
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print(f"\nMenyimpan model ke {MODEL_PATH}")
    model.save(MODEL_PATH)
    
    print(f"Menyimpan tokenizer ke {TOKENIZER_PATH}")
    with open(TOKENIZER_PATH, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    print("\nProses training selesai dan file telah disimpan.")

if __name__ == '__main__':
    train()
