import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def get_wiki_genres(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        infobox = soup.find("table", class_="infobox")

        genres = []

        # --- ORIGINAL SEARCH ---
        if infobox:
            for row in infobox.find_all("tr"):
                header = row.find("th")
                if header and header.get_text(strip=True).lower() in ["genre", "genres"]:
                    td = row.find("td")
                    if td:
                        genres = list(td.stripped_strings)
                    break

        # --- FALLBACK: search nested tables or sections ---
        if not genres and infobox:
            for th in infobox.find_all("th"):
                if th.get_text(strip=True).lower() in ["genre", "genres"]:
                    td = th.find_next_sibling("td")
                    if td:
                        genres = list(td.stripped_strings)
                    break

        return genres

    except:
        return []


 #Do James Bay with singer added
