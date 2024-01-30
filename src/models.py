from src import db, bcrypt
import click
from flask.cli import with_appcontext

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    favourites = db.relationship("Favourite", back_populates="user")
    comments = db.relationship("Comment", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
    
    def deserialize(self, doc):
        self.name = doc["name"]
        self.password = self.hash_password(doc["password"])

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.password, pw)

    def hash_password(self, pw):
        return bcrypt.generate_password_hash(pw).decode('utf-8')

class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    locationId = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

    user = db.relationship("User", back_populates="favourites")
    location = db.relationship("Location", back_populates="favourites")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "userId": self.userId,
            "locationId": self.locationId
        }

    def deserialize(self, doc):
        self.title = doc["title"]
        self.description = doc["description"]
        self.userId = doc["userId"]
        self.locationId = doc["locationId"]

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
            "time": self.time
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

    favourites = db.relationship("Favourite", back_populates="location")
    weatherData = db.relationship("WeatherData", back_populates="location")
    trafficData = db.relationship("TrafficData", back_populates="location")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    def deserialize(self, doc):
        self.name = doce["name"]
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
    locationId = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

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
            "locationId": self.locationId
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
    locationId = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

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
            "locationId": self.locationId
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
    

