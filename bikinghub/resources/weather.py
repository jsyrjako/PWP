from sqlite3 import IntegrityError
from attr import validate
from flask import Response, abort, Flask, request
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from bikinghub.models import Location, User, Favourite, Comment, TrafficData, WeatherData
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType

class WeatherCollection(Resource):

    def get(self):
        pass

class WeatherItem(Resource):

    def get(self, location):
        """
        Get a specific weather report for a location
        """
        weather_obj = WeatherData.query.get(location).first()
        if not weather_obj:
            raise NotFound
        body = weather_obj.serialize()
        return Response(body, 200, mimetype="application/json")
    
