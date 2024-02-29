from flask import Flask

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from mongoengine import connect

from src.blueprints.apografi import apografi
from src.blueprints.psped import psped
from src.blueprints.stats import stats

from src.config import (
    MONGO_HOST,
    MONGO_PORT,
    MONGO_APOGRAFI_DB,
    MONGO_PSPED_DB,
    MONGO_USERNAME,
    MONGO_PASSWORD,
    MONGO_AUTHENTICATION_SOURCE,
)

app = Flask(__name__)

connect(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USERNAME,
    password=MONGO_PASSWORD,
    authentication_source=MONGO_AUTHENTICATION_SOURCE,
    db=MONGO_APOGRAFI_DB,
    alias=MONGO_APOGRAFI_DB,
)
connect(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USERNAME,
    password=MONGO_PASSWORD,
    authentication_source=MONGO_AUTHENTICATION_SOURCE,
    db=MONGO_PSPED_DB,
    alias=MONGO_PSPED_DB,
)


# CORS configuration
cors = CORS(
    app,
    resources={r"*": {"origins": ["http://localhost:4200", "https://ypes.ddns.net"]}},
)

# Register blueprints
app.register_blueprint(apografi, url_prefix="/apografi")
app.register_blueprint(stats, url_prefix="/apografi/stats")
app.register_blueprint(psped, url_prefix="/psped")


# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Υπουργείο Εσωτερικών"},
)
app.register_blueprint(swaggerui_blueprint)
