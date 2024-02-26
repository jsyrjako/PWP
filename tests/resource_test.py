import json
import os
import pytest
import time
from conftest import populate_db
from sqlalchemy.engine import Engine
from sqlalchemy import event
from bikinghub import db
from bikinghub.models import AuthenticationKey


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def _get_user_json(number=1):
    # Creates a valid user JSON object for testing
    return {"name": "extra-user{}".format(number), "password": "extra-password{}".format}

def _get_location_json(number=1):
    # Creates a valid location JSON object for testing
    return {"name": "extra-location{}".format(number), "latitude": 65.55785284617326, "longitude": 25.068937083629477}


@pytest.mark.usefixtures("client")
class TestUserCollection:
    URL = "/api/user/"       

    def test_get(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            admin_token = AuthenticationKey.query.filter_by(admin=True).first()
            admin_headers = {"Content-Type": "application/json", "Bikinghub-Api-Key": admin_token.key}
            resp = test_client.get(self.URL, headers=admin_headers)
            print(f"RESPONSE: {type(resp)}")
            assert resp.status_code == 200
            body = json.loads(resp.data)
            assert len(body["users"]) == 3
            for user in body["users"]:
                assert "name" in user
                assert "password" in user

    def test_post(self, client):
        # test with wrong content type
        with client.app_context():
            valid = _get_user_json()
            resp = client.post(self.URL, data=json.dumps(valid))
            assert resp.status_code == 415

@pytest.mark.usefixtures("client") 
class TestUserItem:
    URL = "/api/user/user1/"
    INVALID_URL = "/api/user/user10/"

    def test_get(self, client):
        with client.app_context():
            populate_db(db)
            resp = client.get(self.URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            assert body["name"] == "user1"
            assert body["password"] == "password1"
            resp = client.get(self.INVALID_URL)
            assert resp.status_code == 404

    def test_put(self, client):
        with client.app_context():
            populate_db(db)
            valid = _get_user_json()

            # Wrong content type
            resp = client.put(self.URL, data=json.dumps(valid), headers={"Content-Type": "text/html"})
            assert resp.status_code == 415
            
            resp = client.put(self.INVALID_URL, json=valid)
            assert resp.status_code == 404

    def test_delete(self, client):
        with client.app_context():
            populate_db(db)
            resp = client.delete(self.URL)
            assert resp.status_code == 204
            resp = client.get(self.URL)
            assert resp.status_code == 404
            resp = client.delete(self.INVALID_URL)
            assert resp.status_code == 404

@pytest.mark.usefixtures("client")
class TestLocationCollection(object):
    URL = "/api/locations/"
    INVALID_URL = "/api/location1/"

    def test_get(self, client):
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

    def test_post(self, client):
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
            assert resp.status_code == 415
            
            # test with wrong method
            resp = test_client.put(self.URL, json=valid_new)
            assert resp.status_code == 405

@pytest.mark.usefixtures("client")
class TestLocationItem(object):
    URL = "/api/location/1/"
    INVALID_URL = "/api/location/10/"

    def test_get(self, client):
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
            assert resp.status_code == 415

            # test with wrong method
            resp = test_client.post(self.URL, json=valid_new)
            assert resp.status_code == 405

    def test_delete(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

            # Get admin token
            admin_headers = {"Content-Type": "application/json", "Bikinghub-Api-Key": "ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4"}

            # Assert 403 for non-admin user
            resp = test_client.delete(self.URL)
            assert resp.status_code == 403
    
            # Assert 204 for valid location
            resp = test_client.delete(self.URL, headers=admin_headers)
            assert resp.status_code == 204

            # Assert 404 for invalid location (already deleted)
            resp = test_client.get(self.URL)
            assert resp.status_code == 404

            # Assert 404 for invalid location (never existed)
            resp = test_client.delete(self.INVALID_URL, headers=admin_headers)
            assert resp.status_code == 404


@pytest.mark.usefixtures("client")
class TestWeatherCollection:
    URL = "/api/location/1/weather/"
    INVALID_URL = "/api/location/1/non-weather/"

    def test_get(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

@pytest.mark.usefixtures("client")
class TestWeatherItem:
    URL = "/api/location/1/weather/1/"
    INVALID_URL = "/api/location/1/weather/10"

    def test_get(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)

@pytest.mark.usefixtures("client")
class TestFavouriteCollection:
    URL = "/api/user/user1/favourites/"

    def test_get(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)


    def test_post(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)


@pytest.mark.usefixtures("client")
class TestFavouriteItem:
    URL = "/api/user/user1/favourites/1/"
    INVALID_URL = "/api/user/user1/favourites/10/"

    def test_get(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)


    def test_put(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            
    def test_delete(self, client):
        with client.app_context():
            test_client = client.test_client()
            populate_db(db)
            resp = client.delete(self.URL)
            assert resp.status_code == 204
            resp = client.get(self.URL)
            assert resp.status_code == 404
            resp = client.delete(self.INVALID_URL)
            assert resp.status_code == 404