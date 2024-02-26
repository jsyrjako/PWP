import pytest
import os
import tempfile
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
from bikinghub import create_app, db
from bikinghub.models import User, Favourite, Location, WeatherData, AuthenticationKey, Comment
from conftest import populate_db

#@event.listens_for(Engine, "connect")
#def set_sqlite_pragma(dbapi_connection, connection_record):
#    cursor = dbapi_connection.cursor()
#    cursor.execute("PRAGMA foreign_keys=ON")
#    cursor.close()

# based on http://flask.pocoo.org/en/3.0.x/testing/

@pytest.mark.usefixtures("client")
def test_create_instances(client):
    # Check that everything exists
    with client.app_context():
        populate_db(db)
        assert 3 == User.query.count()
        assert AuthenticationKey.query.count() == 3
        assert Location.query.count() == 3
        assert Favourite.query.count() == 4
        assert WeatherData.query.count() == 3
        db_user = User.query.first()
        db_auth_key = AuthenticationKey.query.first()
        db_location = Location.query.first()
        db_favourite = Favourite.query.first()
        db_weather_data = WeatherData.query.first()

        # Check relationships
        assert db_user.api_key[0] == db_auth_key
        assert db_favourite.user == db_user
        assert db_favourite.location == db_location
        assert db_weather_data.location == db_location
        assert db_weather_data in db_location.weatherData

@pytest.mark.usefixtures("client")
def test_delete_user(client):
    with client.app_context():
        populate_db(db)
        user = User.query.filter_by(name = "user1").first()
        assert user is not None
        db.session.delete(user)
        db.session.commit()
        assert User.query.filter_by(name = "user1").first() is None
        assert Favourite.query.filter_by(userId=user.id).first() is None
        assert AuthenticationKey.query.filter_by(userId=user.id).first() is None

@pytest.mark.usefixtures("client")
def test_delete_favourite(client):
    with client.app_context():
        populate_db(db)
        user  = User.query.filter_by(name = "user1").first()
        favourite = Favourite.query.filter_by(userId = user.id).first()


@pytest.mark.usefixtures("client")
def test_location_weatherData_one_to_one(client):
    with client.app_context():
        populate_db(db)
        location = Location.query.filter_by(name="location1").first()
        weatherData_1 = WeatherData.query.filter_by(id=1).first()
        weatherData_2 = WeatherData.query.filter_by(id=2).first()
        weatherData_1.location = location
        weatherData_2.location = location
        db.session.add(location)
        db.session.add(weatherData_1)
        db.session.add(weatherData_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_user_columns(client):
    with client.app_context():
        populate_db(db)
        # Attempt to create a user with a non-unique name
        user = User(name="user1", password="password")
        db.session.add(user)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Attempt to create a user with a None password
        with pytest.raises(ValueError):
            user = User(name="user4", password=None)

def test_authentication_key_columns(client):
    with client.app_context():
        populate_db(db)
        # Attempt to create an authentication key with a non-existing user ID
        key = AuthenticationKey(userId=4, admin=True)
        db.session.add(key)
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_location_columns(client):
    with client.app_context():
        populate_db(db)
        # Attempt to create a location with a None name
        location = Location.query.filter_by(name="location1").first()
        location.name = None
        db.session.add(location)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Attempt to create a location with non-numeric latitude and longitude
        location = Location.query.filter_by(name="location2").first()
        location.latitude = "abc"
        location.longitude = "def"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()
