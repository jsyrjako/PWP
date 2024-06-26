"""
This module contains the tests for the resources in the API.
Test are besed on http://flask.pocoo.org/en/3.0.x/testing/
and course materials are used for guidance.
"""

import json
import pytest
from conftest import populate_db
from sqlalchemy.engine import Engine
from sqlalchemy import event
from bikinghub import db
from bikinghub.constants import MASON_CONTENT, JSON_CONTENT, LINK_RELATIONS_URL
from jsonschema import validate
from bikinghub.utils import SECRETS


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enable foreign key constraints in the SQLite database upon connection
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _get_user_json(number=1):
    # Creates a valid user JSON object for testing
    return {
        "name": f"extra-user{number}",
        "password": "extra-password",
    }


def _get_location_json(number=1):
    # Creates a valid location JSON object for testing
    return {
        "name": f"extra-location{number}",
        "latitude": 65.55785284617326,
        "longitude": 25.068937083629477,
    }


def _get_favourite_json(number=1):
    # Creates a valid favourite JSON object for testing
    return {
        "title": f"extra-favourite{number}",
        "description": f"extra-description{number}",
        "user_id": number,
        "location_id": number,
    }


def _get_admin_auth_headers(
    content_type=JSON_CONTENT,
    api_key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4",
):
    # Creates valid admin headers for testing
    return {
        "Content-Type": f"{content_type}",
        "Bikinghub-Api-Key": f"{api_key}",
    }


def _get_user_auth_headers(
    content_type=JSON_CONTENT,
    api_key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4",
):
    # Creates valid user headers for testing
    return {
        "Content-Type": f"{content_type}",
        "Bikinghub-Api-Key": f"{api_key}",
    }


