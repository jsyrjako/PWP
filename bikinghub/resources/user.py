import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, Conflict
from bikinghub import db
from bikinghub.models import User
from ..utils import require_admin, require_authentication


class UserCollection(Resource):
    """
    Resource for the user collection.
    This Python class represents a resource for managing user collection with methods for
    retrieving all users and adding a new user. \n Requires admin authentication.
    """

    @require_admin
    def get(self):
        """
        Get a list of all users. Requires admin authentication.
        """
        body = {"users": []}
        for user in User.query.all():
            body["users"].append(user.serialize())

        return Response(json.dumps(body), 200, mimetype="application/json")

    @require_admin
    def post(self):
        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        user = User(
            name=request.json.get("name"), password=request.json.get("password")
        )
        if User.query.filter_by(name=user.name).first():
            raise Conflict("User already exists")
        db.session.add(user)
        db.session.commit()

        return Response(
            status=201,
            headers={"User": url_for("api.useritem", user=user)},
        )


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
        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        if User.query.filter_by(name=request.json.get("name")).first():
            raise Conflict("User already exists")
        user.deserialize(request.json)
        db.session.commit()

        return Response(
            status=204, headers={"User": url_for("api.useritem", user=user)}
        )

    @require_authentication
    def delete(self, user):
        """
        DELETE method for the user item. Deletes the resource. Requires api authentication.
        """
        db.session.delete(user)
        db.session.commit()
        return Response(status=204)
