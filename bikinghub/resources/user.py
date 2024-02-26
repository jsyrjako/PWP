import json
from sqlite3 import IntegrityError
from flask import Response, abort, Flask, request, url_for
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from jsonschema import ValidationError, validate
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from ..utils import require_admin, require_authentication
from bikinghub import db
from bikinghub.models import Location, User, Favourite
from werkzeug.exceptions import NotFound, BadRequest, UnsupportedMediaType, Conflict



class UserCollection(Resource):
    @require_admin
    def get(self):
        body = {"users": []}
        for user in User.query.all():
            body["users"].append(user.serialize())

        return Response(json.dumps(body), 200, mimetype="application/json")

    @require_admin
    def post(self):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        try:
            pw = request.json.get("password")
            name = request.json.get("name")
            if not pw or not name:
                raise BadRequest("Name and password are required")
            user = User(name=name, password=pw)
            db.session.add(user)
            db.session.commit()
            return Response(
                status=201, headers={"User": url_for(user.UserItem, user=user)}
            )
        except IntegrityError:
            return Response("User already exists", status=409)

class UserItem(Resource):
    def get(self, user):
        """
        GET method for the user item.
        """
        body = user.serialize()
        return Response(json.dumps(body), 200, mimetype="application/json")

    @require_authentication
    def put(self, user):
        """
        PUT method for the user item. Updates the resource. Requires api authentication.
        """
        if not request.json:
            raise UnsupportedMediaType
        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            raise UnsupportedMediaType(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        # Do updates...
        try:
            old_acc_db = User.query.filter_by(name=user.name).first()
            new_user_name = request.json["name"]
            old_acc_db.name = new_user_name
            db.session.commit()
        except IntegrityError as e:
            raise Conflict(str(e)) from e

        # Fetch the existing user from db
        user.deserialize(request.json)
        db.session.commit()
        return Response(status=200, headers={"User": url_for(user.UserItem, user=user)}) # If name changed add headers={"User": url_for("api.UserItem", user=user)}

    @require_authentication
    def delete(self, user):
        """
        DELETE method for the user item. Deletes the resource. Requires api authentication.
        """
        db.session.delete(user)
        db.session.commit()
        return Response(status=204)
