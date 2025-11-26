import json
import re

import bs4
import requests
from bs4 import BeautifulSoup

class SkinScraper2:
    def __init__(self, url):
        self.url = url

    def get_skin_urls(self):
        response = requests.get(self.url)
        data = response.json()["tree"][0]["children"]
        skin_list = []
        for champion in data:
            skin_list.append({"Skin": champion["label"], "Url": "https://lolskin.info/"+champion["url"]})
        return skin_list


    def extract_skin_json(self, raw_text):
        """
        Extracts the balanced JSON object that begins at `"skin": {`
        inside the lolskin.info React Flight payload.
        """

        # Find `"skin":{` position
        start = re.search(r'"skin"\s*:\s*\{', raw_text)
        if not start:
            raise ValueError("Could not find the 'skin' root in the raw text")

        start_index = start.start() + raw_text[start.start():].find('{')
        # Walk forward to find matching closing brace
        depth = 0
        i = start_index
        in_string = False
        escape = False

        while i < len(raw_text):
            c = raw_text[i]

            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_string = not in_string
            elif not in_string:
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        # Extract inclusive object
                        json_str = raw_text[start_index:i + 1]
                        print(json_str)
                        return json.loads(json_str)

            i += 1

        raise ValueError("Unbalanced braces while extracting skin JSON")


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
        # cleaned = raw_json.replace("\\\"", "\"")
        # cleaned = raw_json.encode('utf-8').decode('unicode_escape')
        # TODO this needs to be better cleaned, it technically works for now but introduces a TON of typos to gurantee it wont crash


        try:
            data = self.extract_skin_json(raw_json)
            print(data)
            #data = data["children"][-1]
        except Exception:
            print("JSON failed to parse. Raw extract:")
            print(raw_json)
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
        data = self.extract_json_from_url(url)
        while "main" not in data["className"]:
            data = data["children"][-1]
        data = data["children"][-2][-1]
        skin_layer = data.get("skin")
        skin_info = {
            "champion": data.get("championName"),
            "skin_name": skin_layer.get("name"),
            "price": skin_layer.get("cost"),
            "release_date": skin_layer.get("release"),
            "rarity": skin_layer.get("rarity"),
            "availability": skin_layer.get("availability"),
            "loot_eligible": skin_layer.get("looteligible"),
            "skinlines": [line["name"] for line in skin_layer.get("skinLines", [])],
            "universes": [u["name"] for u in skin_layer.get("skinUniverses", [])],
            "description": skin_layer.get("description"),
            "voice_actors": skin_layer.get("voiceActor", []),

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