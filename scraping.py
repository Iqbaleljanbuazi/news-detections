import requests
from bs4 import BeautifulSoup
import csv
import os
import time

# --- Konfigurasi ---
OUTPUT_FILE = 'real_data.csv'
TOTAL_ARTICLES_TO_SCRAPE = 800  # Target judul berita dari MASING-MASING situs
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
MAX_PAGES_TO_CHECK = 50
RETRY_COUNT = 3
RETRY_DELAY = 5

def get_page_content(url):
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"  -> Gagal mengakses {url}. Percobaan ke-{attempt + 1} dari {RETRY_COUNT}. Error: {e}")
            if attempt < RETRY_COUNT - 1:
                print(f"  -> Mencoba lagi dalam {RETRY_DELAY} detik...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  -> Gagal total mengakses halaman setelah {RETRY_COUNT} percobaan.")
                return None

def scrape_cnn(max_articles):
    titles = []
    page = 1
    print("Memulai scraping dari CNN Indonesia...")
    while len(titles) < max_articles and page <= MAX_PAGES_TO_CHECK:
        print(f"CNN - Halaman {page}...")
        url = f"https://www.cnnindonesia.com/indeks?page={page}"
        
        response = get_page_content(url)
        if not response:
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        if not articles:
            print("Tidak ada artikel lagi di CNN Indonesia. Stop.")
            break

        for article in articles:
            title_tag = article.find('h2')
            if title_tag and len(titles) < max_articles:
                titles.append(title_tag.get_text(strip=True))
        
        print(f"  -> Terkumpul: {len(titles)} dari {max_articles}")
        page += 1
        time.sleep(1)
            
    return titles

def scrape_kompas(max_articles):
    titles = []
    page = 1
    print("\nMemulai scraping dari Kompas.com...")
    while len(titles) < max_articles and page <= MAX_PAGES_TO_CHECK:
        print(f"Kompas - Halaman {page}...")
        url = f"https://indeks.kompas.com/?page={page}"

        response = get_page_content(url)
        if not response:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        article_list = soup.find_all('div', class_='article__list')

        if not article_list:
            print("Tidak ada artikel lagi di Kompas.com. Stop.")
            break

        for article in article_list:
            title_tag = article.find('h3', class_='article__title--medium')
            if title_tag and title_tag.find('a') and len(titles) < max_articles:
                titles.append(title_tag.find('a').get_text(strip=True))

        print(f"  -> Terkumpul: {len(titles)} dari {max_articles}")
        page += 1
        time.sleep(1)

    return titles

def save_to_csv(data_list):
    file_exists = os.path.isfile(OUTPUT_FILE)
    
    try:
        with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # tulis header hanya kalau file belum ada atau kosong
            if not file_exists or os.path.getsize(OUTPUT_FILE) == 0:
                writer.writerow(['title', 'label'])
            
            for item in data_list:
                writer.writerow([item, "real"])
        print(f"\n✅ {len(data_list)} judul baru berhasil ditambahkan ke {OUTPUT_FILE}")

    except IOError as e:
        print(f"Error saat menulis ke CSV: {e}")

if __name__ == "__main__":
    all_titles = []
    
    cnn_titles = scrape_cnn(TOTAL_ARTICLES_TO_SCRAPE)
    kompas_titles = scrape_kompas(TOTAL_ARTICLES_TO_SCRAPE)
    
    all_titles.extend(cnn_titles)
    all_titles.extend(kompas_titles)
    
    if all_titles:
        save_to_csv(all_titles)
    else:
        print("\n❌ Tidak ada judul berita yang berhasil di-scrape.")
