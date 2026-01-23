import requests
from bs4 import BeautifulSoup

def get_wiki_genres(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)


    soup = BeautifulSoup(response.text, "html.parser")

    infobox = soup.find("table", class_=lambda x: x and "infobox" in x)
    genres = []

    if not infobox:
        return genres

    for row in infobox.find_all("tr"):
        th = row.find("th")
        if th and th.get_text(strip=True).lower() in ("genre", "genres"):
            td = row.find("td")
            if td:
                genres = [g.strip() for g in td.stripped_strings]
            break


    cleaned = []
    for value in genres:
        if not(value.isdigit()) and not(value in ['[', ']']) :
            cleaned.append(value)
    return cleaned


#print(get_wiki_genres("https://en.wikipedia.org/wiki/Crystal_Waters"))
