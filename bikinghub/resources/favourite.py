import json
from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Resource
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
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
        for fav in Favourite.query.filter_by(userId=user.id).all():
            body["favourites"].append(fav.serialize())

        return Response(json.dumps(body), 200, mimetype="application/json")

    def post(self, user):
        """
        Create a new favorite location for user
        """
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        favourite = Favourite()
        favourite.deserialize(request.json)
        favourite.user = user
        db.session.add(favourite)
        db.session.commit()
        return Response(
            status=201,
            headers={
                "Favourite": url_for(
                    favourite.FavouriteItem, user=user, favourite=favourite
                )
            },
        )


class FavouriteItem(Resource):
    def get(self, user, favourite):
        """
        Get user's favorite location
        """
        if favourite not in user.favourites:
            raise NotFound
        body = favourite.serialize()
        return Response(json.dumps(body), 200, mimetype="application/json")

    def put(self, user, favourite):
        """
        Update a user's favorite location by overwriting the entire resource
        """
        if favourite not in user.favourites:
            raise NotFound
        # if not request.json:
        #    raise UnsupportedMediaType
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            raise UnsupportedMediaType(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e
        # Fetch the existing favourite from db
        favourite.deserialize(request.json)
        db.session.commit()
        return Response(200)

    def delete(self, user, favourite):
        """
        Delete a user's favorite location
        """
        if favourite not in user.favourites:
            raise NotFound

        db.session.delete(favourite)
        db.session.commit()
        return Response(status=204)
