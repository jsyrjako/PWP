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

class CommentCollection(Resource):
    
    def get(self):
        """Get all users comments"""
        comments = Comment.query.all()
        return {"comments": [c.serialize() for c in comments]}
    
    
class CommentItem(Resource):
    
    def get(self, comment):
        """Get a specific comment"""
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_doc = comment_obj.serialize()
        return Response(comment_doc, 200, mimetype="application/json")
    
    def delete(self, comment):
        """Delete a comment"""
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_obj.delete()
        return Response("Comment deleted", 200, mimetype="application/json")
    
    def put(self, comment):
        """Update a comment"""
        if not request.json:
            raise UnsupportedMediaType
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_obj.update(request.json)
        return Response("Comment updated", 200, mimetype="application/json")
