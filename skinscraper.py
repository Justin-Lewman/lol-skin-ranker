import json
import re
import unicodedata

import bs4
import requests
from bs4 import BeautifulSoup

class SkinScraper:
    def __init__(self, url):
        self.url = url

    def get_skin_urls(self):
        try:
            response = requests.get(self.url)
        except requests.exceptions.RequestException as e:
            print(f"timed out on {self.url}")
            print(e)
        data = response.json()["tree"][0]["children"]
        skin_list = []
        for champion in data:
            skin_list.append({"Skin": champion["label"], "Url": "https://lolskin.info/"+champion["url"]})
        return skin_list


    def clean_raw_json(self, raw_text):
        """
        Extracts the balanced JSON object that begins at `"skin": {`
        inside the lolskin.info React Flight payload.
        """
        # Find `"skin":{` position
        # pattern = r'\{\"skin\":\{'
        # start = re.findall(pattern, raw_text)
        start = raw_text.find('{\\"skin\\":{')
        if not start:
            print("couldn't find start")
        stack = []
        finish = 0
        for idx,token in enumerate(raw_text[start:]):
            if token == "{":
                stack.append("{")
            if token == "}":
                stack.pop()
                if not stack:
                    finish = idx+start+1
                    break
        if finish == 0:
            print("couldn't find finish")
        # need to find ending bracket
        raw_text = raw_text[start:finish]
        clean_text = raw_text.encode().decode('unicode_escape')

        clean_json = clean_text
        # clean_json = raw_text
        return clean_json



    def extract_json_from_url(self,url):
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", string=lambda t: t and "skin" in t and "tilePath" in t)
        if not script_tag:
            raise RuntimeError("Could not find embedded skin JSON in <script> tags.")

        script_text = script_tag.string

        # Extract the JSON portion inside the push() call
        # It looks like: self.__next_f.push([1,"5:[...JSON...]"])
        json_matches = re.findall(r'(\{.*\})', script_text, flags=re.DOTALL)

        if not json_matches:
            raise RuntimeError("Could not extract JSON object from script text.")

        # Usually the LAST {...} is the actual skin JSON object
        raw_json = json_matches[-1]
        # cleaned = raw_json.encode('utf-8').decode('unicode_escape')
        cleaned = self.clean_raw_json(raw_json)

        try:
            data = json.loads(cleaned)
            #data = data["children"][-1]
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            print("JSON failed to parse. Raw extract:")
            print(cleaned)
            raise
        return data


    def get_skin_info_using_url(self,url):
        """
        Fetches lolskin.info skin page and extracts:
          - base skin metadata
          - chroma names
          - YouTube video URLs
          - splash/loadscreen images
          - release, cost, rarity, etc.
        """
        def force_utf8(text: str) -> str:
            # Fix broken characters safely
            if not text:
                return ""
            try:
                utf8 = text.encode("utf-8", errors="replace").decode("utf-8")
                try:
                    return utf8.encode("latin1").decode("utf-8")
                except UnicodeDecodeError:
                    return utf8  # leave untouched if it wasn’t mojibake
            except:
                print(f"broke on {text}")
                return ""

        data = self.extract_json_from_url(url)
        skin_layer = data.get("skin")
        skin_info = {
            "champion": force_utf8(data.get("championName")),
            "skin_name": force_utf8(skin_layer.get("name")),
            "price": skin_layer.get("cost"),
            "release_date": skin_layer.get("release"),
            "rarity": skin_layer.get("rarity"),
            "availability": skin_layer.get("availability"),
            "loot_eligible": skin_layer.get("looteligible"),
            "skinlines": [force_utf8(line["name"]) for line in skin_layer.get("skinLines", [])],
            "universes": [force_utf8(u["name"]) for u in skin_layer.get("skinUniverses", [])],
            "description": force_utf8(skin_layer.get("description")),

            # Features
            "new_effects": skin_layer.get("newEffects", False),
            "new_animations": skin_layer.get("newAnimations", False),
            "new_recall": skin_layer.get("newRecall", False),
            "new_voice": skin_layer.get("newVoice", False),
            "new_quotes": skin_layer.get("newQuotes", False),

            # Images
            "splash": skin_layer.get("splashPath"),
            "loadscreen": skin_layer.get("loadScreenPath"),

            # Chromas
            "chromas": list(skin_layer.get("fandomChromas", dict()).keys()),

            # Videos (convert YouTube IDs -> URLs)
            "videos": [
                f"https://www.youtube.com/watch?v={vid_id}"
                for vid_id in skin_layer.get("videos", [])
                if isinstance(vid_id, str)
            ]
        }
        return skin_info