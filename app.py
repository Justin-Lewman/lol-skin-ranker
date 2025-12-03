import math
from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd
from itertools import combinations

from reset_elo import reset_elo

app = Flask(__name__)

# Load flat JSON as a pandas DataFrame
database = pd.read_json("test_elo_data.json")

# Track already compared pairs globally
already_compared = set()  # stores "minID-maxID" strings

# Precompute all possible pairs once
all_pairs = []  # List of (id1, id2) tuples
pair_index = 0  # Tracks next pair to pick

def pair_key(a, b):
    return f"{min(a,b)}-{max(a,b)}"

def precompute_pairs(filtered_df=None):
    """
    Precompute all possible pairs of skin IDs.
    If filtered_df is None -> use entire database.
    Otherwise, use only the filtered DataFrame (e.g., selected champions).
    """
    global all_pairs, pair_index
    df = filtered_df if filtered_df is not None else database
    ids = df["ID"].tolist()
    all_pairs = [(a, b) for a, b in combinations(ids, 2)]
    random.shuffle(all_pairs)  # Randomize order
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
    """Return the next un-compared pair from precomputed pairs."""
    global pair_index
    while pair_index < len(all_pairs):
        id1, id2 = all_pairs[pair_index]
        key = pair_key(id1, id2)
        pair_index += 1
        if key not in already_compared:
            already_compared.add(key)
            skin1 = database.loc[database['ID'] == id1].iloc[0].to_dict()
            skin2 = database.loc[database['ID'] == id2].iloc[0].to_dict()
            return skin1, skin2
    return None  # All pairs exhausted

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

@app.route("/", methods=["GET", "POST"])
def index():
    champions = sorted(database['Champion'].unique())

    if request.method == "POST":
        selected = request.form.getlist("champions")
        if not selected:
            selected = champions

        # Filter database for selected champions and precompute pairs
        filtered = database[database['Champion'].isin(selected)]
        precompute_pairs(filtered_df=filtered)

        return redirect(url_for("compare", champs=",".join(selected)))

    return render_template("index.html", champions=champions)

@app.route("/compare")
def compare():
    champ_string = request.args.get("champs", "")
    selected_champs = champ_string.split(",") if champ_string else []

    # Compute progress
    if selected_champs:
        filtered = database[database['Champion'].isin(selected_champs)]
        selected_ids = set(filtered["ID"].tolist())
        total_pairs = total_possible_pairs(len(filtered))
        rated_pairs = count_rated_pairs(selected_ids=selected_ids)
    else:
        selected_ids = None
        total_pairs = total_possible_pairs(len(database))
        rated_pairs = count_rated_pairs()

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
    app.run(debug=True)
    # reset_elo()
