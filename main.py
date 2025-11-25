import time

from skin import Skin
from skinscraper import SkinScraper
import random

def create_skin_objects(skins_by_champ):
    # TODO construct a skin object for each skin
    all_skins = []
    # Step 1, test for just smolder's skins
    for skin in skins_by_champ:
        if skin["Champion"] == "Smolder":
            skin_info = scraper.get_skin_info_using_url(skin["Url"])
            skin_obj = Skin(skin["Skin"], skin_info)

            all_skins.append(skin_obj)
        # Add delay for scraping to not get rate-limited
        time.sleep(random.uniform(0.50135, 1.69))
    # Step 2, save that skin - for now a local json should be fine

    # Step 3, make and save all skin objects


if __name__ == '__main__':
    scraper = SkinScraper("https://lolskin.info/data/homepage/en-us.json")
    #champ_skins = scraper.get_skins_by_champion()
    champ_skins = [{'Champion': 'Smolder', 'Skin': 'Reindeer Smolder', 'Url': 'https://lolskin.info//en-us/skin/901011'},
{'Champion': 'Smolder', 'Skin': 'Smolder', 'Url': 'https://lolskin.info//en-us/skin/901000'},
{'Champion': 'Smolder', 'Skin': 'Heavenscale Smolder', 'Url': 'https://lolskin.info//en-us/skin/901001'}]
    create_skin_objects(champ_skins)

