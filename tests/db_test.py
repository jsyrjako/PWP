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
        db.session.delete(favourite)
        db.session.commit()
        assert Favourite.query.filter_by(userId = user.id).first() is None

@pytest.mark.usefixtures("client")
def test_delete_location(client):
    with client.app_context():
        populate_db(db)
        location = Location.query.filter_by(name = "location1").first()
        db.session.delete(location)
        db.session.commit()
        assert Location.query.filter_by(name = "location1").first() is None
        assert Favourite.query.filter_by(locationId = location.id).first() is None
        assert WeatherData.query.filter_by(locationId = location.id).first() is None

@pytest.mark.usefixtures("client")
def test_delete_weatherData(client):
    with client.app_context():
        populate_db(db)
        weatherData = WeatherData.query.filter_by(locationId = 1).first()
        db.session.delete(weatherData)
        db.session.commit()
        assert WeatherData.query.filter_by(locationId = 1).first() is None

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

        # Attempt to create a location with non-numeric latitude
        location = Location.query.filter_by(name="location2").first()
        location.latitude = str(location.latitude) + "°"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

        # Attempt to create a location with non-numeric longitude
        location = Location.query.filter_by(name="location3").first()
        location.longitude = str(location.longitude) + "°"
        db.session.add(location)
        with pytest.raises(StatementError):
            db.session.commit()

def test_weatherData_columns(client):
    with client.app_context():
        populate_db(db)
        #Attempt to create weather data with non-numeric temperature
        weather_data = WeatherData.query.filter_by(id=1).first()
        weather_data.temperature = str(weather_data.temperature) + "°C"
        db.session.add(weather_data)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

        #Attempt to create weather data with non-numeric rain
        weather_data = WeatherData.query.filter_by(id=2).first()
        weather_data.rain = str(weather_data.rain) + "mm"
        db.session.add(weather_data)
        with pytest.raises(StatementError):
            db.session.commit()

        db.session.rollback()

        #Attempt to create weather data with non-numeric wind speed
        weather_data = WeatherData.query.filter_by(id=3).first()
        weather_data.windSpeed = str(weather_data.windSpeed) + "m/s"
        db.session.add(weather_data)
        with pytest.raises(StatementError):
            db.session.commit()
