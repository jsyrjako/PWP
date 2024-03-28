"""
This file is the entry point for the application. It creates the Flask app and
initializes the database and cache. It also registers the API blueprint and
custom URL converters.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from flasgger import Swagger

cache = Cache()
db = SQLAlchemy()
bcrypt = Bcrypt()
api_keys = {}


def create_app(test_config=None):
    """
    Create and configure the app. If a test_config is provided, it will be used
    instead of the instance config. The config should contain
    the following configuration:
    - SECRET
    - SQLALCHEMY_DATABASE_URI
    - SQLALCHEMY_TRACK_MODIFICATIONS
    - CACHE_TYPE
    - CACHE_DIR
    """

    from . import models
    from . import api
    from .constants import LINK_RELATIONS_URL

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

    # merge swagger docs
    doc_dir = "./bikinghub/docs/"
    app.config["SWAGGER"] = {
        "title": "Sensorhub API",
        "openapi": "3.0.3",
        "doc_dir": doc_dir,
    }
    swagger = Swagger(
        app,
        template_file=os.path.join(os.getcwd(), "bikinghub", "docs", "bikinghub.yml"),
        parse=False,
    )

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

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "link relations"

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return f"you requested {profile} profile"


    

    # @app.route("/admin/")
    # def admin_site():
    #     return app.send_static_file("html/admin.html")

    return app
