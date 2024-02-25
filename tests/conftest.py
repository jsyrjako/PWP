import pytest
import os
import tempfile
from bikinghub import create_app, db
from bikinghub.models import User, Favourite, Location, WeatherData, AuthenticationKey

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_fname}"}
    app = create_app(config)

    with app.app_context():
        db.create_all()
        populate_db(db)

    yield app

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def populate_db(db):
    # Create some users
    user1 = User(name="user1", password="password1")
    user2 = User(name="user2", password="password2")
    user3 = User(name="user3", password="password3")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    # Create some api keys
    key1 = AuthenticationKey(userId=1, admin=True)
    key2 = AuthenticationKey(userId=2, admin=False)
    key3 = AuthenticationKey(userId=3, admin=False)
    db.session.add(key1)
    db.session.add(key2)
    db.session.add(key3)
    db.session.commit()

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
    db.session.add(location1)
    db.session.add(location2)
    db.session.add(location3)
    db.session.commit()

    # Create some favourites
    favourite1 = Favourite(
        title="favourite1", description="description1", userId=1, locationId=1
    )
    favourite2 = Favourite(
        title="favourite2", description="description2", userId=2, locationId=2
    )
    favourite3 = Favourite(
        title="favourite3", description="description3", userId=3, locationId=3
    )
    favourite4 = Favourite(
        title="favourite3", description="description4", userId=2, locationId=1
    )
    db.session.add(favourite1)
    db.session.add(favourite2)
    db.session.add(favourite3)
    db.session.add(favourite4)
    db.session.commit()

    # Create some weather data
    weatherData1 = WeatherData(
        rain=0,
        humidity=0,
        windSpeed=0,
        windDirection=0,
        temperature=0,
        temperatureFeel=0,
        cloudCover="cloudCover1",
        weatherDescription="weatherDescription1",
        locationId=1,
    )
    weatherData2 = WeatherData(
        rain=0,
        humidity=0,
        windSpeed=0,
        windDirection=0,
        temperature=0,
        temperatureFeel=0,
        cloudCover="cloudCover2",
        weatherDescription="weatherDescription2",
        locationId=2,
    )
    weatherData3 = WeatherData(
        rain=0,
        humidity=0,
        windSpeed=0,
        windDirection=0,
        temperature=0,
        temperatureFeel=0,
        cloudCover="cloudCover3",
        weatherDescription="weatherDescription3",
        locationId=3,
    )
    db.session.add(weatherData1)
    db.session.add(weatherData2)
    db.session.add(weatherData3)
    db.session.commit()
