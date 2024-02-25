import secrets
import math
import requests
from werkzeug.exceptions import Forbidden
from flask import request
from bikinghub.models import AuthenticationKey
from bikinghub.constants import MML_URL, MML_API_KEY, FMI_FORECAST_URL, SLIPPERY_URL


def require_admin(func):
    """
    Check if the request is made by an admin
    """

    def wrapper(*args, **kwargs):
        key_hash = AuthenticationKey.key_hash(
            request.headers.get("Bikinghub-Api-Key", "").strip()
        )
        db_key = AuthenticationKey.query.filter_by(key=key_hash, admin=True).first()
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden

    return wrapper


def require_authentication(func):
    """
    Check if the request is made by an authenticated user
    """

    def wrapper(*args, **kwargs):
        key_hash = AuthenticationKey.key_hash(
            request.headers.get("Bikinghub-Api-Key", "").strip()
        )
        db_key = AuthenticationKey.query.filter_by(key=key_hash).first()
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden

    return wrapper


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
        obj_lat = obj["latitude"]
        obj_lon = obj["longitude"]
        dist = haversine(lat, lon, obj_lat, obj_lon)
        if dist <= distance:
            close_objects.append(obj)
    return close_objects


def query_fmi_open_data(lat, lon):
    """
    Query the FMI open data API for weather data
    """
    pass


def query_slipperiness(municipality: str) -> bool:
    """
    Query the Slipperiness API for slipperiness data
    """
    query = f"{SLIPPERY_URL}/warnings"
    response = requests.get(query)
    json_resp = response.json()
    filtered_data = [
        item
        for item in json_resp
        if item["city"].lower().strip() == municipality.lower().strip()
    ]
    sorted_data = sorted(filtered_data, key=lambda x: x["created_at"], reverse=True)
    most_recent = sorted_data[:10]
    return most_recent


def query_fmi_forecast(district, municipality):
    """
    Query the FMI API for weather forecast
    """
    # ?place=kaijonharju&area=oulu
    fmi_query = f"{FMI_FORECAST_URL}?place={district}&area={municipality}"
    response = requests.get(fmi_query)
    json_resp = response.json()
    return json_resp


def query_mml_open_data_coordinates(lat, lon):
    """
    Query the MML open data API for reverse geocoding based on coordinates \n
    Requires MML_API_KEY to be set in constants.py
    """

    pelias_query = (
        MML_URL
        + f"/geocoding/v2/pelias/reverse?&lang=fi&sources=addresses&point.lon={lon}&point.lat={lat}"
        + f"&api-key={MML_API_KEY}"
    )

    response = requests.get(pelias_query)
    json_resp = response.json()
    post_number = json_resp["features"][0]["properties"]["osoite.Osoite.postinumero"]
    municipality_name = json_resp["features"][0]["properties"]["kuntanimiFin"]

    # Create bounding box for lat and lon
    upper_left = f"{lon-0.005},{lat-0.005}"
    lower_right = f"{lon+0.005},{lat+0.005}"
    bbox = f"{upper_left},{lower_right}"

    # lat 65.0219, lon 25.4827
    # f"https://avoin-paikkatieto.maanmittauslaitos.fi/geographic-names/features/v1/collections/places/items?placeType=3010105,3020105&bbox=25.4777,65.0169,25.4877,65.0269"

    place_name_query = (
        f"{MML_URL}"
        + f"/geographic-names/features/v1/collections/places/items?placeType=3010105,3020105&bbox={bbox}"
    )
    place_name_response = requests.get(place_name_query)
    place_name_json = place_name_response.json()
    district = place_name_json["features"][0]["properties"]["name"][0]["spelling"]

    return_str = {
        "municipality": municipality_name,
        "postnumber": post_number,
        "district": district,
    }
    return return_str
