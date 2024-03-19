"""
This module is used to define the API endpoints
and the resources that are used to handle the requests.
"""

import json
from flask import Blueprint, Response
from flask_restful import Api
from bikinghub.resources import location, user, weather, favourite
from .utils import BodyBuilder
from bikinghub.constants import LINK_RELATIONS_URL, MASON, NAMESPACE

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)

# User
api.add_resource(user.UserCollection, "/users/")
api.add_resource(user.UserItem, "/user/<user:user>/")

# Location
api.add_resource(location.LocationCollection, "/locations/")
api.add_resource(location.LocationItem, "/location/<location:location>/")

# Favourites
api.add_resource(favourite.FavouriteCollection, "/user/<user:user>/favourites/")
api.add_resource(
    favourite.FavouriteItem, "/user/<user:user>/favourite/<favourite:favourite>/"
)

# Weather
api.add_resource(weather.WeatherCollection, "/weather/")
api.add_resource(weather.WeatherItem, "/location/<location:location>/weather/")


# Entry point
@api_bp.route("/")
def entry_point():
    body = BodyBuilder()
    body.add_namespace(f"{NAMESPACE}", LINK_RELATIONS_URL)
    body.add_control_users_all()
    # body.add_control(f"{NAMESPACE}:locations-all", href="/api/locations/")
    # body.add_control(f"{NAMESPACE}:weather-all", href="/api/weather/")
    return Response(json.dumps(body), 200, mimetype=MASON)
