import json
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from deepdiff import DeepDiff

from src.models.psped.foreas import Foreas
from src.models.psped.change import Change
from src.blueprints.decorators import can_edit

psped = Blueprint("psped", __name__)


@psped.route("/foreas/<string:code>")
def get_foreas(code: str):
    try:
        foreas = Foreas.objects.only("code", "level").exclude("id").get(code=code)
        return Response(
            # json.dumps(foreas.to_json()),
            foreas.to_json(),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/foreas/<string:code>", methods=["PUT"])
@jwt_required()
@can_edit
def update_poliepipedi(code: str):
    current_user = get_jwt_identity()

    try:
        data = request.get_json()

        foreas = Foreas.objects.get(code=data["code"])

        foreas_dict = foreas.to_mongo().to_dict()
        del foreas_dict["level"]
        del foreas_dict["code"]
        id = foreas_dict.pop("_id")

        foreas_updated = Foreas(**foreas_dict, **data)
        foreas_updated = foreas_updated.to_mongo().to_dict()
        foreas_updated["_id"] = id

        diff = DeepDiff(foreas.to_mongo().to_dict(), foreas_updated)

        if diff:
            change = Change(action="update", who=current_user, change=diff)
            foreas.update(**data, changes=foreas.changes + [change])
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
