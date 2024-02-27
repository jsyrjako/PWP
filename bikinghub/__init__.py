import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_bcrypt import Bcrypt

cache = Cache()
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(test_config=None):
    from . import models
    from . import api

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.init_app(app)
        db.create_all()
        cache.init_app(app)
        bcrypt.init_app(app)

    from bikinghub.converters import (
        UserConverter,
        FavouriteConverter,
        LocationConverter,
    )

    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.populate_db_command)
    app.cli.add_command(models.delete_object)

    app.url_map.converters["user"] = UserConverter
    app.url_map.converters["favourite"] = FavouriteConverter
    # app.url_map.converters["traffic"] = TrafficConverter
    # app.url_map.converters["weather"] = WeatherConverter
    app.url_map.converters["location"] = LocationConverter

    app.register_blueprint(api.api_bp)

    return app
