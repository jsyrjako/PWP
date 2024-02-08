from app import db, bcrypt
import click
from flask.cli import with_appcontext


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    favourites = db.relationship(
        "Favourite", cascade="all, delete-orphan", back_populates="user"
    )
    comments = db.relationship(
        "Comment", cascade="all, delete-orphan", back_populates="user"
    )
    locations = db.relationship(
        "Location", cascade="all, delete-orphan", back_populates="user"
    )

    def __init__(self, name, password):
        self.name = name
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


class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
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


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(64), nullable=False)
    information = db.Column(db.String(256), nullable=False)
    time = db.Column(db.String(32), nullable=False)

    user = db.relationship("User", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "title": self.title,
            "information": self.information,
            "time": self.time,
        }

    def deserialize(self, doc):
        self.userId = doc["userId"]
        self.title = doc["title"]
        self.information = doc["information"]
        self.time = doc["time"]


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )

    user = db.relationship("User", back_populates="locations")
    favourites = db.relationship(
        "Favourite", back_populates="location", cascade="all, delete-orphan"
    )
    weatherData = db.relationship(
        "WeatherData", cascade="all, delete-orphan", back_populates="location"
    )
    trafficData = db.relationship(
        "TrafficData", cascade="all, delete-orphan", back_populates="location"
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


class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rain = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Integer, nullable=True)
    windSpeed = db.Column(db.Float, nullable=True)
    windDirection = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    temperatureFeel = db.Column(db.Integer)
    cloudCover = db.Column(db.String(32), nullable=True)
    weatherDescription = db.Column(db.String(32), nullable=False)
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


class TrafficData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
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

    # Create some locations

    location1 = Location(
        name="location1",
        latitude=65.05785284617326,
        longitude=25.468937083629477,
        userId=1,
    )
    location2 = Location(
        name="location2",
        latitude=65.0219057635643,
        longitude=25.482738222593955,
        userId=2,
    )
    location3 = Location(
        name="location3",
        latitude=65.01329038381004,
        longitude=25.458994792425564,
        userId=3,
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
    db
    db.session.add(favourite1)
    db.session.add(favourite2)
    db.session.add(favourite3)
    db.session.add(favourite4)
    db.session.commit()

    # Create some comments
    comment1 = Comment(
        userId=1, title="comment1", information="information1", time="time1"
    )
    comment2 = Comment(
        userId=2, title="comment2", information="information2", time="time2"
    )
    comment3 = Comment(
        userId=3, title="comment3", information="information3", time="time3"
    )
    db.session.add(comment1)
    db.session.add(comment2)
    db.session.add(comment3)
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

    # Create some traffic data
    trafficData1 = TrafficData(
        name="trafficData1",
        count=0,
        speed=0,
        flowLevel=0,
        latitude=0,
        longitude=0,
        locationId=1,
    )
    trafficData2 = TrafficData(
        name="trafficData2",
        count=0,
        speed=0,
        flowLevel=0,
        latitude=0,
        longitude=0,
        locationId=2,
    )
    trafficData3 = TrafficData(
        name="trafficData3",
        count=0,
        speed=0,
        flowLevel=0,
        latitude=0,
        longitude=0,
        locationId=3,
    )
    db.session.add(trafficData1)
    db.session.add(trafficData2)
    db.session.add(trafficData3)
    db.session.commit()


@click.command("delete-object")
@with_appcontext
def delete_object():
    object = User.query.first()
    db.session.delete(object)
    db.session.commit()
