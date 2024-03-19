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
    FAVORITE_PROFILE,
    MASON,
    NAMESPACE,
)
from bikinghub import db, cache
from ..utils import create_error_response, require_authentication, page_key, BodyBuilder


class FavouriteCollection(Resource):

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
        List all favorite locations for user
        """
        print("Cache miss favourite")

        try:
            page = int(request.args.get("page", 0))
        except ValueError:
            return create_error_response(400, "Invalid page number")

        remaining = (
            Favourite.query.filter_by(user=user).order_by("location_id").offset(page)
        )

        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.favouritecollection", user=user))
        body.add_control_favourite_add(user)
        body["items"] = []
        for fav in remaining.limit(PAGE_SIZE):
            item = BodyBuilder()
            item.add_control(
                "self", url_for("api.favouriteitem", user=user, favourite=fav)
            )
            item.add_control("profile", FAVORITE_PROFILE)
            body["items"].append(item)

        response = Response(json.dumps(body), 200, mimetype=MASON)
        if len(body["items"]) == PAGE_SIZE:
            cache.set(page_key(), response, timeout=None)

        return response

    def post(self, user):
        """
        Create a new favorite location for user
        """
        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            return create_error_response(400, str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

        favourite = Favourite()
        favourite.deserialize(request.json)
        favourite.user = user
        db.session.add(favourite)
        db.session.commit()

        self._clear_cache(user)

        return Response(
            status=201,
            headers={
                "Location": url_for("api.favouriteitem", user=user, favourite=favourite)
            },
        )


class FavouriteItem(Resource):

    # Inspiration from course material
    def _clear_cache(self, user):
        request_path = url_for("api.favouritecollection", user=user)
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[user_{user}_page_{page}]"
            cache.delete(cache_key)

    def get(self, user, favourite):
        """
        Get user's favorite location
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favorite not found")
        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control(
            "self", url_for("api.favouriteitem", user=user, favourite=favourite)
        )
        body.add_control("profile", FAVORITE_PROFILE)
        body.add_control("collection", url_for("api.favouritecollection", user=user))
        body.add_control(
            "edit", url_for("api.favouriteitem", user=user, favourite=favourite)
        )
        body.add_control(
            "delete", url_for("api.favouriteitem", user=user, favourite=favourite)
        )
        body.add_control_locations_all()

        body["item"] = favourite.serialize()
        return Response(json.dumps(body), status=200, mimetype=MASON)

    def put(self, user, favourite):
        """
        Update a user's favorite location by overwriting the entire resource
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favorite not found")

        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            return create_error_response(400, str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

        # Fetch the existing favourite from db
        favourite.deserialize(request.json)
        db.session.commit()

        self._clear_cache(user)

        return Response(status=204)

    @require_authentication
    def delete(self, user, favourite):
        """
        Delete a user's favorite location
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            return create_error_response(404, "Favorite not found")
        db.session.delete(favourite)
        db.session.commit()

        self._clear_cache(user)

        return Response(status=204)
