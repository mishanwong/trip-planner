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
        cities = []
        for i in range(NUM_CITIES):
            cities.append(request.form.get(f"city-{i}"))

        coord_list = []

        url = f"http://api.worldbank.org/v2/country/all?format=json&per_page=500"

        r = requests.get(url)
        data = r.json()[1]

        capital_cities = {}

        for country in data:
            if not country["capitalCity"]:
                continue
            capital_cities[country["capitalCity"]] = {
                "latitude": country["latitude"],
                "longitude": country["longitude"],
            }

        # Validate cities entry

        for city in cities:
            if city in capital_cities:
                coord_list.append(
                    (
                        float(capital_cities[city]["latitude"]),
                        float(capital_cities[city]["longitude"]),
                    )
                )

        distance_matrix = []

        for i in range(NUM_CITIES):  # [0, 1, 2, 3]
            distance_row = []
            for j in range(NUM_CITIES):  # [0, 1, 2, 3]
                distance_row.append(geodesic(coord_list[i], coord_list[j]).miles)
            distance_matrix.append(distance_row)

        # Get all permutation of routes
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

        path_list = []
        for i in path:
            path_list.append(cities[i])

        print(path_list)
        return render_template("routes.html")
    else:
        return render_template("routes.html")
