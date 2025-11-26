import time

from json_storage import JSON_Storage
from skin import Skin
from skinscraper import SkinScraper
import random


def create_skin_objects(url_by_skin):
    # TODO construct a skin object for each skin
    all_skins = []
    storage = JSON_Storage()
    first_skin = url_by_skin[0]["Skin"]
    for i, skin in enumerate(url_by_skin):
        try:
            skin_obj = Skin(scraper.get_skin_info_using_url(skin["Url"]))
            all_skins.append(skin_obj)
            # Add delay for scraping to not get rate-limited
            wait = random.uniform(0.34512, 1.6653)
            storage.add_skin(skin_obj)
            print(f"Skin {i+1}: {skin["Skin"]} added to storage\nWaiting {wait} seconds")
            time.sleep(wait)
        except:
            print(f"ERROR OCCURRED ON {skin["Skin"]}")
            print(f"{i + 1} skins were saved, the first is {first_skin} and the last is {skin["Skin"]}")
            storage.to_flat_json("checkpoint_flat.json")
            storage.to_champ_json("checkpoint_champ.json")
            return False
    print(f"{i + 1} skins were saved, the first is {first_skin} and the last is {skin["Skin"]}")
    storage.to_flat_json("flat.json")
    storage.to_champ_json("champ.json")
    return True


if __name__ == '__main__':
    scraper = SkinScraper("https://lolskin.info/data/homepage/en-us.json")
    champ_skins = scraper.get_skin_urls()
    # champ_skins = [{'Skin': 'Reindeer Smolder', 'Url': 'https://lolskin.info//en-us/skin/901011'}, {"Skin": 'Spirit Blossom Teemo', 'Url': 'https://lolskin.info/en-us/skin/17054'}]
#     champ_skins = [{'Skin': 'Reindeer Smolder', 'Url': 'https://lolskin.info//en-us/skin/901011'},
# {'Skin': 'Smolder', 'Url': 'https://lolskin.info//en-us/skin/901000'},
# {'Skin': 'Heavenscale Smolder', 'Url': 'https://lolskin.info//en-us/skin/901001'},
#                    {'Skin': 'Prestige Winterblessed Mel', 'Url': 'https://lolskin.info/en-us/skin/800010'},
#                    {'Skin': "Risen Legend Kai'Sa", 'Url': 'https://lolskin.info/en-us/skin/145070'}]
    create_skin_objects(champ_skins)

