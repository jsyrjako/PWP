import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import UnsupportedMediaType, BadRequest
from bikinghub import db, cache
from bikinghub.models import Location
from bikinghub.constants import PAGE_SIZE, CACHE_TIME
from ..utils import find_within_distance, require_admin, page_key_location


class LocationCollection(Resource):
    """
    Collection of all locations
    """

    # Inspiration from course material
    def _clear_cache(self):
        request_path = url_for("api.locationcollection")
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[page_{page}]"
            cache.delete(cache_key)

    # Lists all the user's favourites
    # Cache from course material
    @cache.cached(
        timeout=CACHE_TIME,
        make_cache_key=page_key_location,
        response_filter=lambda r: True,
    )
    def get(self):
        """
        List all locations
        """
        print("Cache miss location")

        try:
            page = int(request.args.get("page", 0))
        except ValueError:
            return (400, "Invalid page value")

        all_locations = Location.query.order_by(Location.id).offset(page)

        body = {"locations": []}

        for location in all_locations.limit(PAGE_SIZE):
            body["locations"].append(location.serialize())

        response = Response(json.dumps(body), status=200, mimetype="application/json")
        if len(body["locations"]) == PAGE_SIZE:
            cache.set(page_key_location(), response, timeout=None)

        return response

    def post(self):
        """
        Create a new location
        """
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        lat = request.json.get("latitude")
        lon = request.json.get("longitude")

        # query for locations within 0.05km of lat, lon
        all_locations = Location.query.all()
        if find_within_distance(lat, lon, 0.05, all_locations):
            return Response("Location already exists", status=409)

        location = Location()
        location.deserialize(request.json)
        db.session.add(location)
        db.session.commit()

        self._clear_cache()

        return Response(
            status=201,
            headers={"Location": url_for("api.locationitem", location=location)},
        )


class LocationItem(Resource):
    """
    Represents a single location
    """

    # Inspiration from course material
    def _clear_cache(self):
        request_path = url_for("api.locationcollection")
        for page in range(0, PAGE_SIZE):
            cache_key = request_path + f"[page_{page}]"
            cache.delete(cache_key)

    def get(self, location):
        location_doc = location.serialize()
        print("location_doc", location_doc)
        return Response(
            json.dumps(location_doc), status=200, mimetype="application/json"
        )

    def put(self, location):
        """
        Update a location by overwriting the entire resource
        """
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            raise BadRequest(str(e)) from e
        except UnsupportedMediaType as e:
            raise UnsupportedMediaType(str(e)) from e

        location.deserialize(request.json)
        db.session.commit()

        self._clear_cache()

        return Response(status=204)

    @require_admin
    def delete(self, location):
        """
        Delete a location, requires admin authentication
        """
        db.session.delete(location)
        db.session.commit()

        self._clear_cache()

        return Response(status=204)
