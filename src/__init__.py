from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = [
    {
        "db": "attica_dt",
        "host": environ.get("MONGODB_HOST"),
        "port": int(environ.get("MONGODB_PORT")),
        "alias": "attica_dt",
    },
    {
        "db": "attica_green",
        "host": environ.get("MONGODB_HOST"),
        "port": int(environ.get("MONGODB_PORT")),
        "alias": "attica_green",
    },
    {
        "db": "impetus-dev",
        "host": environ.get("MONGODB_HOST"),
        "port": int(environ.get("MONGODB_PORT")),
        "alias": "impetus-dev",
    },
]

cors = CORS(
    app,
    resources={r"*": {"origins": ["http://localhost:4200", "https://ypes.ddns.net"]}},
)

db = MongoEngine()
db.init_app(app)


SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Υπουργείο Εσωτερικών"},
)

app.register_blueprint(swaggerui_blueprint)
