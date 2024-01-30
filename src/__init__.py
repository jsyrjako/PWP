from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_bcrypt import Bcrypt 
import os

from . import models

cache = Cache()
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        db.init_app(app)
        db.create_all()
        cache.init_app(app)
        bcrypt.init_app(app)

    app.cli.add_command(models.init_db_command)

    return app


