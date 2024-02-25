from flask import Blueprint
from flask_restful import Api
from bikinghub.resources import location, traffic, user, weather, favourite, user

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# Location
api.add_resource(user.UserCollection, "/user/")
api.add_resource(user.UserItem, "/user/<user:user>/")

api.add_resource(location.LocationCollection, "/locations")

api.add_resource(location.LocationItem, "/location/<location:location>/")
api.add_resource(location.LocationComment, "/location/<location:location>/comments/")
#api.add_resource(location.LocationWeather, "/location/<location:location>/weather/")
#api.add_resource(location.LocationTraffic, "/location/<location:location>/traffic/")

# Favourites
api.add_resource(favourite.FavouriteCollection, "/user/<user:user>/favourites/")
api.add_resource(favourite.FavouriteItem, "/user/<user:user>/favourite/<favourite:favourite>/")

