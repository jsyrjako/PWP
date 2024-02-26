from bikinghub import db, bcrypt
import click
from flask.cli import with_appcontext
import secrets
import hashlib
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    favourites = db.relationship(
        "Favourite", cascade="all, delete-orphan", back_populates="user"
    )
    comments = db.relationship(
        "Comment", cascade="all, delete-orphan", back_populates="user"
    )
    api_key = db.relationship("AuthenticationKey", cascade="all, delete-orphan", back_populates="user")


    def __init__(self, name, password):
        self.name = name

        if not password:
            raise ValueError("Password cannot be empty")
        self.password = self.hash_password(password)

    def serialize(self):
        return {"id": self.id, "name": self.name}

    def deserialize(self, doc):
        self.name = doc["name"]
        self.password = self.hash_password(doc["password"])

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password, pw)

    def hash_password(self, pw):
        return bcrypt.generate_password_hash(pw).decode("utf-8")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "password"]
        }
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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    locationId = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=False)

    user = db.relationship("User", back_populates="favourites")
    location = db.relationship("Location", back_populates="favourites")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "userId": self.userId,
            "locationId": self.locationId,
        }

    def deserialize(self, doc):
        self.title = doc["title"]
        self.description = doc["description"]
        self.userId = doc["userId"]
        self.locationId = doc["locationId"]

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["title"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Favourite's title",
            "type": "string",
        }
        props["description"] = {
            "description": "Favourite's description",
            "type": "string",
        }
        props["locationId"] = {
            "description": "Favourite's locationId",
            "type": "integer",
        }
        return schema

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    locationId = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.Text, nullable=False)
    information = db.Column(db.Text, nullable=False)
    time = db.Column(db.Text, nullable=False)

    user = db.relationship("User", back_populates="comments")
    location = db.relationship("Location", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "locationId": self.locationId,
            "title": self.title,
            "information": self.information,
            "time": self.time,
        }

    def deserialize(self, doc):
        self.userId = doc["userId"]
        self.locationId = doc["locationId"]
        self.title = doc["title"]
        self.information = doc["information"]
        self.time = doc["time"]

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["title", "information"]
        }
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
    id = db.Column(db.Integer, primary_key=True)
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
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.latitude = doc["latitude"]
        self.longitude = doc["longitude"]

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Location's name",
            "type": "string",
        }
        return schema

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rain = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Integer, nullable=True)
    windSpeed = db.Column(db.Float, nullable=True)
    windDirection = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    temperatureFeel = db.Column(db.Integer, nullable=True)
    cloudCover = db.Column(db.Text, nullable=True)
    weatherDescription = db.Column(db.Text, nullable=True)
    weatherTime = db.Column(db.DateTime, nullable=True)
    locationId = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )

    location = db.relationship("Location", back_populates="weatherData")

    def serialize(self):
        return {
            "id": self.id,
            "rain": self.rain,
            "humidity": self.humidity,
            "windSpeed": self.windSpeed,
            "windDirection": self.windDirection,
            "temperature": self.temperature,
            "temperatureFeel": self.temperatureFeel,
            "cloudCover": self.cloudCover,
            "weatherDescription": self.weatherDescription,
            "locationId": self.locationId,
            "weatherTime": datetime.fromisoformat(self.weatherTime)
        }

    def deserialize(self, doc):
        self.rain = doc["rain"]
        self.humidity = doc["humidity"]
        self.windSpeed = doc["windSpeed"]
        self.windDirection = doc["windDirection"]
        self.temperature = doc["temperature"]
        self.temperatureFeel = doc["temperatureFeel"]
        self.cloudCover = doc["cloudCover"]
        self.weatherDescription = doc["weatherDescription"]
        self.locationId = doc["locationId"]
        self.weatherTime = datetime.fromisoformat(doc["weatherTime"])

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["temperature"]
        }
        props = schema["properties"] = {}
        props["rain"] = {
            "description": "WeatherData's rain",
            "type": "number",
        }
        props["humidity"] = {
            "description": "WeatherData's humidity",
            "type": "integer",
        }
        props["windSpeed"] = {
            "description": "WeatherData's windSpeed",
            "type": "number",
        }
        props["windDirection"] = {
            "description": "WeatherData's windDirection",
            "type": "integer",
        }
        props["temperature"] = {
            "description": "WeatherData's temperature",
            "type": "number",
        }
        props["temperatureFeel"] = {
            "description": "WeatherData's temperatureFeel",
            "type": "integer",
        }
        props["cloudCover"] = {
            "description": "WeatherData's cloudCover",
            "type": "string",
        }
        props["weatherDescription"] = {
            "description": "WeatherData's weatherDescription",
            "type": "string",
        }
        props["weatherTime"] = {
            "description": "WeatherData's weatherTime",
            "type": "string",
        }
        return schema

