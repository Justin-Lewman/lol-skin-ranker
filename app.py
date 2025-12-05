import math
from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd
from itertools import combinations
import json
import atexit
import os

from reset_elo import reset_elo

app = Flask(__name__)

# Load flat JSON as a pandas DataFrame
database = pd.read_json("test_elo_data.json")

# Track already compared pairs globally
# Load previously compared pairs
if os.path.exists("already_compared.json"):
    with open("already_compared.json", "r") as f:
        already_compared = set(json.load(f))
else:
    already_compared = set()


pair_queue = []        # List of (id1, id2) tuples for THIS session
pair_index = 0         # Tracks next index to inspect in pair_queue
accuracy_level = 5  # (1–10)


def pair_key(a, b):
    return f"{min(a,b)}-{max(a,b)}"

def precompute_pairs(filtered_df=None, accuracy=5):
    """
    Precompute the pair_queue for this session.
    For small n we use full pairwise, for large n we use tournament sampling.
    pair_queue is kept intact for the whole session (we won't pop from it).
    """
    global pair_queue, pair_index, accuracy_level

    accuracy_level = int(accuracy)
    df = filtered_df if filtered_df is not None else database
    ids = df["ID"].tolist()
    n = len(ids)
    print(f"{n} pairs on accuracy level {accuracy_level}")

    # --- Small collections: full pairwise ---
    if n <= 5:
        pair_queue = [(a, b) for a, b in combinations(ids, 2)]
        random.shuffle(pair_queue)
        pair_index = 0
        return

    target_pairs = min(n * accuracy_level, total_possible_pairs(n))

    # neighbor-biased pairs (adjacent in Elo order)
    sorted_ids = sorted(ids, key=lambda i: database.loc[database['ID'] == i, 'Elo'].iloc[0])
    neighbor_pairs = [(sorted_ids[i], sorted_ids[i+1]) for i in range(len(sorted_ids)-1)]

    # fill the rest with random unique pairs (without repeating neighbor pairs)
    all_possible = [(a, b) for a, b in combinations(ids, 2)]
    # remove neighbor pairs from pool so we don't double-add them
    pool = [p for p in all_possible if p not in neighbor_pairs and (p[1], p[0]) not in neighbor_pairs]

    remaining_needed = max(0, target_pairs - len(neighbor_pairs))
    if remaining_needed > 0 and pool:
        remaining_needed = min(remaining_needed, len(pool))
        random_pairs = random.sample(pool, remaining_needed)
    else:
        random_pairs = []

    pair_queue = neighbor_pairs + random_pairs
    random.shuffle(pair_queue)
    pair_index = 0



def count_rated_pairs(selected_ids=None):
    """Count already-compared pairs relevant to selection."""
    if selected_ids is None:
        return len(already_compared)

    c = 0
    for pair in already_compared:
        a_str, b_str = pair.split('-')
        a, b = int(a_str), int(b_str)
        if a in selected_ids and b in selected_ids:
            c += 1
    return c


def total_possible_pairs(count):
    return count * (count - 1) // 2

def choose_match():
    """Return the next unseen match from pair_queue (session pairs)."""
    global pair_index
    while pair_index < len(pair_queue):
        id1, id2 = pair_queue[pair_index]
        key = pair_key(id1, id2)
        pair_index += 1

        if key in already_compared:
            continue

        # mark as seen/rated for progress tracking (we still wait to record Elo in record_match)
        already_compared.add(key)

        skin1 = database.loc[database['ID'] == id1].iloc[0].to_dict()
        skin2 = database.loc[database['ID'] == id2].iloc[0].to_dict()
        return skin1, skin2

    return None

def record_match(winner_id, loser_id):
    K = 32
    win_idx = database.index[database['ID'] == int(winner_id)][0]
    lose_idx = database.index[database['ID'] == int(loser_id)][0]
    winner = database.loc[win_idx]
    loser = database.loc[lose_idx]

    win_confidence = 1/(1 + math.pow(10, ((winner["Elo"] - loser["Elo"])/400)))
    winner_multiplier = 1 / math.sqrt(winner['Matches']+1)
    loser_multiplier = 1 / math.sqrt(loser['Matches'] + 1)
    new_winner_elo = winner['Elo'] + math.ceil(K * winner_multiplier * win_confidence)
    new_loser_elo = loser['Elo'] - math.ceil(K * loser_multiplier * (1 - win_confidence))

    database.loc[win_idx, 'Elo'] = new_winner_elo
    database.loc[lose_idx, 'Elo'] = new_loser_elo
    database.loc[win_idx, 'Matches'] = winner['Matches'] + 1
    database.loc[lose_idx, 'Matches'] = loser['Matches'] + 1

    print(f"{winner['Skin_Name']} won and Elo is now {new_winner_elo}")
    print(f"{loser['Skin_Name']} lost and Elo is now {new_loser_elo}")

def save_state():
    # Save updated Elo + Matches
    print(already_compared)
    database.to_json("test_elo_data.json", orient="records")

    # Save compared pairs
    with open("already_compared.json", "w") as nf:
        json.dump(list(already_compared), nf)
    print("data saved")



@app.route("/", methods=["GET", "POST"])
def index():
    champions = sorted(database['Champion'].unique())

    if request.method == "POST":
        selected = request.form.getlist("champions")
        if not selected:
            selected = champions

        # Filter database for selected champions and precompute pairs
        filtered = database[database['Champion'].isin(selected)]
        precompute_pairs(filtered_df=filtered, accuracy=request.form.get("accuracy", 5))

        return redirect(url_for("compare", champs=",".join(selected)))

    return render_template("index.html", champions=champions)

@app.route("/compare")
def compare():
    champ_string = request.args.get("champs", "")
    selected_champs = champ_string.split(",") if champ_string else []

    # Compute progress using pair_queue (session pairs)
    total_pairs = len(pair_queue)
    if total_pairs > 0:
        queue_keys = {pair_key(a, b) for (a, b) in pair_queue}
        rated_pairs = sum(1 for k in queue_keys if k in already_compared)
    else:
        rated_pairs = 0

    # Pick next match
    match = choose_match()
    if not match:
        return redirect(url_for("results", champs=champ_string))

    skin1, skin2 = match

    return render_template(
        "compare.html",
        skin1=skin1,
        skin2=skin2,
        champs=",".join(selected_champs),
        progress=rated_pairs,
        total=total_pairs
    )

@app.route("/choose", methods=["POST"])
def choose():
    winner = request.form.get("winner")
    loser = request.form.get("loser")
    champs = request.form.get("champs")

    record_match(winner, loser)
    return redirect(url_for("compare", champs=champs))

@app.route("/results")
def results():
    champ_string = request.args.get("champs", "")
    selected_champs = champ_string.split(",") if champ_string else []

    if selected_champs:
        rows = database[database['Champion'].isin(selected_champs)]
    else:
        rows = database

    rows = rows.sort_values(by="Elo", ascending=False)

    return render_template(
        "results.html",
        rows=rows.to_dict(orient="records"),
        champs=champ_string
    )

if __name__ == "__main__":
    atexit.register(save_state)
    app.run(debug=True, use_reloader=False)
    # reset_elo()
