import json
from bson import ObjectId
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from deepdiff import DeepDiff

from src.models.psped.foreas import Foreas
from src.models.psped.change import Change
from src.models.psped.legal_provision import LegalProvision
from src.blueprints.decorators import can_edit

psped = Blueprint("psped", __name__)


@psped.route("/foreas/count")
def get_foreas_count():
    count = Foreas.objects.count()
    return Response(
        json.dumps({"count": count}),
        mimetype="application/json",
        status=200,
    )


@psped.route("/foreas/<string:code>")
def get_foreas(code: str):
    try:
        foreas = Foreas.objects.get(code=code)
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
def update_foreas(code: str):
    who = get_jwt_identity()
    what = {"entity": "organization", "key": {"code": code}}

    try:
        data = request.get_json()

        level = data["level"]
        legalProvisionIDs = [ObjectId(id) for id in data["legalProvisions"]]
        legalProvisions = LegalProvision.objects(id__in=legalProvisionIDs)
        updates = {"level": level, "legalProvisions": legalProvisions}
        print(">>>>>>>>>> updates >>", updates)

        foreas = Foreas.objects.get(code=code)

        foreas_dict = foreas.to_dict()
        id = foreas_dict.pop("_id")
        del foreas.id
        foreas_dict.update(updates)

        foreas_updated = Foreas(**foreas_dict)

        diff = DeepDiff(foreas.to_dict(), foreas_updated.to_dict())

        if diff:
            print(">>>>>>>>>>", diff)
            foreas = Foreas.objects(id=id).first()
            foreas.update(**foreas_dict)
            Change(action="update", who=who, what=what, change=diff).save()

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
