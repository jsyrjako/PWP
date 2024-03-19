import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate
from werkzeug.exceptions import UnsupportedMediaType
from bikinghub import db, cache
from bikinghub.models import Location
from bikinghub.constants import PAGE_SIZE, CACHE_TIME
from ..utils import (
    create_error_response,
    find_within_distance,
    require_admin,
    page_key_location,
    BodyBuilder,
)
from bikinghub.constants import LINK_RELATIONS_URL, LOCATION_PROFILE, MASON, NAMESPACE
from flasgger import swag_from


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

        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationcollection"))
        body.add_control_add_location()
        body["items"] = []

        # Serialize each location and add it to the response body
        for location in Location.query.all():
            item = BodyBuilder(
                latitude=location.latitude,
                longitude=location.longitude,
                name=location.name,
            )
            item.add_control("self", url_for("api.locationitem", location=location))
            item.add_control("profile", LOCATION_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), status=200, mimetype="application/json")

    def post(self):
        """
        Create a new location
        """
        print(f"LocationCollection.post()")
        print(f"request.json: {request.json}")
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            print(f"LocationCollection.post() ValidationError: {e}")
            return create_error_response(400, str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

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
        """
        GET method for the location item
        """
        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationitem", location=location))
        body.add_control("profile", LOCATION_PROFILE)
        body.add_control("collection", url_for("api.locationcollection"))
        body.add_control_location_delete(location)
        body.add_control_location_edit(location)
        body.add_control_weather_all()

        body["item"] = location.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, location):
        """
        Update a location by overwriting the entire resource
        """
        try:
            validate(request.json, Location.json_schema())
        except ValidationError as e:
            return create_error_response(400, str(e))
        except UnsupportedMediaType as e:
            return create_error_response(415, str(e))

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
