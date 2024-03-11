from flask import Flask

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from mongoengine import connect

from src.blueprints.apografi import apografi
from src.blueprints.psped import psped
from src.blueprints.stats import stats
from src.blueprints.armodiotites import remit
from src.blueprints.legal_provisions import legal_provisions
from src.blueprints.legal_acts import legal_acts

app = Flask(__name__)

connect(db="apografi",
        alias="apografi",
        host='mongodb://localhost:27017/apografi')
connect(db="psped", alias="psped", host='mongodb://localhost:27017/psped')

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

app.register_blueprint(legal_provisions, url_prefix="/legal_provisions")
app.register_blueprint(legal_acts, url_prefix="/legal_acts")
# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Υπουργείο Εσωτερικών"},
)
app.register_blueprint(swaggerui_blueprint)
