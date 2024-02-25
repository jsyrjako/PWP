from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from bikinghub.models import Location, User, TrafficData, WeatherData


class UserConverter(BaseConverter):
    def to_python(self, user):
        user = User.query.filter_by(name=user).first()
        if not user:
            raise NotFound
        return user

    def to_url(self, user):
        return str(user.name)

class FavouriteConverter(BaseConverter):
    def to_python(self, value):
        favourite = Location.query.get(value).first()
        if not favourite:
            raise NotFound
        return favourite

    def to_url(self, value):
        return value.id

class TrafficConverter(BaseConverter):
    def to_python(self, value):
        traffic = TrafficData.query.get(value).first()
        if not traffic:
            raise NotFound
        return traffic

    def to_url(self, value):
        return value.id

class WeatherConverter(BaseConverter):
    def to_python(self, value):
        weather = WeatherData.query.get(value).first()
        if not weather:
            raise NotFound
        return weather

    def to_url(self, value):
        return value.id

class LocationConverter(BaseConverter):
    def to_python(self, value):
        location = Location.query.get(value).first()
        if not location:
            raise NotFound
        return location

    def to_url(self, value):
        return value.id
