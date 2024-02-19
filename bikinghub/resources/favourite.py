import json
from sqlite3 import IntegrityError
from attr import validate
from flask import Response, abort, Flask, request
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from bikinghub.models import Location, User, Favourite
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType
from bikinghub import db


class FavouriteCollection(Resource):

    # Lists all the user's favourites
    def get(self, user):
        """
        List all favorite locations for user
        """
        body = {"favourites": []}
        for fav in Favourite.query.filter_by(user_id=user).all():
            body["favourites"].append(fav.to_dict())

        return Response(json.dumps(body), 200, mimetype="application/json")

    def post(self, user):
        """
        Create a new favorite location for user
        """
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e))
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e))

        location_id = request.json.get("location_id")

        location_obj = Location.query.get(location_id).first()
        if not location_obj:
            raise BadRequest
        user_obj = User.query.get(user.id).first()
        if not user_obj:
            raise BadRequest

        favourite = Favourite(
            title=request.json.get("title"),
            description=request.json.get("description"),
            location_id=location_id,
            user_id=user.id,
        )

        db.session.add(favourite)
        db.session.commit()
        return Response(
            json.dumps(favourite.serialize()), 201, mimetype="application/json"
        )


class FavoriteItem(Resource):
    def get(self, favourite):
        """
        Get user's favorite location
        """
        body = favourite.serialize()
        return Response(json.dumps(body), 200, mimetype="application/json")

    def put(self):
        """
        Update a user's favorite location by overwriting the entire resource
        """
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            raise UnsupportedMediaType(str(e))
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e))

    def delete(self):
        """
        Delete a user's favorite location
        """
        raise NotImplementedError
