import json
from flask import Blueprint, Response

from src.models.apografi.organization import Organization
from src.models.psped import Foreas

psped = Blueprint("psped", __name__)


@psped.route("/foreas/<string:code>", methods=["GET"])
def get_foreas(code: str):
    try:
        organization = Organization.objects.get(code=code)
        return Response(
            organization.to_json_enchanced(),
            mimetype="application/json",
            status=200,
        )
    except Organization.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/foreas/<string:code>/enchanched", methods=["GET"])
def get_foreas_enchanced(code: str):
    try:
        foreas = Foreas.objects.get(code=code)
        return Response(
            foreas.to_json_enchanced(),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )
