"""
This module contains utility functions for the Bikinghub API
- require_admin: Decorator to check if the request is made by an admin
- require_authentication: Decorator to check if the request is made by an authenticated user
- haversine: Calculate the great circle distance in kilometers between two points
- find_within_distance: Find all the objects within a certain distance from a point
- create_weather_data: Create weather data for a location
"""

import os
import json
import secrets
import math
from functools import wraps
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import requests
from werkzeug.exceptions import Forbidden
from flask import request, url_for, Response
from bikinghub import db
from bikinghub.models import AuthenticationKey, WeatherData, User, Location, Favourite
from bikinghub.constants import (
    MML_URL,
    FMI_FORECAST_URL,
    NAMESPACE,
    ERROR_PROFILE,
    MASON_CONTENT,
)


def create_error_response(status_code, title, message=None):
    """
    This function uses the MasonBuilder to create a Mason formatted error response.
    The error response includes a link to the error profile.

    Returns:
        Response: A Flask Response object with the error details and status code.
    """
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON_CONTENT)


class MasonBuilder(dict):
    """
    Taken from course materials

    ---

    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {"name": uri}

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class BodyBuilder(MasonBuilder):

    # region User
    def add_control_users_all(self):
        """
        Adds a control to the object for getting all users
        """
        self.add_control(
            f"{NAMESPACE}:users-all",
            href=url_for("api.usercollection"),
            method="GET",
            title="Get all users",
        )

    def add_control_user_add(self):
        """
        Adds a control to the object for adding a new user
        """
        self.add_control(
            f"{NAMESPACE}:user-add",
            href=url_for("api.usercollection"),
            method="POST",
            title="Add a new user",
            encoding="json",
            schema=User.json_schema(),
        )

    def add_control_user_delete(self, user):
        """
        Adds a control to the object for deleting a user
        """
        self.add_control(
            f"{NAMESPACE}:user-delete",
            href=url_for("api.useritem", user=user),
            method="DELETE",
            title="Delete a user",
        )

    def add_control_user_edit(self, user):
        """
        Adds a control to the object for editing a user
        """
        self.add_control(
            f"{NAMESPACE}:user-edit",
            href=url_for("api.useritem", user=user),
            method="PUT",
            title="Edit a user",
            encoding="json",
            schema=User.json_schema(),
        )

    # endregion

    # region Location
    def add_control_locations_all(self):
        """
        Adds a control to the object for getting all locations
        """
        self.add_control(
            f"{NAMESPACE}:locations-all",
            href=url_for("api.locationcollection"),
            method="GET",
            title="Get all locations",
        )

    def add_control_add_location(self):
        """
        Adds a control to the object for adding a new location
        """
        self.add_control(
            f"{NAMESPACE}:location-add",
            href=url_for("api.locationcollection"),
            method="POST",
            title="Add a new location",
            encoding="json",
            schema=Location.json_schema(),
        )

    def add_control_location_delete(self, location):
        """
        Adds a control to the object for deleting a location
        """
        self.add_control(
            f"{NAMESPACE}:location-delete",
            href=url_for("api.locationitem", location=location),
            method="DELETE",
            title="Delete a location",
        )

    def add_control_location_edit(self, location):
        """
        Adds a control to the object for editing a location
        """
        self.add_control(
            f"{NAMESPACE}:location-edit",
            href=url_for("api.locationitem", location=location),
            method="PUT",
            title="Edit a location",
            encoding="json",
            schema=Location.json_schema(),
        )

    # endregion

    # region Weather
    def add_control_weather_all(self):
        """
        Adds a control to the object for getting all weather data
        """
        self.add_control(
            f"{NAMESPACE}:weather-all",
            href=url_for("api.weathercollection"),
            method="GET",
            title="Get all weather data",
        )

    # endregion

    # region Favourite
    def add_control_favourites_all(self, user):
        """
        Adds a control to the object for getting all favourite locations
        """
        self.add_control(
            f"{NAMESPACE}:favourites-all",
            href=url_for("api.favouritecollection", user=user),
            method="GET",
            title="Get all favourite locations",
        )

    def add_control_favourite_add(self, user):
        """
        Adds a control to the object for adding a new favourite location
        """
        self.add_control(
            f"{NAMESPACE}:favourite-add",
            href=url_for("api.favouritecollection", user=user),
            method="POST",
            title="Add a new favourite location",
            encoding="json",
            schema=Favourite.json_schema(),
        )

    def add_control_favourite_delete(self, user, favourite):
        """
        Adds a control to the object for deleting a favourite location
        """
        self.add_control(
            f"{NAMESPACE}:favourite-delete",
            href=url_for("api.favouriteitem", user=user, favourite=favourite),
            method="DELETE",
            title="Delete a favourite location",
        )

    def add_control_favourite_edit(self, user, favourite):
        """
        Adds a control to the object for editing a favourite location
        """
        self.add_control(
            f"{NAMESPACE}:favourite-edit",
            href=url_for("api.favouriteitem", user=user, favourite=favourite),
            method="PUT",
            title="Edit a favourite location",
            encoding="json",
            schema=Favourite.json_schema(),
        )


# endregion


def require_admin(func):
    """
    Check if the request is made by an admin
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        print("ADMIN CHECK")
        api_key = request.headers.get("Bikinghub-Api-Key", "").strip()
        print(f"API KEY: {api_key}")
        if not api_key or len(api_key) == 0:
            raise Forbidden
        key_hash = AuthenticationKey.key_hash(api_key)
        db_key = AuthenticationKey.query.filter_by(admin=True).first()
        if not db_key:
            raise Forbidden
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)

    return wrapper


def require_authentication(func):
    """
    Check if the request is made by an authenticated user
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("Bikinghub-Api-Key", "").strip()
        if not api_key or len(api_key) == 0:
            raise Forbidden
        key_hash = AuthenticationKey.key_hash(api_key)
        db_key = AuthenticationKey.query.filter_by(key=key_hash).first()
        if not db_key:
            raise Forbidden
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)

    return wrapper


# From stack Overflow
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers.
    return c * r


def find_within_distance(lat, lon, distance, all_locations):
    """
    Find all the objects within a certain distance from a point
    - lat (float): Latitude of the point
    - lon (float): Longitude of the point
    - distance (float): Distance in kilometers
    - objects (list of locations) -- locations model needed??
    """
    close_objects = []
    for obj in all_locations:
        obj_lat = obj.latitude
        obj_lon = obj.longitude
        dist = haversine(lat, lon, obj_lat, obj_lon)
        if dist <= distance:
            close_objects.append(obj)
    return close_objects


def create_weather_data(location):
    """
    Fetches weather data from an external API using the latitude and longitude of the provided location.
    It then parses the fetched data, creates a new WeatherData object for each forecast in the data, and stores these objects in the database.
    The function returns the first WeatherData object created.

    Returns:
    WeatherData: The first WeatherData object created from the fetched weather data.
    """
    latitude = location.latitude
    longitude = location.longitude
    weather_data = fetch_weather_data(latitude, longitude)
    weathers = []

    for forecast in weather_data["forecasts"]["forecast"]:
        rain = forecast["Precipitation1h"]
        temp = forecast["Temperature"]
        temp_feels = forecast["FeelsLike"]
        wind_speed = forecast["WindSpeedMS"]
        wind_direction = forecast["WindDirection"]

        symbol_id = int(forecast["SmartSymbol"])
        symbols = next(
            (
                symbol
                for symbol in weather_data["forecasts"]["symbols"]
                if symbol["id"] == symbol_id
            ),
            None,
        )
        weather_desc = symbols["text_fi"]

        weather_time = datetime.strptime(forecast["isolocaltime"], "%Y-%m-%dT%H:%M:%S")

        weather = WeatherData(
            rain=rain,
            temperature=temp,
            temperature_feel=temp_feels,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            weather_description=weather_desc,
            location_id=location.id,
            weather_time=weather_time,
        )

        db.session.add(weather)
        db.session.commit()

        weathers.append(weather)

    print(f"weather: [{weathers[0]}]")

    return weathers[0]


def fetch_weather_data(lat, lon):
    """
    Fetch weather data from the FMI open data API
    """
    # print(f"fetch_weather_data: lat: {lat}, lon: {lon}")
    location = query_mml_open_data_coordinates(lat, lon)
    # print(f"location: {location}")
    forecasts = query_fmi_forecast(location["district"], location["municipality"])
    # print(f"forecasts: {forecasts}")

    return {
        "location": location,
        "forecasts": forecasts,
    }


# def query_slipperiness(municipality: str) -> bool:
#     """
#     Query the Slipperiness API for slipperiness data
#     """
#     query = f"{SLIPPERY_URL}/warnings"
#     response = requests.get(query, timeout=5)
#     json_resp = response.json()
#     filtered_data = [
#         item
#         for item in json_resp
#         if item["city"].lower().strip() == municipality.lower().strip()
#     ]
#     sorted_data = sorted(filtered_data, key=lambda x: x["created_at"], reverse=True)
#     most_recent = sorted_data[:10]
#     return most_recent


def query_fmi_forecast(district, municipality):
    """
    Query the FMI API for weather forecast
    """
    # ?place=kaijonharju&area=oulu
    fmi_query = f"{FMI_FORECAST_URL}?place={district}&area={municipality}"
    # print(f"fmi_query: {fmi_query}")
    response = requests.get(fmi_query, timeout=5)
    json_resp = response.json()
    # print(f"json_resp: {json_resp}")

    forecast_values = json_resp["forecastValues"]
    symbol_descriptions = json_resp["symbolDescriptions"]
    day_length = json_resp["dayLengthValues"][0]
    # print(f"forecast_values: {forecast_values}")
    # print(f"symbol_descriptions: {symbol_descriptions}")
    # print(f"day_length: {day_length}")
    rtn = {
        "forecast": forecast_values,
        "symbols": symbol_descriptions,
        "day_length": day_length,
    }
    # print(f"fmi_data: {rtn}")
    return rtn


def query_mml_open_data_coordinates(lat, lon):
    """
    Query the MML open data API for reverse geocoding based on coordinates \n
    Requires MML_API_KEY to be set in constants.py
    """

    pelias_query = (
        MML_URL
        + f"/geocoding/v2/pelias/reverse?&lang=fi&sources=addresses&point.lon={lon}&point.lat={lat}"
        + f"&api-key={SECRETS.MML_API_KEY}"
    )

    # print(f"pelias_query: {pelias_query}")
    response = requests.get(pelias_query, timeout=5)
    # print(f"response: {response.json()}")
    json_resp = response.json()
    post_number = json_resp["features"][0]["properties"]["osoite.Osoite.postinumero"]
    municipality_name = json_resp["features"][0]["properties"]["kuntanimiFin"]
    # print(f"post_number: {post_number}, municipality_name: {municipality_name}")

    # Create bounding box for lat and lon
    upper_left = f"{lon-0.005},{lat-0.005}"
    lower_right = f"{lon+0.005},{lat+0.005}"
    bbox = f"{upper_left},{lower_right}"

    # lat 65.0219, lon 25.4827
    # f"https://avoin-paikkatieto.maanmittauslaitos.fi/
    # +geographic-names/features/v1/collections/places/items?
    # +placeType=3010105,3020105&bbox=25.4777,65.0169,25.4877,65.0269"

    place_name_query = (
        f"{MML_URL}"
        + "/geographic-names/features/v1/collections/places/items"
        + f"?placeType=3010105,3020105&bbox={bbox}"
        + f"&api-key={SECRETS.MML_API_KEY}"
    )
    # print(f"place_name_query: {place_name_query}")
    place_name_response = requests.get(place_name_query, timeout=5)
    place_name_json = place_name_response.json()
    # print(f"place_name_json: {place_name_json}")
    district = place_name_json["features"][0]["properties"]["name"][0]["spelling"]
    # print(f"district: {district}")

    return_str = {
        "municipality": municipality_name.lower(),
        "postnumber": post_number.lower(),
        "district": district.lower(),
    }
    print(f"mml_data: {return_str}")
    return return_str


# From course material
def page_key(*args, **kwargs):
    """
    Generate a cache key for a page
    """
    user = kwargs.get("user")
    page = request.args.get("page", 0)
    request_path = url_for("api.favouritecollection", user=user)
    return request_path + f"[user_{user}_page_{page}]"


# From course material
def page_key_location(*args, **kwargs):
    """
    Generate a cache key for a page
    """
    page = request.args.get("page", 0)
    request_path = url_for("api.locationcollection")
    return request_path + f"[page_{page}]"


@dataclass(frozen=True)
class SECRETS:
    load_dotenv(find_dotenv())

    MML_API_KEY = os.environ.get("MML_API_KEY", "")
