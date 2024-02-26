import json
from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
from bikinghub.models import Location, User, Favourite, Comment, TrafficData, WeatherData
from bikinghub import db
from ..utils import create_weather_data
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
        all_weathers = WeatherData.query.all()
        if not all_weathers:
            raise NotFound
        weather_datas = [weather.serialize() for weather in all_weathers]

        return Response(json.dumps(weather_datas), 200, mimetype="application/json")

    #def post(self, location):
    #    """
    #    Create a new weather report
    #    """
    #    try:
    #        validate(request.json, WeatherData.json_schema())
    #    except ValidationError as e:
    #        raise BadRequest(str(e)) from e
    #    except UnsupportedMediaType as e:
    #        raise UnsupportedMediaType(str(e)) from e
#
    #    # weather.deserialize(request.json)
    #    # weather.locationId = location.id
    #    # db.session.add(weather)
    #    # db.session.commit()
#
    #    return Response(
    #        status=201, headers={"WeatherData": url_for(weather.LocationWeather, location=location.id, weather=weather.id)}
    #    )

class WeatherItem(Resource):

    def get(self, location):
        """
        Get a specific weather report for a location
        """
        print(f"In WeatherItem.get: location={location}")
        weather_obj = WeatherData.query.filter_by(locationId=location.id).order_by(WeatherData.weatherTime.desc()).first()
        if not weather_obj:
            weather_obj = create_weather_data(location)
        body = weather_obj.serialize()
        return Response(body, 200, mimetype="application/json")

    #def put(self, location, weather):
    #    """
    #    Update a specific weather report for a location
    #    """
#
    #    try:
    #        validate(request.json, WeatherData.json_schema())
    #    except ValidationError as e:
    #        raise BadRequest(str(e)) from e
    #    except UnsupportedMediaType as e:
    #        raise UnsupportedMediaType(str(e)) from e
    #    weather_obj = WeatherData.query.filter_by(locationId=location).first()
    #    if not weather_obj:
    #        raise NotFound
    #    weather.deserialize(request.json)
    #    db.session.commit()
#
    #    return Response(201, headers={"WeatherData": url_for(weather.LocationWeather, location=location.id, weather=weather)})
#
    #def delete(self, location):
    #    """
    #    Delete a specific weather report for a location
    #    """
    #    weather_obj = WeatherData.query.filter_by(locationId=location).first()
    #    if not weather_obj:
    #        raise NotFound
    #    db.session.delete(weather_obj)
    #    db.session.commit()
    #    return Response(204)
