import json
from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
from bikinghub.models import Location, User, Favourite, Comment, TrafficData, WeatherData
from bikinghub import db
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType


# Query Weather from database if recent (<2 h) and near location
# If not, query weather from API
# Store weather in database
# Return weather

class WeatherCollection(Resource):

    def get(self):
        """"
        Get all weather reports
        """
        body = {"weather_locations": []}
        for weather in WeatherData.query.all():
            body["weather_locations"].append(weather.serialize())

        return Response(json.dumps(body), 200, mimetype="application/json")

    def post(self):
        """
        Create a new weather report
        """
        try:
            validate(request.json, WeatherData.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        weather = WeatherData()
        weather.deserialize(request.json)
        db.session.add(weather)
        db.session.commit()

        return Response(
            status=201, headers={"WeatherData": url_for(weather.LocationWeather, location=weather.id)}
        )

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

    def put(self, location, weather):
        """
        Update a specific weather report for a location
        """
        data = request.get_json()
        weather_obj = WeatherData.query.filter_by(locationId=location).first()
        if not weather_obj:
            raise NotFound

        weather.deserialize(request.json)
        db.session.add(weather)
        db.session.commit()

        return Response(200)

    def delete(self, location):
        """
        Delete a specific weather report for a location
        """
        weather_obj = WeatherData.query.filter_by(locationId=location).first()
        if not weather_obj:
            raise NotFound
        db.session.delete(weather_obj)
        db.session.commit()
        return Response(204)
