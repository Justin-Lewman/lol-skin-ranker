import time

from json_storage import JSON_Storage
from skin import Skin
from skinscraperOLD import SkinScraperOld
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
            wait = random.uniform(0.54512, 1.62931)
            storage.add_skin(skin_obj)
            print(f"Skin {i+1}: {skin["Skin"]} added to storage\nWaiting {wait} seconds")
            time.sleep(wait)
        except Exception as e:
            print(e)
            print(f"ERROR OCCURRED ON {skin["Skin"]}")
            if i > 0:
                print(f"{i} skins were saved, the first is {first_skin} and the last is {url_by_skin[i-1]["Skin"]}")
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
    # champ_skins = [{'Skin': 'Zaahen', 'Url': 'https://lolskin.info/en-us/skin/904000'}, {"Skin": 'Spirit Blossom Teemo', 'Url': 'https://lolskin.info/en-us/skin/17054'}, {'Skin': 'La Ilusión Draven', 'Url':'https://lolskin.info/en-us/skin/119048'},
    #                {'Skin': 'Count Vladimir', 'Url':'https://lolskin.info/en-us/skin/8001'}]
    create_skin_objects(champ_skins)

