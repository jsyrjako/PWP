from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
import json
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from ..utils import find_within_distance, require_admin
from bikinghub import db
from bikinghub.models import Location, User, Favourite, Comment, TrafficData, WeatherData
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType


class LocationCollection(Resource):

    def get(self):
        """
        List all locations
        """
        all_locations = Location.query.all()
        if not all_locations:
            raise NotFound
        location_data = [location.serialize() for location in all_locations]
        print(f"location_data: {location_data}")
        return Response(json.dumps(location_data), status=200, mimetype="application/json")

    def post(self):
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        try:
            lat = request.json.get("latitude")
            lon = request.json.get("longitude")

            if not lat or not lon:
                raise NotFound

            # query for locations within 0.05km of lat, lon
            all_locations = Location.query.all()
            if find_within_distance(lat, lon, 0.05, all_locations):
                #TODO: should also return the nearest location to the user
                return Response("Location already exists", status=409)

            location = Location()
            location.deserialize(request.json)
            db.session.add(location)
            db.session.commit()
            return Response(
                status=201, headers={"Location": url_for(location.LocationItem, location=location.id)}
            )
        except IntegrityError:
            return Response("Location already exists", status=409)

class LocationItem(Resource):

    def get(self, location):
        location_obj = Location.query.get(location.id)
        if not location_obj:
            raise NotFound
        location_doc = location_obj.serialize()
        print("location_doc", location_doc)
        return Response(json.dumps(location_doc), status=200, mimetype="application/json")

    def put(self, location):
        """
        Update a location by overwriting the entire resource
        """
        location_obj = Location.query.get(location)
        if not location_obj:
            raise NotFound
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise UnsupportedMediaType(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e
        # Fetch the existing favourite from db
        location.deserialize(request.json)
        db.session.commit()
        return Response(status=200, headers={"Location": url_for(location.LocationItem, location=location.id)})

    @require_admin
    def delete(self, location):
        db.session.delete(location)
        db.session.commit()
        return Response(status=204)