def check_namespace(client, body):
    """
    Checks the namespace of a JSON object
    """
    ns_href = body["@namespaces"]["bikinghub"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def check_control_get_method(client, ctrl, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    """

    href = obj["@controls"][ctrl]["href"]
    headers = _get_admin_auth_headers()
    resp = client.get(href, headers=headers)
    assert resp.status_code == 200


def check_control_delete_method(client, ctrl, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an item
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    headers = _get_admin_auth_headers()
    resp = client.delete(href, headers=headers)
    assert resp.status_code == 204


def check_control_put_method(client, ctrl, obj, body=None):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    """
    print(f"Checking control {ctrl} with {obj} and {body}")
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    validate(body, schema)
    headers = _get_admin_auth_headers()
    resp = client.put(href, json=body, headers=headers)
    print(f"Response is {resp}")
    assert resp.status_code == 204


def check_control_post_method(client, ctrl, obj, body=None):
    """
    Checks a POST type control from a JSON object be it root document or an item
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    validate(body, schema)
    headers = _get_admin_auth_headers()
    resp = client.post(href, json=body, headers=headers)
    assert resp.status_code == 201


@pytest.mark.usefixtures("client")
class TestUserCollection:
    """
    This class contains tests for the UserCollection resource.
    """

    URL = "/api/users/"

    def test_entry_point(self, client):
        """
        Test the entry point of the API
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            resp = test_client.get("/api/")
            assert resp.status_code == 200
            data = json.loads(resp.data)

            check_namespace(test_client, data)
            check_control_get_method(test_client, "bikinghub:users-all", data)

    def test_get(self, client):
        """
        Test the GET method for the UserCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

            resp = test_client.get(self.URL, headers=_get_admin_auth_headers())
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(test_client, body)
            check_control_post_method(
                test_client, "bikinghub:user-add", body, _get_user_json()
            )
            assert len(body["items"]) == 3
            for item in body["items"]:
                check_control_get_method(test_client, "self", item)
                check_control_get_method(test_client, "profile", item)

    def test_post(self, client):
        """
        Test the POST method for the UserCollection resource.
        """
        with client.app_context():
            populate_db(db)
            test_client = client.test_client()

            valid = _get_user_json()

            # test with wrong content type and valid rights
            resp = test_client.post(
                self.URL,
                data=json.dumps(valid),
                headers={"Content-Type": "image/gif"},
            )
            assert resp.status_code == 415

            # test with invalid content and valid rights
            invalid_user = _get_user_json().pop("name")
            # invalid_user = {**invalid_user, **{"extra_key": "extra_value"}}
            resp = test_client.post(self.URL, json=invalid_user)
            assert resp.status_code == 400

            # test with valid and see that it exists afterward
            resp = test_client.post(self.URL, json=valid)
            assert resp.status_code == 201

            # send same data again for 409
            resp = test_client.post(self.URL, json=valid)
            assert resp.status_code == 409


@pytest.mark.usefixtures("client")
class TestUserItem:
    """
    This class contains tests for the UserItem resource.
    """

    URL = "/api/users/user37722c77-8004-41d7-993f-ef4f24356ce3/"
    URL2 = "/api/users/user135b18a6-b150-498a-810d-b09ab98e1bcc/"
    NEW_URL = "/api/users/extra-user1/"
    INVALID_URL = "/api/users/user10/"

    def test_get(self, client):
        """
        Test the GET method for the UserItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Test with empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            populate_db(db)

            # Test with valid user
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(test_client, body)
            check_control_get_method(test_client, "self", body)
            check_control_get_method(test_client, "profile", body)
            check_control_get_method(test_client, "collection", body)
            check_control_get_method(test_client, "bikinghub:favourites-all", body)
            check_control_get_method(test_client, "bikinghub:locations-all", body)

            check_control_put_method(
                test_client, "bikinghub:user-edit", body, _get_user_json()
            )

            resp = test_client.get(self.URL2)
            body = json.loads(resp.data)
            check_control_delete_method(test_client, "bikinghub:user-delete", body)

            # Test with invalid user
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_put(self, client):
        """
        Test the PUT method for the UserItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Test with empty database
            resp = test_client.put(
                self.URL,
                data=json.dumps(_get_user_json()),
                headers=_get_user_auth_headers(),
            )

            populate_db(db)
            valid = _get_user_json()

            # Wrong content type, valid rights
            resp = test_client.put(
                self.URL,
                data=json.dumps(valid),
                headers=_get_user_auth_headers(content_type="text/html"),
            )
            assert resp.status_code == 415

            # test invalid data and valid rights
            invalid = _get_user_json().pop("name")
            resp = test_client.put(
                self.URL, data=json.dumps(invalid), headers=_get_user_auth_headers()
            )
            assert resp.status_code == 400

            # test valid data and valid rights
            resp = test_client.put(
                self.URL, json=valid, headers=_get_user_auth_headers()
            )
            assert resp.status_code == 204

            # test with same valid data and valid rights again
            diff_name = _get_user_json()
            diff_name["name"] = "user135b18a6-b150-498a-810d-b09ab98e1bcc"
            resp = test_client.put(
                self.NEW_URL,
                data=json.dumps(diff_name),
                headers=_get_user_auth_headers(),
            )
            assert resp.status_code == 409

            # Invalid rights
            resp = test_client.put(
                self.NEW_URL,
                data=json.dumps(valid),
                headers=_get_user_auth_headers(api_key="invalid_api_key"),
            )
            assert resp.status_code == 403

            # Invalid user, valid rights
            resp = test_client.put(
                self.INVALID_URL,
                data=json.dumps(valid),
                headers=_get_user_auth_headers(),
            )
            assert resp.status_code == 404

    def test_delete(self, client):
        """
        Test the DELETE method for the UserItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            populate_db(db)

            # valid user, invalid rights
            resp = test_client.delete(
                self.URL, headers=_get_user_auth_headers(api_key="invalid_api_key")
            )
            assert resp.status_code == 403

            # valid user, valid rights
            resp = test_client.delete(self.URL, headers=_get_user_auth_headers())
            assert resp.status_code == 204

            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            resp = test_client.delete(self.INVALID_URL)
            assert resp.status_code == 404


@pytest.mark.usefixtures("client")
class TestLocationCollection(object):
    """
    This class contains tests for the LocationCollection resource.
    """

    URL = "/api/locations/"
    INVALID_URL = "/api/location1/"

    def test_get(self, client):
        """
        Test the GET method for the LocationCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == JSON_CONTENT
            data = json.loads(resp.data)

            check_namespace(test_client, data)
            check_control_post_method(
                test_client, "bikinghub:location-add", data, _get_location_json()
            )
            for item in data["items"]:
                check_control_get_method(test_client, "self", item)
                check_control_get_method(test_client, "profile", item)

            assert len(data) > 0

            # Test again if cache works, should not print "Cache miss location"
            resp = test_client.get(self.URL)
            assert resp.status_code == 200

            # Test again if cache works, should not print "Cache miss location"
            resp = test_client.get(self.URL)
            assert resp.status_code == 200

            # Assert 404 for invalid location
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_post(self, client):
        """
        Test the POST method for the LocationCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            valid_new = _get_location_json()

            # test with wrong content type
            resp = test_client.post(self.URL, data=json.dumps(valid_new))
            assert resp.status_code == 415

            # Assert 404 for invalid url
            resp = test_client.post(self.INVALID_URL, json=valid_new)
            assert resp.status_code == 404
            print(f"AAAAAAAAAAAAAAAAAA {resp.headers}")

            # test with valid and see that it exists afterward
            resp = test_client.post(self.URL, json=valid_new)
            print(f"Location created with ")
            assert resp.status_code == 201
            print(f"Location created at {resp.headers}")
            resp = test_client.get(resp.headers.get("location"))
            assert resp.status_code == 200

            # send same data again for 409
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 409

            # location already exists or too close
            valid_new["latitude"] = 65.55785484617326
            valid_new["longitude"] = 25.068934083629477
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 409

            # remove model field for 415
            valid_new.pop("latitude")
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 400

            # test with wrong method
            resp = test_client.put(self.URL, json=valid_new)
            assert resp.status_code == 405


@pytest.mark.usefixtures("client")
class TestLocationItem(object):
    """
    This class contains tests for the LocationItem resource.
    """

    URL = "/api/locations/1/"
    URL2 = "/api/locations/2/"
    INVALID_URL = "/api/locations/10/"

    def test_get(self, client):
        """
        Test the GET method for the LocationItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT
            data = json.loads(resp.data)
            assert len(data) > 0
            check_namespace(test_client, data)
            check_control_get_method(test_client, "self", data)
            check_control_get_method(test_client, "profile", data)
            check_control_get_method(test_client, "collection", data)
            check_control_get_method(test_client, "bikinghub:weather-all", data)

            check_control_put_method(
                test_client, "bikinghub:location-edit", data, _get_location_json()
            )

            resp = test_client.get(self.URL2)
            body = json.loads(resp.data)
            check_control_delete_method(test_client, "bikinghub:location-delete", body)

            # Assert 404 for invalid location
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_put(self, client):
        """
        Test the PUT method for the LocationItem resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            valid_new = _get_location_json()

            # test with wrong content type
            resp = test_client.put(self.URL, data=json.dumps(valid_new))
            assert resp.status_code == 415

            # Assert 404 for invalid url/id
            resp = test_client.put(self.INVALID_URL, json=valid_new)
            assert resp.status_code == 404

            # test with new lat and lon
            valid_new["name"] = "location1"
            resp = test_client.put(self.URL, json=valid_new)
            assert resp.status_code == 204

            # test with everything the new
            resp = test_client.put(self.URL, json=valid_new)
            assert resp.status_code == 204

            # remove field
            valid_new.pop("latitude")
            resp = test_client.put(self.URL, json=valid_new)
            assert resp.status_code == 400

            # test with wrong method
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 405

    def test_delete(self, client):
        """
        Test the DELETE method for the LocationItem resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

            # Assert 403 for non-admin user
            resp = test_client.delete(self.URL)
            assert resp.status_code == 403

            # Assert 204 for valid location
            resp = test_client.delete(self.URL, headers=_get_admin_auth_headers())
            assert resp.status_code == 204

            # Assert 404 for invalid location (already deleted)
            resp = test_client.get(self.URL, headers=_get_admin_auth_headers())
            assert resp.status_code == 404

            # Assert 404 for invalid location (never existed)
            resp = test_client.delete(
                self.INVALID_URL, headers=_get_admin_auth_headers()
            )
            assert resp.status_code == 404


@pytest.mark.usefixtures("client")
class TestWeatherCollection:
    """
    This class contains tests for the WeatherCollection resource.
    """

    URL = "/api/weather/"

    def test_get(self, client):
        """
        Test the GET method for the WeatherCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT
            data = json.loads(resp.data)
            check_namespace(test_client, data)
            for item in data["items"]:
                check_control_get_method(test_client, "self", item)
                check_control_get_method(test_client, "profile", item)
            assert len(data) > 0


@pytest.mark.usefixtures("client")
class TestWeatherItem:
    """
    This class contains tests for the WeatherItem resource.
    """

    URL = "/api/locations/1/weather/"
    INVALID_URL = "/api/locations/10/weather/"

    def test_get(self, client):
        """
        Test the GET method for the WeatherItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Error if no API key
            assert SECRETS.MML_API_KEY is not None and SECRETS.MML_API_KEY != ""

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT
            data = json.loads(resp.data)
            print(f"Data is {data}")

            check_namespace(test_client, data)
            check_control_get_method(test_client, "self", data)
            check_control_get_method(test_client, "profile", data)
            check_control_get_method(test_client, "collection", data)
            check_control_get_method(test_client, "location", data)

            assert len(data) > 0

            # Fetch the weather data for the location with no weather data
            resp = test_client.get("/api/locations/4/weather/")
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT
            data = json.loads(resp.data)
            print(data)

            # Assert 404 for invalid location
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404


@pytest.mark.usefixtures("client")
class TestFavouriteCollection:
    """
    This class contains tests for the FavouriteCollection resource.
    """

    URL = "/api/users/user37722c77-8004-41d7-993f-ef4f24356ce3/favourites/"
    INVALID_URL = "/api/users/user37722c77-8004-41d7-993f-ef4f24356ce3/non-favourites/"

    def test_get(self, client):
        """
        Test the GET method for the FavouriteCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            populate_db(db)

            # Assert 200 for populated database
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT

            data = json.loads(resp.data)

            check_namespace(test_client, data)
            check_control_post_method(
                test_client, "bikinghub:favourite-add", data, _get_favourite_json()
            )
            for item in data["items"]:
                check_control_get_method(test_client, "self", item)
                check_control_get_method(test_client, "profile", item)

            assert len(data) > 0

            # Assert 200 for testing the cache,
            # "Cache miss favourite" should print only once if working
            resp = test_client.get(self.URL)
            assert resp.status_code == 200

            # Assert 200 for testing the cache,
            # "Cache miss favourite" should print only once if working
            resp = test_client.get(self.URL)
            assert resp.status_code == 200

            # Assert 404 for invalid location
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_post(self, client):
        """
        Test the POST method for the FavouriteCollection resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            valid = _get_favourite_json()

            # test with wrong content type
            resp = test_client.post(self.URL, data=json.dumps(valid))
            assert resp.status_code == 415

            # Assert 404 for invalid url
            resp = test_client.post(self.INVALID_URL, json=valid)
            assert resp.status_code == 404

            # test with valid and see that it exists afterward
            resp = test_client.post(self.URL, json=valid)
            assert resp.status_code == 201
            resp = test_client.get(resp.headers.get("Location"))
            assert resp.status_code == 200

            # remove model field for 400
            valid.pop("title")
            resp = test_client.post(self.URL, json=valid)
            assert resp.status_code == 400

            # test with wrong method
            resp = test_client.put(self.URL, json=valid)
            assert resp.status_code == 405


@pytest.mark.usefixtures("client")
class TestFavouriteItem:
    """
    This class contains tests for the FavouriteItem resource.
    """

    URL = "/api/users/user37722c77-8004-41d7-993f-ef4f24356ce3/favourites/1/"
    URL2 = "/api/users/user135b18a6-b150-498a-810d-b09ab98e1bcc/favourites/2/"
    INVALID_URL = "/api/users/user37722c77-8004-41d7-993f-ef4f24356ce3/favourites/2/"
    URL_INVALID_USER = "/api/users/user10/favourites/1/"

    def test_get(self, client):
        """
        This function is a test function that takes a client as a parameter.

        :param client: The `test_get` method seems to be a test method in a testing framework.
        The `client` parameter is likely an object that represents a client or a connection to
        a server or service that the test will interact with. This client object is typically
        used to make requests to the server or service being
        """
        with client.app_context():
            test_client = client.test_client()

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == MASON_CONTENT
            data = json.loads(resp.data)
            print(f"Data is {data}")

            check_namespace(test_client, data)
            check_control_get_method(test_client, "self", data)
            check_control_get_method(test_client, "profile", data)
            check_control_get_method(test_client, "collection", data)
            check_control_put_method(
                test_client, "bikinghub:favourite-edit", data, _get_favourite_json()
            )

            assert len(data) > 0

            resp = test_client.get(self.URL2)
            body = json.loads(resp.data)
            check_control_delete_method(test_client, "bikinghub:favourite-delete", body)

            check_control_get_method(test_client, "bikinghub:locations-all", data)

            # Assert 404 for invalid location
            resp = test_client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_put(self, client):
        """
        Test the PUT method for the FavouriteItem resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            valid = _get_favourite_json()

            # test with wrong content type
            resp = test_client.put(self.URL, data=json.dumps(valid))
            assert resp.status_code == 415

            # Assert 404 for invalid url
            resp = test_client.put(self.INVALID_URL, json=valid)
            assert resp.status_code == 404

            # test with correct content
            resp = test_client.put(self.URL, json=valid)
            assert resp.status_code == 204

            # test with missing field
            valid.pop("title")
            resp = test_client.put(self.URL, json=valid)
            assert resp.status_code == 400

            # test with wrong method
            resp = test_client.post(self.URL, json=valid)
            assert resp.status_code == 405

    def test_delete(self, client):
        """
        Test the DELETE method for the FavouriteItem resource.
        """
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

            # Assert 403 for non-authenticated user
            resp = test_client.delete(self.URL)
            assert resp.status_code == 403

            # Assert 204 for valid location
            resp = test_client.delete(self.URL, headers=_get_user_auth_headers())
            assert resp.status_code == 204

            # Assert 404 for invalid location (already deleted)
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 404 for favourite not in user's favourites
            resp = test_client.delete(
                self.INVALID_URL, headers=_get_user_auth_headers()
            )
            assert resp.status_code == 404

            # Assert 404 for favourite not in nonexistent user's favourites
            resp = test_client.delete(
                self.URL_INVALID_USER, headers=_get_user_auth_headers()
            )
            assert resp.status_code == 404

            # Assert 404 for invalid location (never existed)
            resp = test_client.delete(
                self.INVALID_URL, headers=_get_user_auth_headers()
            )
            assert resp.status_code == 404


@pytest.mark.usefixtures("client")
class TestExtraURLs:

    PROFILE_URL = "/profiles/user1/"

    def test_get_profile(self, client):
        with client.app_context():
            test_client = client.test_client()

            # Assert 200 for valid request
            resp = test_client.get(self.PROFILE_URL)
            assert resp.status_code == 200

    def test_get_link_relations(self, client):
        with client.app_context():
            test_client = client.test_client()

            # Assert 200 for valid request
            resp = test_client.get(LINK_RELATIONS_URL)
            assert resp.status_code == 200

    def test_login(self, client):
        LOGIN_URL = "/api/login/"
        with client.app_context():
            populate_db(db)
            test_client = client.test_client()
            valid = {
                "name": "user37722c77-8004-41d7-993f-ef4f24356ce3",
                "password": "password1",
            }

            # Create a user
            resp = test_client.post("/api/users/", json=valid)

            # test with wrong content type
            resp = test_client.post(
                LOGIN_URL, data=json.dumps(valid), headers={"Content-Type": "image/gif"}
            )
            assert resp.status_code == 415

            # test with invalid password
            invalid = valid.copy()
            invalid["password"] = "wrong-password"
            resp = test_client.post(LOGIN_URL, json=invalid)
            assert resp.status_code == 401

            # test with correct content type and valid user params
            resp = test_client.post(LOGIN_URL, json=valid)
            assert resp.status_code == 200
