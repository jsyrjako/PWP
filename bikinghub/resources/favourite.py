import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import UnsupportedMediaType
from bikinghub.models import Favourite
from bikinghub.constants import (
    PAGE_SIZE,
    CACHE_TIME,
    LINK_RELATIONS_URL,
    FAVOURITE_PROFILE,
    MASON_CONTENT,
    NAMESPACE,
)
from bikinghub import db, cache
from ..utils import create_error_response, require_authentication, page_key, BodyBuilder


class FavouriteCollection(Resource):
    """
    Resource for handling a collection of user's favourite locations
    """

    # Inspiration from course material
    def _clear_cache(self, user):
        request_path = url_for("api.favouritecollection", user=user)
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[user_{user}_page_{page}]"
            cache.delete(cache_key)

    # Lists all the user's favourites
    # Cache from course material
    @cache.cached(
        timeout=CACHE_TIME, make_cache_key=page_key, response_filter=lambda r: True
    )
    def get(self, user):
        """
        List all favourite locations for user
        """
        print("Cache miss favourite")

        page = int(request.args.get("page", 0))  # Get the page number

        remaining = (
            Favourite.query.filter_by(user=user).order_by("location_id").offset(page)
        )

        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)  # Add namespace
        body.add_control(
            "self", url_for("api.favouritecollection", user=user)
        )  # Add self control
        body.add_control_favourite_add(user)  # Add control to add a favourite
        body.add_control("user", url_for("api.useritem", user=user))
        body["items"] = []
        for fav in remaining.limit(PAGE_SIZE):
            print(f"Favourite: {fav}")
            item = BodyBuilder(
                title=fav.title, id=fav.id, location_id=fav.location_id
            )  # Create a new item
            item.add_control(
                "self", url_for("api.favouriteitem", user=user, favourite=fav)
            )
            item.add_control("profile", FAVOURITE_PROFILE)  # Add profile control
            body["items"].append(item)

        response = Response(
            json.dumps(body), 200, mimetype=MASON_CONTENT
        )  # Create response

        # Cache the response if it's a full page
        if len(body["items"]) == PAGE_SIZE:
            cache.set(page_key(), response, timeout=None)

        return response

    def post(self, user):
        """
        Create a new favourite location for user
        """
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            return create_error_response(400, str(e))
        # Not needed if request.json raises 415 error correctly
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

        favourite = Favourite()  # Create a new favourite
        favourite.deserialize(request.json)
        favourite.user = user
        db.session.add(favourite)
        db.session.commit()

        self._clear_cache(user)  # Clear the cache

        return Response(
            status=201,
            headers={
                "Location": url_for("api.favouriteitem", user=user, favourite=favourite)
            },
        )


class FavouriteItem(Resource):
    """
    Resource for handling a single user's favourite location
    """

    # Inspiration from course material
    def _clear_cache(self, user):
        request_path = url_for("api.favouritecollection", user=user)
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[user_{user}_page_{page}]"
            cache.delete(cache_key)

    def get(self, user, favourite):
        """
        Get user's favourite location
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favourite not found")
        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)  # Add namespace
        body.add_control(
            "self",
            url_for(
                "api.favouriteitem", user=user, favourite=favourite
            ),  # Add self control
        )
        body.add_control("profile", FAVOURITE_PROFILE)  # Add profile control
        body.add_control(
            "collection", url_for("api.favouritecollection", user=user)
        )  # Add collection control
        body.add_control_favourite_delete(
            user, favourite
        )  # Add control to delete a favourite
        body.add_control_favourite_edit(
            user, favourite
        )  # Add control to edit a favourite
        body.add_control_locations_all()  # Add control to get all locations

        body.add_control_favourite_get(
            user, favourite
        )  # Add control to get all favourites

        body["item"] = favourite.serialize()
        return Response(json.dumps(body), status=200, mimetype=MASON_CONTENT)

    def put(self, user, favourite):
        """
        Update a user's favourite location by overwriting the entire resource
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favourite not found")

        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            return create_error_response(400, str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

        # Fetch the existing favourite from db
        favourite.deserialize(request.json)
        db.session.commit()

        self._clear_cache(user)  # Clear the cache

        return Response(status=204)

    @require_authentication
    def delete(self, user, favourite):
        """
        Delete a user's favourite location
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favourite not found")
        db.session.delete(favourite)
        db.session.commit()

        self._clear_cache(user)  # Clear the cache

        return Response(status=204)
