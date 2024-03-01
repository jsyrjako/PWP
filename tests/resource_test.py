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
from bikinghub.constants import MML_API_KEY


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
    content_type="application/json",
    api_key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4",
):
    # Creates valid admin headers for testing
    return {
        "Content-Type": f"{content_type}",
        "Bikinghub-Api-Key": f"{api_key}",
    }


def _get_user_auth_headers(
    content_type="application/json",
    api_key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4",
):
    # Creates valid user headers for testing
    return {
        "Content-Type": f"{content_type}",
        "Bikinghub-Api-Key": f"{api_key}",
    }


@pytest.mark.usefixtures("client")
class TestUserCollection:
    """
    This class contains tests for the UserCollection resource.
    """

    URL = "/api/user/"

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
            assert len(body["users"]) == 3
            for user in body["users"]:
                assert "id" in user
                assert "name" in user

    def test_post(self, client):
        """
        Test the POST method for the UserCollection resource.
        """
        with client.app_context():
            populate_db(db)
            test_client = client.test_client()

            # test with invalid rights
            valid = _get_user_json()
            resp = test_client.post(self.URL, data=json.dumps(valid))
            assert resp.status_code == 403

            # test with wrong content type and valid rights
            resp = test_client.post(
                self.URL,
                data=json.dumps(valid),
                headers=_get_admin_auth_headers(content_type="text/html"),
            )
            assert resp.status_code == 415

            # test with invalid content and valid rights
            invalid_user = _get_user_json().pop("name")
            resp = test_client.post(
                self.URL,
                data=json.dumps(invalid_user),
                headers=_get_admin_auth_headers(),
            )
            assert resp.status_code == 400

            # test with valid and see that it exists afterward
            resp = test_client.post(
                self.URL, data=json.dumps(valid), headers=_get_admin_auth_headers()
            )
            assert resp.status_code == 201

            # send same data again for 409
            resp = test_client.post(
                self.URL, data=json.dumps(valid), headers=_get_admin_auth_headers()
            )
            assert resp.status_code == 409


@pytest.mark.usefixtures("client")
class TestUserItem:
    """
    This class contains tests for the UserItem resource.
    """

    URL = "/api/user/user1/"
    NEW_URL = "/api/user/extra-user1/"
    INVALID_URL = "/api/user/user10/"

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
            assert body["id"]
            assert body["name"]

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
                self.URL, data=json.dumps(valid), headers=_get_user_auth_headers()
            )
            assert resp.status_code == 204

            # test with same valid data and valid rights again
            diff_name = _get_user_json()
            diff_name["name"] = "user2"
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
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
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

            # test with valid and see that it exists afterward
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 201
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

    URL = "/api/location/1/"
    INVALID_URL = "/api/location/10/"

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
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
            assert len(data) > 0

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
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
            assert len(data) > 0


@pytest.mark.usefixtures("client")
class TestWeatherItem:
    """
    This class contains tests for the WeatherItem resource.
    """

    URL = "/api/location/1/weather/"
    INVALID_URL = "/api/location/10/weather/"

    def test_get(self, client):
        """
        Test the GET method for the WeatherItem resource.
        """
        with client.app_context():
            test_client = client.test_client()

            # Error if no API key
            assert MML_API_KEY is not None

            # Assert 404 for empty database
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 200 for populated database
            populate_db(db)
            resp = test_client.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
            assert len(data) > 0

            # Fetch the weather data for the location with no weather data
            resp = test_client.get("/api/location/4/weather/")
            assert resp.status_code == 200
            assert resp.mimetype == "application/json"
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

    URL = "/api/user/user1/favourites/"
    INVALID_URL = "/api/user/user1/non-favourites/"

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
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
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

    URL = "/api/user/user1/favourite/1/"
    INVALID_URL = "/api/user/user1/favourite/2/"
    URL_INVALID_USER = "/api/user/user10/favourite/1/"

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
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
            assert len(data) > 0

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
