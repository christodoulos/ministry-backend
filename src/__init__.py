from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from os import environ, path
from dotenv import load_dotenv
import redis

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

app = Flask(__name__)

# MongoEngine configuration
app.config["MONGODB_SETTINGS"] = [
    {
        "db": "apografi",
        "host": environ.get("MONGODB_HOST"),
        "port": int(environ.get("MONGODB_PORT")),
        "alias": "apografi",
    },
    {
        "db": "ypes",
        "host": environ.get("MONGODB_HOST"),
        "port": int(environ.get("MONGODB_PORT")),
        "alias": "ypes",
    },
]
db = MongoEngine()
db.init_app(app)

# Redis configuration
r = redis.Redis(
    host=environ.get("REDIS_HOST"), port=int(environ.get("REDIS_PORT")), db=0
)

# CORS configuration
cors = CORS(
    app,
    resources={r"*": {"origins": ["http://localhost:4200", "https://ypes.ddns.net"]}},
)


# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Υπουργείο Εσωτερικών"},
)
app.register_blueprint(swaggerui_blueprint)

# Import blueprints
from src.blueprints.apografi import apografi  # noqa: E402

# Register blueprints
app.register_blueprint(apografi, url_prefix="/apografi")


# Cache dictionaries
from src.apografi.lib import cache_dictionaries  # noqa: E402

cache_dictionaries()
