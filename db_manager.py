import database # Impor file database.py untuk mendapatkan koneksi

def add_history(text, prediction, confidence):
    """Menambahkan entri baru ke tabel history."""
    conn = database.get_db_connection()
    if conn is None: return
    cursor = conn.cursor()
    cursor.execute('INSERT INTO history (text, prediction, confidence) VALUES (%s, %s, %s)',
                 (text, prediction, confidence))
    conn.commit()
    cursor.close()
    conn.close()

def get_admin_by_username(username):
    """Mencari admin berdasarkan username."""
    conn = database.get_db_connection()
    if conn is None: return None
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
    admin_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return admin_data

def get_all_history():
    """Mengambil semua data dari tabel history."""
    conn = database.get_db_connection()
    if conn is None: return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM history ORDER BY timestamp DESC')
    history_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return history_data

# CRUD Tambahan
def get_history_by_id(id):
    """Mengambil satu data history berdasarkan ID."""
    conn = database.get_db_connection()
    if conn is None: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM history WHERE id = %s', (id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def update_history(id, text, prediction, confidence):
    """Update data history berdasarkan ID."""
    conn = database.get_db_connection()
    if conn is None: return
    cursor = conn.cursor()
    cursor.execute('UPDATE history SET text=%s, prediction=%s, confidence=%s WHERE id=%s', (text, prediction, confidence, id))
    conn.commit()
    cursor.close()
    conn.close()

def export_history_to_csv(filepath):
    """Export seluruh data history ke file CSV."""
    import csv
    data = get_all_history()
    if not data:
        return False
    keys = data[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    return True

def delete_history_by_id(id):
    """Menghapus entri history berdasarkan ID."""
    conn = database.get_db_connection()
    if conn is None: return

    cursor = conn.cursor()
    cursor.execute('DELETE FROM history WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()

# Tambah admin baru
def add_admin(username, password):
    """Menambahkan admin baru ke tabel admin."""
    conn = database.get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO admin (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Gagal menambah admin: {e}")
        return False
    finally:
        cursor.close()
        conn.close()