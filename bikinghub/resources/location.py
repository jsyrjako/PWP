from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
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
        lat = request.json.get("lat")
        lon = request.json.get("lon")
        if not lat or not lon:
            raise NotFound
        # query for locations within 5km of lat, lon
        all_locations = Location.query.all()
        locations = find_within_distance(lat, lon, 5, all_locations)
        location_data = [location.serialize() for location in locations]

        return Response(location_data, 200, mimetype="application/json")

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

            # query for locations within 0.1km of lat, lon
            all_locations = Location.query.all()
            if find_within_distance(lat, lon, 0.1, all_locations):
                return Response("Location already exists", status=409)

            location = Location()
            location.deserialize(request.json)
            db.session.add(location)
            db.session.commit()
            return Response(
                status=201, headers={"User": url_for(location.LocationItem, location=location.id)}
            )
        except IntegrityError:
            return Response("Location already exists", status=409)

class LocationItem(Resource):

    def get(self, location):
        # location_obj = Location.query.get(location).first()
        # if not location_obj:
        #     raise NotFound
        # location_doc = location_obj.serialize()
        return Response(location, 200, mimetype="application/json")

    def put(self, location):
        """
        Update a location by overwriting the entire resource
        """
        location_obj = Location.query.get(location).first()
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
        return Response(status=200, headers={"Location": url_for("api.LocationItem", location=location.id)})

    @require_admin
    def delete(self, location):
        location_obj = Location.query.get(location).first()
        if not location_obj:
            raise NotFound
        db.session.delete(location_obj)
        db.session.commit()
        return Response(204)



class LocationComment(Resource):

    def post(self, location, comment):
        """
        Add a comment to a location
        """
        if not request.json:
            raise UnsupportedMediaType

        text = request.json.get("text")
        if not text:
            raise ValidationError("text is required")

        location_obj = Location.query.get(location).first()
        if not location_obj:
            raise NotFound
        user_obj = User.query.get(comment).first()
        if not user_obj:
            raise NotFound

        comment = Comment(text=text, user_id=user_obj.id, location_id=location_obj.id)

        try:
            comment.save()
        except IntegrityError:
            raise BadRequest("Location already in favorite list")


