from flask import Flask

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from mongoengine import connect

from src.blueprints.apografi import apografi
from src.blueprints.psped import psped
from src.blueprints.stats import stats
from src.blueprints.armodiotites import remit
from src.blueprints.diataxeis import diataxeis
from src.blueprints.nomikes_praxeis import nomikes_praxeis

app = Flask(__name__)

connect(db="apografi", alias="apografi")
connect(db="psped", alias="psped")

# CORS configuration
cors = CORS(
    app,
    resources={
        r"*": {
            "origins": ["http://localhost:4200", "https://ypes.ddns.net"]
        }
    },
)

# Register blueprints
app.register_blueprint(apografi, url_prefix="/apografi")
app.register_blueprint(stats, url_prefix="/apografi/stats")
app.register_blueprint(psped, url_prefix="/psped")
app.register_blueprint(remit, url_prefix="/remit")

app.register_blueprint(diataxeis, url_prefix="/diataxeis")
app.register_blueprint(nomikes_praxeis, url_prefix="/nomikes_praxeis")

# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Υπουργείο Εσωτερικών"},
)
app.register_blueprint(swaggerui_blueprint)