class TrafficData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    flowLevel = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    locationId = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="CASCADE"), nullable=False
    )

    location = db.relationship("Location", back_populates="trafficData")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "count": self.count,
            "speed": self.speed,
            "flowLevel": self.flowLevel,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "locationId": self.locationId,
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.count = doc["count"]
        self.speed = doc["speed"]
        self.flowLevel = doc["flowLevel"]
        self.latitude = doc["latitude"]
        self.longitude = doc["longitude"]
        self.locationId = doc["locationId"]


class AuthenticationKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False, unique=True)
    userId =  db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", back_populates="api_key", uselist=False)

    def __init__(self, key, userId, admin=False):
        self.key = self.key_hash(key)
        self.userId = userId
        self.admin = admin

    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()



# Create the database tables
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


# Populate the database with some dummy data
@click.command("populate-db")
@with_appcontext
def populate_db_command():
    # Create some users
    user1 = User(name="user1", password="password1")
    user2 = User(name="user2", password="password2")
    user3 = User(name="user3", password="password3")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

    # Create some api keys
    key1 = AuthenticationKey(userId=1, admin=True, key="ptKGKz3qINsn-pTIw7nBcsKCsKPlrsEsCkxj38lDpH4")
    key2 = AuthenticationKey(userId=2, admin=False, key="4N3hKWUlFGhBNUxps-jENUVNeqkbetMdr0Bi9qnCcm0")
    key3 = AuthenticationKey(userId=3, admin=False, key= "9M86GKl56ULe2dLBmzAyA3Il7pmn7P16Tjk7jtrPJZ0")
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

    # Create some comments
    # comment1 = Comment(
    #     userId=1, title="comment1", information="information1", time="time1", locationId=1
    # )
    # comment2 = Comment(
    #     userId=2, title="comment2", information="information2", time="time2", locationId=2
    # )
    # comment3 = Comment(
    #     userId=3, title="comment3", information="information3", time="time3", locationId=3
    # )
    # db.session.add(comment1)
    # db.session.add(comment2)
    # db.session.add(comment3)
    # db.session.commit()

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
        weatherTime=datetime.now()
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
        weatherTime=datetime.now()
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
        weatherTime=datetime.now()
    )
    db.session.add(weatherData1)
    db.session.add(weatherData2)
    db.session.add(weatherData3)
    db.session.commit()

    # Create some traffic data
    # trafficData1 = TrafficData(
    #     name="trafficData1",
    #     count=0,
    #     speed=0,
    #     flowLevel=0,
    #     latitude=0,
    #     longitude=0,
    #     locationId=1,
    # )
    # trafficData2 = TrafficData(
    #     name="trafficData2",
    #     count=0,
    #     speed=0,
    #     flowLevel=0,
    #     latitude=0,
    #     longitude=0,
    #     locationId=2,
    # )
    # trafficData3 = TrafficData(
    #     name="trafficData3",
    #     count=0,
    #     speed=0,
    #     flowLevel=0,
    #     latitude=0,
    #     longitude=0,
    #     locationId=3,
    # )
    # db.session.add(trafficData1)
    # db.session.add(trafficData2)
    # db.session.add(trafficData3)
    # db.session.commit()


@click.command("delete-object")
@with_appcontext
def delete_object():
    object = User.query.first()
    db.session.delete(object)
    db.session.commit()
