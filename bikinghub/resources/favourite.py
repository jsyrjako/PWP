import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest
from bikinghub.models import Favourite
from bikinghub.constants import PAGE_SIZE
from bikinghub import db, cache
from ..utils import require_authentication, page_key


class FavouriteCollection(Resource):

    def _clear_cache(self, user):
        request_path = url_for("api.favouritecollection", user=user)
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[user_{user}_page_{page}]"
            cache.delete(cache_key)

    # Lists all the user's favourites
    @cache.cached(timeout=10000, make_cache_key=page_key, response_filter=lambda r: True)
    def get(self, user):
        """
        List all favorite locations for user
        """
        print("Cache miss###############################################")

        try:
            page = int(request.args.get("page", 0))
        except ValueError:
            return (400, "Invalid page value")

        remaining = (
            Favourite.query.filter_by(user=user)
            .order_by("locationId")
            .offset(page)
        )

        body = {"favourites": []}

        for fav in remaining.limit(PAGE_SIZE):
            body["favourites"].append(fav.serialize())

        # for fav in Favourite.query.filter_by(userId=user.id).all():
        #    body["favourites"].append(fav.serialize())

        response = Response(json.dumps(body), 200, mimetype="application/json")
        if len(body["favourites"]) == PAGE_SIZE:
            cache.set(page_key(), response, timeout=None)

        return response

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

        self._clear_cache(user)

        return Response(
            status=201,
            headers={
                "Location": url_for("api.favouriteitem", user=user, favourite=favourite)
            },
        )


class FavouriteItem(Resource):

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
            raise NotFound
        body = favourite.serialize()
        return Response(json.dumps(body), status=200, mimetype="application/json")

    def put(self, user, favourite):
        """
        Update a user's favorite location by overwriting the entire resource
        """
        if favourite.id not in [fav.id for fav in user.favourites]:
            raise NotFound

        try:
            validate(request.json, Favourite.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

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
            raise NotFound
        db.session.delete(favourite)
        db.session.commit()

        self._clear_cache(user)

        return Response(status=204)
