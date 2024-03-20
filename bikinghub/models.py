"""
The models module contains the classes that represent the database tables.

The User class represents a user in the database.
The Favourite class represents a favourite location in the database.
The Comment class represents a comment in the database.
The Location class represents a location in the database.
The WeatherData class represents weather data in the database.
The TrafficData class represents traffic data in the database.
The AuthenticationKey class represents an authentication key in the database.
"""

import hashlib
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from flask.cli import with_appcontext
import click
from bikinghub import db, bcrypt


class User(db.Model):
    """
    Represents a user in the database.
    - id: The user's unique identifier
    - name: The user's name
    - password: The user's password
    - favourites: The user's favourite locations
    - comments: The user's comments
    - api_key: The user's api key
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    favourites = db.relationship(
        "Favourite", cascade="all, delete-orphan", back_populates="user"
    )
    comments = db.relationship(
        "Comment", cascade="all, delete-orphan", back_populates="user"
    )
    api_key = db.relationship(
        "AuthenticationKey", cascade="all, delete-orphan", back_populates="user"
    )

    def __init__(self, name, password):
        self.name = name

        if not password:
            raise ValueError("Password cannot be empty")
        self.password = self.hash_password(password)

    def serialize(self):
        """
        Serializes the User object to a dictionary.
        """
        return {"id": self.id, "name": self.name}

    def deserialize(self, doc):
        """
        Deserializes the User object from a dictionary.
        """
        self.name = doc["name"]
        self.password = self.hash_password(doc["password"])

    def check_password(self, pw):
        """
        Checks the password using bcrypt.
        """
        return bcrypt.check_password_hash(self.password, pw)

    def hash_password(self, pw):
        """
        Hashes the password using bcrypt.
        """
        return bcrypt.generate_password_hash(pw).decode("utf-8")

    @staticmethod
    def json_schema():
        """
        Returns the json schema for the User model.
        """

        schema = {"type": "object", "required": ["name", "password"]}
        props = schema["properties"] = {}
        props["name"] = {
            "description": "User's name",
            "type": "string",
        }
        props["password"] = {
            "description": "User's password",
            "type": "string",
        }
        return schema


class Favourite(db.Model):
    """
    Represents a favourite location in the database.
    - id: The favourite's unique identifier
    - title: The favourite's title
    - description: The favourite's description
    - user_id: The user's unique identifier
    - location_id: The location's unique identifier
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(
        db.Text, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=False)

    user = db.relationship("User", back_populates="favourites")
    location = db.relationship("Location", back_populates="favourites")

    def serialize(self):
        """
        Serializes the Favourite object to a dictionary.
        """

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "location_id": self.location_id,
        }

    def deserialize(self, doc):
        """
        Deserializes the Favourite object from a dictionary.
        """

        self.title = doc["title"]
        self.description = doc["description"]
        self.user_id = doc["user_id"]
        self.location_id = doc["location_id"]

    @staticmethod
    def json_schema():
        """
        Returns the json schema for the Favourite model.
        """

        schema = {"type": "object", "required": ["title"]}
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Favourite's title",
            "type": "string",
        }
        props["description"] = {
            "description": "Favourite's description",
            "type": "string",
        }
        props["location_id"] = {
            "description": "Favourite's location_id",
            "type": "integer",
        }
        return schema


class Comment(db.Model):
    """
    Represents a comment in the database.
    - id: The comment's unique identifier
    - title: The comment's title
    - information: The comment's information
    - time: The comment's time
    - user_id: The user's unique identifier
    - location_id: The location's unique identifier
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.Text, nullable=False)
    information = db.Column(db.Text, nullable=False)
    time = db.Column(db.Text, nullable=False)

    user = db.relationship("User", back_populates="comments")
    location = db.relationship("Location", back_populates="comments")

    def serialize(self):
        """
        Serializes the Comment object to a dictionary.
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "location_id": self.location_id,
            "title": self.title,
            "information": self.information,
            "time": self.time,
        }

    def deserialize(self, doc):
        """
        Deserializes the Comment object from a dictionary.
        """

        self.user_id = doc["user_id"]
        self.location_id = doc["location_id"]
        self.title = doc["title"]
        self.information = doc["information"]
        self.time = doc["time"]

    @staticmethod
    def json_schema():
        """
        Returns the json schema for the Comment model.
        """

        schema = {"type": "object", "required": ["title", "information"]}
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Comment's title",
            "type": "string",
        }
        props["information"] = {
            "description": "Comment's information",
            "type": "string",
        }
        return schema


