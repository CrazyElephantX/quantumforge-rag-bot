# scripts/fetch_roscosmos.py
import requests
from bs4 import BeautifulSoup
import os
import time
import random

# --- Настройки ---
OUTPUT_DIR = "knowledge_base"
USER_AGENT = "QuantumForgeBot/1.0 (Educational Project)"

# Список ключевых тем (названия файлов + URL'ы Википедии)
PAGES = [
    ("Юрий_Гагарин", "https://ru.wikipedia.org/wiki/%D0%93%D0%B0%D0%B3%D0%B0%D1%80%D0%B8%D0%BD,_%D0%AE%D1%80%D0%B8%D0%B9_%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B5%D0%B5%D0%B2%D0%B8%D1%87"),
    ("Валентина_Терешкова", "https://ru.wikipedia.org/wiki/%D0%A2%D0%B5%D1%80%D0%B5%D1%88%D0%BA%D0%BE%D0%B2%D0%B0,_%D0%92%D0%B0%D0%BB%D0%B5%D0%BD%D1%82%D0%B8%D0%BD%D0%B0_%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%BD%D0%B0"),
    ("Спутник-1", "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D1%83%D1%82%D0%BD%D0%B8%D0%BA-1"),
    ("Восток", "https://ru.wikipedia.org/wiki/%D0%92%D0%BE%D1%81%D1%82%D0%BE%D0%BA_(%D0%BA%D0%BE%D1%81%D0%BC%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D0%BA%D0%BE%D1%80%D0%B0%D0%B1%D0%BB%D1%8C)"),
    ("МКС", "https://ru.wikipedia.org/wiki/%D0%9C%D0%B5%D0%B6%D0%B4%D1%83%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D0%B0%D1%8F_%D0%BA%D0%BE%D1%81%D0%BC%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F_%D1%81%D1%82%D0%B0%D0%BD%D1%86%D0%B8%D1%8F"),
    ("Протон-М", "https://ru.wikipedia.org/wiki/%D0%9F%D1%80%D0%BE%D1%82%D0%BE%D0%BD-%D0%9C"),
    ("Ангара", "https://ru.wikipedia.org/wiki/%D0%90%D0%BD%D0%B3%D0%B0%D1%80%D0%B0_(%D1%80%D0%B0%D0%BA%D0%B5%D1%82%D0%B0)"),
    ("Луна-25", "https://ru.wikipedia.org/wiki/%D0%9B%D1%83%D0%BD%D0%B0-25"),
    ("Н1", "https://ru.wikipedia.org/wiki/%D0%9D1_(%D1%80%D0%B0%D0%BA%D0%B5%D1%82%D0%B0-%D0%BD%D0%BE%D1%81%D0%B8%D1%82%D0%B5%D0%BB%D1%8C)"),
    ("Буран", "https://ru.wikipedia.org/wiki/%D0%91%D1%83%D1%80%D0%B0%D0%BD_(%D0%BA%D0%BE%D1%81%D0%BC%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D0%BA%D0%BE%D1%80%D0%B0%D0%B1%D0%BB%D1%8C)"),
]

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table", "sup", ".mw-editsection"]):
        tag.decompose()
    article = soup.find("main") or soup.find("article") or soup.find("div", {"id": "bodyContent"})
    if not article:
        return None
    text = article.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:5000]  # Ограничим до 5000 символов


def fetch_page(filename, url):
    headers = {"User-Agent": USER_AGENT}
    try:
        time.sleep(2 + random.uniform(0, 1))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = clean_text(response.text)
        if text:
            with open(f"{OUTPUT_DIR}/{filename}.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[OK] {filename}")
        else:
            print(f"[No Text] {filename}")
    except Exception as e:
        print(f"[Error] {filename}: {e}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Загружаем статьи о российской космонавтике...\n")
    for title, url in PAGES:
        fetch_page(title, url)
    print("\n✅ Загрузка завершена.")