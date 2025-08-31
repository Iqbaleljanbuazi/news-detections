import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import random

# --- Konfigurasi ---
OUTPUT_FILE = 'hoax_data.csv'
MAX_ARTICLES = 508
BASE_URL = "https://turnbackhoax.id/page/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_turnbackhoax(max_articles):
    """
    Mengambil judul berita dari TurnBackHoax.
    Akan berhenti jika target tercapai ATAU jika halaman berita sudah habis.
    """
    articles = []
    page = 1
    max_pages_to_check = 100  # Batas keamanan supaya tidak infinite loop

    print(f"Memulai scraping. Target: {max_articles} berita dari TurnBackHoax...")
    while len(articles) < max_articles and page <= max_pages_to_check:
        url = f"{BASE_URL}{page}/"
        print(f"Mengakses halaman {page}...")

        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            if response.status_code != 200:
                print(f"Halaman {page} tidak dapat diakses (Status: {response.status_code}).")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # ⚠️ Ganti selector sesuai struktur TurnBackHoax terbaru
            news_items = soup.find_all("h3", class_="jeg_post_title")

            if not news_items:
                print("Tidak ada lagi artikel di halaman ini. Proses scraping selesai.")
                break

            for item in news_items:
                if len(articles) >= max_articles:
                    break
                a_tag = item.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    articles.append([title, "fake"])

            print(f"  -> Berhasil mengumpulkan {len(articles)} dari {max_articles} artikel.")
            page += 1
            time.sleep(random.uniform(1.5, 3.5))  # jeda biar aman

        except requests.exceptions.RequestException as e:
            print(f"Terjadi error koneksi: {e}. Mencoba halaman selanjutnya...")
            page += 1
            continue

    return articles

def save_to_csv(data_list, filename):
    """
    Menyimpan data ke file CSV tanpa menumpuk duplikat.
    """
    if not data_list:
        print("\nTidak ada berita baru untuk disimpan.")
        return

    # Baca data lama kalau sudah ada
    existing_titles = set()
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_titles.add(row['title'])

    # Filter duplikat
    unique_data = [row for row in data_list if row[0] not in existing_titles]

    if not unique_data:
        print("\n⚠️ Semua berita sudah ada, tidak ada yang baru untuk disimpan.")
        return

    file_exists = os.path.isfile(filename)
    try:
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(filename) == 0:
                writer.writerow(['title', 'label'])  # header
            writer.writerows(unique_data)
        print(f"\n✅ Sukses! {len(unique_data)} berita baru ditambahkan ke '{filename}'.")
    except IOError as e:
        print(f"\nTerjadi error saat menulis ke file CSV: {e}")

if __name__ == "__main__":
    scraped_articles = scrape_turnbackhoax(MAX_ARTICLES)
    save_to_csv(scraped_articles, OUTPUT_FILE)
    print(f"\nProses Selesai. Total terkumpul: {len(scraped_articles)} artikel (termasuk duplikat sebelum difilter).")