class Location(db.Model):
    """
    Represents a location in the database.
    - id: The location's identifier
    - uuid: The location's uuid
    - name: The location's name
    - latitude: The location's latitude
    - longitude: The location's longitude
    """

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=str(uuid.uuid4))
    name = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    favourites = db.relationship(
        "Favourite", back_populates="location", cascade="all, delete-orphan"
    )
    weatherData = db.relationship(
        "WeatherData", cascade="all, delete-orphan", back_populates="location"
    )
    trafficData = db.relationship(
        "TrafficData", cascade="all, delete-orphan", back_populates="location"
    )
    comments = db.relationship(
        "Comment", cascade="all, delete-orphan", back_populates="location"
    )

    def serialize(self):
        """
        Serializes the Location object to a dictionary.
        """

        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def deserialize(self, doc):
        """
        Deserializes the Location object from a dictionary.
        """

        self.name = doc["name"]
        self.latitude = doc["latitude"]
        self.longitude = doc["longitude"]

    @staticmethod
    def json_schema():
        """
        Returns the json schema for the Location model.
        """

        schema = {"type": "object", "required": ["name", "latitude", "longitude"]}
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Location's name",
            "type": "string",
        }
        props["latitude"] = {
            "description": "Location's latitude",
            "type": "number",
        }
        props["longitude"] = {
            "description": "Location's longitude",
            "type": "number",
        }
        return schema


class WeatherData(db.Model):
    """
    Represents weather data in the database.
    - id: The weather data's unique identifier
    - rain: The weather data's rain
    - humidity: The weather data's humidity
    - wind_speed: The weather data's wind speed
    - wind_direction: The weather data's wind direction
    - temperature: The weather data's temperature
    - temperature_feel: The weather data's temperature feel
    - cloud_cover: The weather data's cloud cover
    - weather_description: The weather data's description
    - weather_time: The weather data's time
    - location_id: The location's unique identifier
    """

    id = db.Column(db.Integer, primary_key=True)
    rain = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Integer, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)
    wind_direction = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    temperature_feel = db.Column(db.Integer, nullable=True)
    cloud_cover = db.Column(db.Text, nullable=True)
    weather_description = db.Column(db.Text, nullable=True)
    weather_time = db.Column(db.DateTime, nullable=True)
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )

    location = db.relationship("Location", back_populates="weatherData")

    def serialize(self):
        """
        Serializes the WeatherData object to a dictionary.
        """

        return {
            "rain": self.rain,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "temperature": self.temperature,
            "temperature_feel": self.temperature_feel,
            "cloud_cover": self.cloud_cover,
            "weather_description": self.weather_description,
            "location_id": self.location_id,
            "weather_time": str(self.weather_time),
        }

    def deserialize(self, doc):
        """
        Deserializes the WeatherData object from a dictionary.
        """

        self.rain = doc["rain"]
        self.humidity = doc["humidity"]
        self.wind_speed = doc["wind_speed"]
        self.wind_direction = doc["wind_direction"]
        self.temperature = doc["temperature"]
        self.temperature_feel = doc["temperature_feel"]
        self.cloud_cover = doc["cloud_cover"]
        self.weather_description = doc["weather_description"]
        self.location_id = doc["location_id"]
        self.weather_time = datetime.fromisoformat(doc["weather_time"])

    @staticmethod
    def json_schema():
        """
        Returns the json schema for the WeatherData model.
        """

        schema = {"type": "object", "required": ["temperature"]}
        props = schema["properties"] = {}
        props["rain"] = {
            "description": "WeatherData's rain",
            "type": "number",
        }
        props["humidity"] = {
            "description": "WeatherData's humidity",
            "type": "integer",
        }
        props["wind_speed"] = {
            "description": "WeatherData's wind_speed",
            "type": "number",
        }
        props["wind_direction"] = {
            "description": "WeatherData's wind_direction",
            "type": "integer",
        }
        props["temperature"] = {
            "description": "WeatherData's temperature",
            "type": "number",
        }
        props["temperature_feel"] = {
            "description": "WeatherData's temperature_feel",
            "type": "integer",
        }
        props["cloud_cover"] = {
            "description": "WeatherData's cloud_cover",
            "type": "string",
        }
        props["weather_description"] = {
            "description": "WeatherData's weather_description",
            "type": "string",
        }
        props["weather_time"] = {
            "description": "WeatherData's weather_time",
            "type": "string",
            "format": "date-time",
        }
        return schema


