import os
import tempfile
from datetime import datetime
import pytest
import uuid
from bikinghub.models import User, Favourite, Location, WeatherData, AuthenticationKey
from bikinghub import create_app, db


@pytest.fixture
def client():
    """
    Create a test client for the application
    """
    db_fd, db_fname = tempfile.mkstemp()
    config = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_fname}"}
    app = create_app(config)

    with app.app_context():
        db.create_all()
        # populate_db(db)

    yield app

    # db.session.remove()
    os.close(db_fd)

    # Comment this line when running tests in Windows
    # os.unlink(db_fname)


def populate_db(database):
    """
    Populate the database with some test data
    """
    # Create some users
    uuid1 = uuid.uuid4()
    user1 = User(name="user" + str(uuid1), password="password1")
    
    uuid2 = uuid.uuid4()
    user2 = User(name="user" + str(uuid2), password="password2")
    
    uuid3 = uuid.uuid4()
    user3 = User(name="user" + str(uuid3), password="password3")

    database.session.add(user1)
    database.session.add(user2)
    database.session.add(user3)
    database.session.commit()

    # Create some api keys
    key1 = AuthenticationKey(
        user_id=uuid1, admin=True, key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4"
    )
    key2 = AuthenticationKey(
        user_id=uuid2, admin=False, key="4N3hKWUlFGhBNUxps-jENUVNeqkbetMdr0Bi9qnCcm0"
    )
    key3 = AuthenticationKey(
        user_id=uuid3, admin=False, key="9M86GKl56ULe2dLBmzAyA3Il7pmn7P16Tjk7jtrPJZ0"
    )
    database.session.add(key1)
    database.session.add(key2)
    database.session.add(key3)
    database.session.commit()

    # Create some locations

    location1 = Location(
        name="location1",
        latitude=65.05785284617326,
        longitude=25.468937083629477,
    )
    location2 = Location(
        name="location2",
        latitude=65.0219057635643,
        longitude=25.482738222593955,
    )
    location3 = Location(
        name="location3",
        latitude=65.01329038381004,
        longitude=25.458994792425564,
    )
    location4 = Location(
        name="location4",
        latitude=65.01326969,
        longitude=25.45420420,
    )
    database.session.add(location1)
    database.session.add(location2)
    database.session.add(location3)
    database.session.add(location4)
    database.session.commit()

    # Create some favourites
    favourite1 = Favourite(
        title="favourite1", description="description1", user_id=uuid1, location_id=1
    )
    favourite2 = Favourite(
        title="favourite2", description="description2", user_id=uuid2, location_id=2
    )
    favourite3 = Favourite(
        title="favourite3", description="description3", user_id=uuid3, location_id=3
    )
    favourite4 = Favourite(
        title="favourite3", description="description4", user_id=uuid2, location_id=1
    )
    database.session.add(favourite1)
    database.session.add(favourite2)
    database.session.add(favourite3)
    database.session.add(favourite4)
    database.session.commit()

    # Create some weather data
    weather_data1 = WeatherData(
        rain=0,
        humidity=0,
        wind_speed=0,
        wind_direction=0,
        temperature=0,
        temperature_feel=0,
        cloud_cover="cloud_cover1",
        weather_description="weather_description1",
        weather_time=datetime.now(),
        location_id=1,
    )
    weather_data2 = WeatherData(
        rain=0,
        humidity=0,
        wind_speed=0,
        wind_direction=0,
        temperature=0,
        temperature_feel=0,
        cloud_cover="cloud_cover2",
        weather_description="weather_description2",
        weather_time=datetime.now(),
        location_id=2,
    )
    weather_data3 = WeatherData(
        rain=0,
        humidity=0,
        wind_speed=0,
        wind_direction=0,
        temperature=0,
        temperature_feel=0,
        cloud_cover="cloud_cover3",
        weather_description="weather_description3",
        weather_time=datetime.now(),
        location_id=3,
    )
    database.session.add(weather_data1)
    database.session.add(weather_data2)
    database.session.add(weather_data3)
    database.session.commit()
