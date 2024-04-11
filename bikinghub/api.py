"""
This module is used to define the API endpoints
and the resources that are used to handle the requests.
"""

import json
from flask import Blueprint, Response, request
from flask_restful import Api
from bikinghub.models import User
from bikinghub.resources import location, user, weather, favourite
from bikinghub.constants import LINK_RELATIONS_URL, MASON_CONTENT, NAMESPACE
from .utils import BodyBuilder, create_error_response

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)

# User
api.add_resource(user.UserCollection, "/users/")
api.add_resource(user.UserItem, "/users/<user:user>/")


@api_bp.route("/login/", methods=["POST"])
def login():
    """
    Login endpoint
    """
    # if request.method == "GET":
    #    body = BodyBuilder()
    #    body.add_control_user_login()
    #    return Response(json.dumps(body), 200, mimetype=MASON_CONTENT)
    # if request.method == "POST":

    req = request.json
    if "name" not in req or "password" not in req:
        return create_error_response(400, "Invalid input", "Missing name or password")
    else:
        name = req["name"]
        password = req["password"]

        user = User.query.filter_by(name=name).first()
        if user is None or not user.check_password(password):
            return create_error_response(401, "Unauthorized", "Invalid credentials")
        else:
            return Response(
                json.dumps(
                    {
                        "message": "Login successful",
                        "api_key": user.get_api_key(),
                        "username": user.name,
                        "@controls": {
                            "self": {"href": f"/api/users/{name}/"},
                        },
                    }
                ),
                200,
            )


# Location
api.add_resource(location.LocationCollection, "/locations/")
api.add_resource(location.LocationItem, "/locations/<location:location>/")

# Favourites
api.add_resource(favourite.FavouriteCollection, "/users/<user:user>/favourites/")
api.add_resource(
    favourite.FavouriteItem, "/users/<user:user>/favourites/<favourite:favourite>/"
)

# Weather
api.add_resource(weather.WeatherCollection, "/weather/")
api.add_resource(weather.WeatherItem, "/locations/<location:location>/weather/")


# Entry point
@api_bp.route("/")
def entry_point():
    """
    Entry point for the API
    """
    body = BodyBuilder()
    body.add_namespace(f"{NAMESPACE}", LINK_RELATIONS_URL)
    body.add_control_users_all()
    # add user control
    body
    body.add_control_user_add()
    body.add_control_user_login()

    body.add_control_locations_all()
    body.add_control_weather_all()

    return Response(json.dumps(body), 200, mimetype=MASON_CONTENT)