class TrafficData(db.Model):
    """
    Represents traffic data in the database.
    - id: The traffic data's unique identifier
    - name: The traffic data's name
    - count: The traffic data's count
    - speed: The traffic data's speed
    - flow_level: The traffic data's flow level
    - latitude: The traffic data's latitude
    - longitude: The traffic data's longitude
    - location_id: The location's unique identifier
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    flow_level = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )

    location = db.relationship("Location", back_populates="trafficData")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "count": self.count,
            "speed": self.speed,
            "flow_level": self.flow_level,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_id": self.location_id,
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.count = doc["count"]
        self.speed = doc["speed"]
        self.flow_level = doc["flow_level"]
        self.latitude = doc["latitude"]
        self.longitude = doc["longitude"]
        self.location_id = doc["location_id"]


class AuthenticationKey(db.Model):
    """
    Represents an authentication key in the database.
    - id: The authentication key's unique identifier
    - key: The authentication key
    - user_id: The user's unique identifier
    - admin: Whether the key has admin privileges
    """

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(
        db.Text, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    admin = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", back_populates="api_key", uselist=False)

    def __init__(self, key, user_id, admin=False):
        self.key = self.key_hash(key)
        self.user_id = user_id
        self.admin = admin

    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Creates the database tables.
    """
    db.create_all()


# Populate the database with some dummy data
@click.command("populate-db")
@with_appcontext
def populate_db_command():
    """
    Populates the database with some dummy data.
    """
    # Create some users
    user1 = User(name="user1", password="password1")
    user2 = User(name="user2", password="password2")
    user3 = User(name="user3", password="password3")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    # Create some api keys
    key1 = AuthenticationKey(
        user_id=1, admin=True, key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4"
    )
    key2 = AuthenticationKey(
        user_id=2, admin=False, key="4N3hKWUlFGhBNUxps-jENUVNeqkbetMdr0Bi9qnCcm0"
    )
    key3 = AuthenticationKey(
        user_id=3, admin=False, key="9M86GKl56ULe2dLBmzAyA3Il7pmn7P16Tjk7jtrPJZ0"
    )
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
        title="favourite1", description="description1", user_id=1, location_id=1
    )
    favourite2 = Favourite(
        title="favourite2", description="description2", user_id=2, location_id=2
    )
    favourite3 = Favourite(
        title="favourite3", description="description3", user_id=3, location_id=3
    )
    favourite4 = Favourite(
        title="favourite3", description="description4", user_id=2, location_id=1
    )
    db.session.add(favourite1)
    db.session.add(favourite2)
    db.session.add(favourite3)
    db.session.add(favourite4)
    db.session.commit()

    # Create some comments
    # comment1 = Comment(
    #     user_id=1, title="comment1", information="information1", time="time1", location_id=1
    # )
    # comment2 = Comment(
    #     user_id=2, title="comment2", information="information2", time="time2", location_id=2
    # )
    # comment3 = Comment(
    #     user_id=3, title="comment3", information="information3", time="time3", location_id=3
    # )
    # db.session.add(comment1)
    # db.session.add(comment2)
    # db.session.add(comment3)
    # db.session.commit()

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
        location_id=1,
        weather_time=datetime.now(),
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
        location_id=2,
        weather_time=datetime.now(),
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
        location_id=3,
        weather_time=datetime.now(),
    )
    db.session.add(weather_data1)
    db.session.add(weather_data2)
    db.session.add(weather_data3)
    db.session.commit()

    # Create some traffic data
    # trafficData1 = TrafficData(
    #     name="trafficData1",
    #     count=0,
    #     speed=0,
    #     flow_level=0,
    #     latitude=0,
    #     longitude=0,
    #     location_id=1,
    # )
    # trafficData2 = TrafficData(
    #     name="trafficData2",
    #     count=0,
    #     speed=0,
    #     flow_level=0,
    #     latitude=0,
    #     longitude=0,
    #     location_id=2,
    # )
    # trafficData3 = TrafficData(
    #     name="trafficData3",
    #     count=0,
    #     speed=0,
    #     flow_level=0,
    #     latitude=0,
    #     longitude=0,
    #     location_id=3,
    # )
    # db.session.add(trafficData1)
    # db.session.add(trafficData2)
    # db.session.add(trafficData3)
    # db.session.commit()


@click.command("delete-thing")
@with_appcontext
def delete_object():
    thing = User.query.first()
    db.session.delete(thing)
    db.session.commit()
