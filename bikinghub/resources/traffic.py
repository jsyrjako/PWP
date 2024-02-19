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

class TrafficCollection(Resource):

    def get(self):
        pass

class TrafficItem(Resource):

    def get(self, traffic):
        traffic_obj = TrafficData.query.get(traffic).first()
        if not traffic_obj:
            raise NotFound
        traffic_doc = traffic_obj.serialize()
        return Response(traffic_doc, 200, mimetype="application/json")

class TrafficLocation(Resource):

    def put(self, traffic, location):
        """
        Add a traffic report to a location
        """
        raise NotImplementedError
    