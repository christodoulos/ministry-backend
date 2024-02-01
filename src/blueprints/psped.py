from flask import Blueprint, Response

from src.models.apografi import Organization

psped = Blueprint("psped", __name__)


@psped.route("/foreas/<string:code>", methods=["GET"])
def get_foreas(code: str):
    organization = Organization.objects(code=code).first().to_json_enchanced()
    return Response(organization, mimetype="application/json", status=200)
