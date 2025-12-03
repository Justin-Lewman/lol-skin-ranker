import json

INPUT_FILE = "test_elo_data.json"
OUTPUT_FILE = "test_elo_data.json"   # overwrite in place



def reset_elo():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for skin in data:
        skin["Elo"] = 1000
        skin["Uncertainty"] = 40
        skin["Matches"] = 0


    # Save back to disk
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("ELO reset successfully.")

if __name__ == "__main__":
    reset_elo()
