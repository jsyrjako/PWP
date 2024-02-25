import json
import os
import pytest
import time



@pytest.mark.usefixtures("client")
class TestLocationCollection(object):
    URL = "/api/locations/"

    def test_get(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.mimetype == "application/json"
        data = json.loads(resp.data)
        assert data.length > 0


    def test_post(self, client):
        pass

@pytest.mark.usefixtures("client")
class TestLocationItem(object):
    URL = "/api/locations/1/"

    def test_get(self, client):
        with client.app_context():
            app = client.test_client()
            resp = app.get(self.URL)
            assert resp.status_code == 200
            assert resp.mimetype == "application/json"
            data = json.loads(resp.data)
            assert data.length > 0

    def test_put(self):
        pass
    def test_delete(self):
        pass

class TestTrafficCollection:
    def test_get(self):
        pass

class TestTrafficItem:
    def test_get(self):
        pass

class TestTrafficLocation:
    def test_put(self):
        pass

class TestWeatherCollection:
    def test_get(self):
        pass
    def test_post(self):
        pass

class TestWeatherItem:
    def test_get(self):
        pass
    def test_put(self):
        pass
    def test_delete(self):
        pass

class TestFavouriteCollection:
    def test_get(self):
        pass
    def test_post(self):
        pass

