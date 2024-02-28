from flask import Blueprint
from flask_restful import Api
from bikinghub.resources import location, user, weather, favourite

api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(api_bp)

# User
api.add_resource(user.UserCollection, "/user/")
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
