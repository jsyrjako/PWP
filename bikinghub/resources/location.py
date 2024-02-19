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

class LocationCollection(Resource):

    def get(self):
        pass

class LocationItem(Resource):

    def get(self, location):
        location_obj = Location.query.get(location).first()
        if not location_obj:
            raise NotFound
        location_doc = location_obj.serialize()
        return Response(location_doc, 200, mimetype="application/json")
    
    

class LocationComment(Resource):

    def put(self, location, comment):
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


