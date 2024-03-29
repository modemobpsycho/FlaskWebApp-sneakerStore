from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_mail import *
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from website.config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    mail = Mail(app)
    app.config["MAIL_SERVER"] = Config.MAIL_SERVER
    app.config["MAIL_PORT"] = Config.MAIL_PORT
    app.config["MAIL_USERNAME"] = Config.MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = Config.MAIL_PASSWORD
    app.config["MAIL_USE_TLS"] = Config.MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = Config.MAIL_USE_SSL
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Config.DB_NAME}"

    db.init_app(app)
    migrate = Migrate(app, db)

    app.config["SESSION_TYPE"] = "sqlalchemy"
    app.config["SESSION_SQLALCHEMY"] = db
    app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"
    app.config["SESSION_SQLALCHEMY_MODEL"] = "website.models.CustomSessionModel"

    Session(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


from website.models import CustomSessionModel


def create_database(app):
    if not path.exists("website/" + Config.DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
