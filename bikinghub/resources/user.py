import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import BadRequest, UnsupportedMediaType, Conflict
from bikinghub import db
from bikinghub.models import User
from ..utils import (
    require_admin,
    require_authentication,
    BodyBuilder,
    create_error_response,
)
from bikinghub.constants import (
    LINK_RELATIONS_URL,
    USER_PROFILE,
    MASON_CONTENT,
    NAMESPACE,
)


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
        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL) # Add namespace
        body.add_control("self", url_for("api.usercollection")) # Add self control
        body.add_control_user_add() # Add control to add a user
        body["items"] = []
        for user in User.query.all():
            item = BodyBuilder()
            item.add_control("self", url_for("api.useritem", user=user)) # Add self control
            item.add_control("profile", USER_PROFILE) # Add profile control
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON_CONTENT)

    @require_admin
    def post(self):
        """
        POST method for the user collection. Adds a new user. Requires admin authentication.
        """
        print(f"Request: {request.json}")
        print(f"Request type: {request.headers}")
        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid input", str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, "Unsupported media type", str(e))

        user = User(
            name=request.json.get("name"), password=request.json.get("password") # Get name and password from request
        )
        if User.query.filter_by(name=user.name).first():
            return create_error_response(409, "User already exists")
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
        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL) # Add namespace
        body.add_control("self", url_for("api.useritem", user=user)) # Add self control
        body.add_control("profile", USER_PROFILE) # Add profile control
        body.add_control("collection", url_for("api.usercollection")) # Add collection control
        body.add_control_user_edit(user) # Add control to edit user
        body.add_control_user_delete(user) # Add control to delete user
        body.add_control_favourites_all(user) # Add control to get all favourites
        body.add_control_locations_all() # Add control to get all locations

        body["item"] = user.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON_CONTENT)

    @require_authentication
    def put(self, user):
        """
        PUT method for the user item. Updates the resource. Requires api authentication.
        """
        try:
            validate(request.json, User.json_schema())
            print(f"User: {user}")
            print(f"Request: {request.json}")
        except ValidationError as e:
            return create_error_response(400, "Invalid input", str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, "Unsupported media type", str(e))

        if User.query.filter_by(name=request.json.get("name")).first():
            return create_error_response(409, "User already exists")
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
