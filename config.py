import os

SECRET_KEY = "#d#JCqtTW\nilK\\7m\x0bp#\tj~#H"

GALA_APP_ID = 1208456960154745

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

