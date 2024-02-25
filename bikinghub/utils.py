import secrets
import math
import requests
from werkzeug.exceptions import Forbidden
from flask import request
from bikinghub.models import AuthenticationKey
from bikinghub.constants import MML_URL


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
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # Radius of Earth in kilometers.
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
        obj_lat = obj['latitude']
        obj_lon = obj['longitude']
        dist = haversine(lat, lon, obj_lat, obj_lon)
        if dist <= distance:
            close_objects.append(obj)
    return close_objects


def query_fmi_open_data(lat, lon):
    """
    Query the FMI open data API for weather data
    """
    pass

def query_mml_open_data_coordinates(lat, lon):
    """
    Query the MML open data API for reverse geocoding based on coordinates
    """

    query = f"geocoding/v2/pelias/reverse?&lang=fi&sources=addresses&point.lon={lon}&point.lat={lat}"
    url = MML_URL + query

    # Make the request
    response = requests.get(url)
    json_resp = response.json()
    post_number = json_resp['features'][0]['properties']['osoite.Osoite.postinumero']

    return post_number


