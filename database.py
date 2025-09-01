import os
import mysql.connector

# Konfigurasi Database MySQL
def get_db_connection():
    """Membuat dan mengembalikan koneksi ke database menggunakan variabel lingkungan dari Railway."""
    try:
        # Gunakan nama variabel lingkungan yang sesuai dengan yang ada di dashboard Railway
        conn = mysql.connector.connect(
            host=os.environ.get('MYSQLHOST'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            database=os.environ.get('MYSQLDATABASE'),
            port=int(os.environ.get('MYSQLPORT', 3306))
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error saat koneksi ke MySQL: {err}")
        return None