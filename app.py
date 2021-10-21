from flask import Flask, render_template, request
import requests, math
from geopy.distance import geodesic
from itertools import permutations

app = Flask(__name__)

NUM_CITIES = 4


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capital", methods=["GET", "POST"])
def capital():
    if request.method == "POST":
        country_code = request.form.get("code")
        url = f"http://api.worldbank.org/v2/country/{country_code}?format=json"

        r = requests.get(url)
        data = r.json()[1]
        capital = data[0]["capitalCity"]

        return render_template("capital.html", data=capital)

    else:
        return render_template("capital.html")


@app.route("/coordinates", methods=["GET", "POST"])
def coordinates():
    if request.method == "POST":

        min_lat = request.form.get("min-lat")
        max_lat = request.form.get("max-lat")
        min_lng = request.form.get("min-lng")
        max_lng = request.form.get("max-lng")

        url = f"http://api.worldbank.org/v2/country/all?format=json"

        r = requests.get(url)
        data = r.json()[1]
        result = []

        for country in data:
            if (
                country["longitude"] > min_lng
                and country["longitude"] < max_lng
                and country["latitude"] > min_lat
                and country["latitude"] < max_lat
            ):
                result.append(country["capitalCity"])

        return render_template("coordinates.html", data=result)
    else:
        return render_template("coordinates.html")


@app.route("/route", methods=["GET", "POST"])
def route():
    if request.method == "POST":
        # city_1 = request.form.get("city-1")
        # city_2 = request.form.get("city-2")
        # city_3 = request.form.get("city-3")
        # city_4 = request.form.get("city-4")
        city_0 = "Kuala Lumpur"
        city_1 = "Brasilia"
        city_2 = "Bangkok"
        city_3 = "New Delhi"

        url = f"http://api.worldbank.org/v2/country/all?format=json&per_page=500"

        r = requests.get(url)
        data = r.json()[1]

        for country in data:
            if country["capitalCity"] == city_0:
                coord_0 = (float(country["latitude"]), float(country["longitude"]))

            if country["capitalCity"].lower() == city_1.lower():
                coord_1 = (float(country["latitude"]), float(country["longitude"]))

            if country["capitalCity"].lower() == city_2.lower():
                coord_2 = (float(country["latitude"]), float(country["longitude"]))

            if country["capitalCity"].lower() == city_3.lower():
                coord_3 = (float(country["latitude"]), float(country["longitude"]))

        # Calculate distance between all cities - total 6 distances and save it in a matrix
        d01 = geodesic(coord_0, coord_1).miles
        d02 = geodesic(coord_0, coord_2).miles
        d03 = geodesic(coord_0, coord_3).miles
        d12 = geodesic(coord_1, coord_2).miles
        d13 = geodesic(coord_1, coord_3).miles
        d23 = geodesic(coord_2, coord_3).miles

        # This can be improved
        distance_matrix = [
            [0, d01, d02, d03],
            [d01, 0, d12, d13],
            [d02, d12, 0, d23],
            [d03, d13, d23, 0],
        ]

        list_of_routes = []

        perm = permutations([0, 1, 2, 3])

        for tuple in list(perm):
            distance = 0
            for j in range(3):
                distance += distance_matrix[tuple[j]][tuple[j + 1]]

            list_of_routes.append([tuple, round(distance, 2)])

        path = None
        min_distance = math.inf

        for route in list_of_routes:
            if route[1] < min_distance:
                min_distance = route[1]
                path = route[0]

        print(path)
        return render_template("routes.html")
    else:
        return render_template("routes.html")
