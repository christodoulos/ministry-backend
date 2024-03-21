import json
from flask import Blueprint, Response


from src.models.psped import Foreas

psped = Blueprint("psped", __name__)


@psped.route("/foreas/<string:code>")
def get_foreas(code: str):
    try:
        foreas = Foreas.objects(code=code).only("code", "level").exclude("id")
        return Response(
            json.dumps(foreas.to_json()),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/foreas/<string:code>/tree")
def get_foreas_tree(code: str):
    try:
        foreas = Foreas.objects.get(code=code)
        return Response(
            json.dumps(foreas.tree_to_json()),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )
