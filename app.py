from os import error
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

        # Get user input
        country_code = request.form.get("code")

        # Validate input is not empty
        error_msg = ""
        if not country_code:
            error_msg = "Please enter valid input"
            return render_template("capital.html", error_msg=error_msg)

        # Call World Bank API
        url = f"http://api.worldbank.org/v2/country/{country_code}?format=json"
        r = requests.get(url)

        try:
            data = r.json()[1]
            capital = data[0]["capitalCity"]
            country = data[0]["name"]

            return render_template("capital.html", country=country, capital=capital)
        except:
            error_msg = "Please enter valid input"
            return render_template("capital.html", error_msg=error_msg)

    else:
        return render_template("capital.html")


@app.route("/coordinates", methods=["GET", "POST"])
def coordinates():
    if request.method == "POST":

        # Get user's input
        min_lat = request.form.get("min-lat")
        max_lat = request.form.get("max-lat")
        min_lng = request.form.get("min-lng")
        max_lng = request.form.get("max-lng")

        # Validate user input
        error_msg = ""
        if not min_lat or not max_lat or not min_lng or not max_lng:
            error_msg = "Please enter valid input"
            return render_template("coordinates.html", error_msg=error_msg)

        try:
            if (
                float(min_lat) < -90
                or float(min_lat) > 90
                or float(max_lat) < -90
                or float(max_lat) > 90
                or float(min_lng) < -180
                or float(min_lng) > 180
                or float(max_lng) < -180
                or float(max_lng) > 180
            ):
                error_msg = "Please enter valid input range. -90 to 90 for latitude and -180 to 180 for longitude."
                return render_template("coordinates.html", error_msg=error_msg)
        except:
            error_msg = "Please enter valid input"
            return render_template("coordinates.html", error_msg=error_msg)

        if float(max_lat) < float(min_lat):
            error_msg = "Minimum latitude cannot be greater than maximum latitude"
            return render_template("coordinates.html", error_msg=error_msg)

        if float(max_lng) < float(min_lng):
            error_msg = "Minimum longitude cannot be greater than maximum longitude"
            return render_template("coordinates.html", error_msg=error_msg)

        # Call World Bank API
        url = f"http://api.worldbank.org/v2/country/all?format=json&per_page=500"

        r = requests.get(url)
        data = r.json()[1]
        cities = []

        for country in data:
            try:
                if (
                    float(country["longitude"]) >= float(min_lng)
                    and float(country["longitude"]) <= float(max_lng)
                    and float(country["latitude"]) >= float(min_lat)
                    and float(country["latitude"]) <= float(max_lat)
                ):
                    cities.append(country["capitalCity"])
            except ValueError:
                print("Encountered empty string")

        return render_template(
            "coordinates.html",
            cities=cities,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
        )
    else:
        return render_template("coordinates.html")


@app.route("/route", methods=["GET", "POST"])
def route():
    if request.method == "POST":

        # Get user input and store it in a list
        cities = []
        for i in range(NUM_CITIES):
            cities.append(request.form.get(f"city-{i}"))

        # Call World Bank API and save capital city and coordinates in a new dictionary
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

        # If city entered is not in World Bank's database, show error message
        error_msg = ""
        for city in cities:
            if city not in capital_cities:
                error_msg = "One or more cities entered is invalid"
                return render_template("route.html", error_msg=error_msg)

        # Save the coordinates of the cities in a list
        coord_list = []
        for city in cities:
            if city in capital_cities:
                coord_list.append(
                    (
                        float(capital_cities[city]["latitude"]),
                        float(capital_cities[city]["longitude"]),
                    )
                )

        # Create a 2-dimensional matrix to store distance between 2 cities
        distance_matrix = []
        for i in range(NUM_CITIES):
            distance_row = []
            for j in range(NUM_CITIES):
                distance_row.append(geodesic(coord_list[i], coord_list[j]).miles)
            distance_matrix.append(distance_row)

        # Get all permutations of routes
        routes = []
        perm = permutations([*range(NUM_CITIES)])

        # Calculate total distance for all route permutations, save each route and its distance in a list
        for i in list(perm):
            distance = 0
            for j in range(NUM_CITIES - 1):
                distance += distance_matrix[i[j]][i[j + 1]]
            routes.append([i, round(distance, 0)])

        # Find path with shortest total miles travelled
        shortest_path = None
        min_distance = math.inf

        for route in routes:
            if route[1] < min_distance:
                min_distance = route[1]
                shortest_path = route[0]

        # Convert the route from index to string
        shortest_path_str = []
        for i in shortest_path:
            shortest_path_str.append(cities[i])

        min_distance = "{0:,.0f}".format(min_distance)

        return render_template(
            "route.html", path=shortest_path_str, distance=min_distance
        )
    else:
        return render_template("route.html")
