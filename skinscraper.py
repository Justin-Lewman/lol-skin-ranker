import re

import bs4
import requests
from bs4 import BeautifulSoup

class SkinScraper:
    def __init__(self, url):
        self.url = url

    def get_skins_by_champion(self):
        response = requests.get(self.url)
        data = response.json()["tree"][0]["children"]
        skin_list = []
        for champion in data:
            skin_list.append({"Champion": champion["label"].split()[-1], "Skin": champion["label"], "Url": "https://lolskin.info/"+champion["url"]})
        return skin_list

    def get_skin_info_using_url(self, skin_url):
        # response = requests.get(skin_url)
        html = requests.get(skin_url).text
        soup = BeautifulSoup(html, "html.parser")
        skin_info = dict()
        table = soup.find("table")
        if not table:
            return skin_info

        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            key = th.get_text(strip=True)
            value = " ".join(td.stripped_strings)

            # Remove time difference from Release date
            if key.lower() == "release date":
                match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
                if match:
                    value = match.group(1)

            skin_info[key] = value
        # TODO add splash, video url for animations, skin features

        return skin_info