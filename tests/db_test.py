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

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()


    yield app

    os.close(db_fd)
    os.unlink(db_fname)

# based on http://flask.pocoo.org/en/3.0.x/testing/

@pytest.mark.usefixtures("app")
def test_create_instances(app):
    # Check that everything exists
    with app.app_context():
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
        user = User.query.filter_by(name = "user1").first()
        db.session.delete(user)
        db.session.commit()
        assert User.query.filter_by(name="user1").first() is None
        assert Favourite.query.filter_by(userId=user.id).count() == 0
        assert AuthenticationKey.query.filter_by(userId=user.id).count() == 0
