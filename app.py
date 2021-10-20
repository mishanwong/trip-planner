from flask import Flask, render_template, request
import urllib.request, json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capital", methods=["GET", "POST"])
def capital():
    if request.method == "POST":
        country_code = request.form.get("code")
        url = f"http://api.worldbank.org/v2/country/{country_code}?format=json"

        response = urllib.request.urlopen(url)
        data = response.read()
        dict = json.loads(data)
        return render_template("capital.html", capital=dict)
    else:
        return render_template("capital.html")


@app.route("/coordinates")
def coordinates():
    if request.method == "POST":
        return render_template("coordinates.html")
    else:
        return render_template("coordinates.html")


@app.route("/route")
def route():
    return "Route"
