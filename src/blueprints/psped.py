import json
from flask import Blueprint, Response

from src.models.apografi import Organization

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
