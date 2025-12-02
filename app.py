from flask import Flask, render_template, request, redirect, url_for
import random
import pandas as pd

app = Flask(__name__)

# Load flat JSON as a pandas DataFrame
database = pd.read_json("flat.json")

def get_random_skins(n):
    return database.sample(n=n).to_dict(orient='records')


@app.route("/")
def index():
    skin1, skin2 = get_random_skins(2)
    return render_template(
        "index.html",
        skin1=skin1,
        skin2=skin2
    )

@app.route("/choose", methods=["POST"])
def choose():
    chosen = request.form.get("chosen")
    print("User chose:", chosen)

    # return new skins after selecting
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
