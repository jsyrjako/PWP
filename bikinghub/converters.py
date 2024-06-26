"""
This file contains the converters for the URL routing.
The converters basic structures are taken from the course material.
"""

from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from bikinghub.models import Location, User, Favourite


class UserConverter(BaseConverter):
    """
    Converts between User objects and their string representations
    """

    def to_python(self, value):
        user = User.query.filter_by(name=value).first()
        if not user:
            raise NotFound
        return user

    def to_url(self, value):
        print(f"UserConverter: {value}")
        return str(value.name)


class FavouriteConverter(BaseConverter):
    """
    Converts between Favourite objects and their string representations
    """

    def to_python(self, value):
        favourite = Favourite.query.filter_by(id=value).first()
        if not favourite:
            raise NotFound
        return favourite

    def to_url(self, value):
        print(f"FavouriteConverter: {value}")
        return str(value.id)


# class TrafficConverter(BaseConverter):
#    def to_python(self, value):
#        traffic = TrafficData.query.get(id=value).first()
#        if not traffic:
#            raise NotFound
#        return traffic
#
#    def to_url(self, value):
#        return value.id


# class WeatherConverter(BaseConverter):
#    def to_python(self, value):
#        weather = WeatherData.query.filter_by(id=value).first()
#        if not weather:
#            raise NotFound
#        return weather
#
#    def to_url(self, weather):
#        return str(weather.id)


class LocationConverter(BaseConverter):
    """
    Converts between Location objects and their string representations
    """

    def to_python(self, value):
        location = Location.query.filter_by(id=value).first()
        if not location:
            raise NotFound
        return location

    def to_url(self, value):
        print(f"LocationConverter: {value}")
        return str(value.id)
