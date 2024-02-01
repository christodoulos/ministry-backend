from flask import Flask

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from mongoengine import connect

from src.blueprints.apografi import apografi
from src.blueprints.psped import psped

app = Flask(__name__)

connect(db="apografi", alias="apografi")
connect(db="psped", alias="psped")


# CORS configuration
cors = CORS(
    app,
    resources={r"*": {"origins": ["http://localhost:4200", "https://ypes.ddns.net"]}},
)

# Register blueprints
app.register_blueprint(apografi, url_prefix="/apografi")
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
