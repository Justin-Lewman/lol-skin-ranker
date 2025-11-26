import time

from skin import Skin
from skinscraper import SkinScraper
import random

def create_skin_objects(url_by_skin):
    # TODO construct a skin object for each skin
    all_skins = []
    for skin in url_by_skin:
        skin_obj = Skin(scraper.get_skin_info_using_url(skin["Url"]))
        all_skins.append(skin_obj)
        # Add delay for scraping to not get rate-limited
        wait = random.uniform(0.50135, 1.69)
        print(f"Skin: {skin["Skin"]} scraped, waiting {wait} seconds")
        time.sleep(wait)
    # Step 2, save the skins - for now a local json should be fine
    for skin in all_skins:
        print(skin)


if __name__ == '__main__':
    scraper = SkinScraper("https://lolskin.info/data/homepage/en-us.json")
    #champ_skins = scraper.get_skin_urls()
    champ_skins = [{'Skin': 'Reindeer Smolder', 'Url': 'https://lolskin.info//en-us/skin/901011'},
{'Skin': 'Smolder', 'Url': 'https://lolskin.info//en-us/skin/901000'},
{'Skin': 'Heavenscale Smolder', 'Url': 'https://lolskin.info//en-us/skin/901001'},
                   {'Skin': 'Prestige Winterblessed Mel', 'Url': 'https://lolskin.info/en-us/skin/800010'},
                   {'Skin': "Risen Legend Kai'Sa", 'Url': 'https://lolskin.info/en-us/skin/145070'}]
    create_skin_objects(champ_skins)

