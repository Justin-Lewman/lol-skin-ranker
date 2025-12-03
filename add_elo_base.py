import json

from skinscraper import SkinScraper

INPUT_FILE = "test_elo_data.json"
OUTPUT_FILE = "test_elo_data.json"   # overwrite in place



def main():
    scraper = SkinScraper("https://lolskin.info/data/homepage/en-us.json")
    ids = {skin_dict["Skin"]:skin_dict["Url"].split("/")[-1] for skin_dict in scraper.get_skin_urls()}

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for skin in data:
        skin["Elo"] = 1000
        skin["ID"] = ids[skin["Skin_Name"]]


    # Save back to disk
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Updated IDs and ELO scores successfully.")

if __name__ == "__main__":
    main()
