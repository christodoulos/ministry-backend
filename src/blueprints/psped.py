import json
from bson import ObjectId
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from deepdiff import DeepDiff
from mongoengine.errors import NotUniqueError

from src.models.psped.foreas import Foreas
from src.models.psped.change import Change
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
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


@psped.route("/organization/<string:code>", methods=["PUT"])
@jwt_required()
@can_edit
def update_foreas(code: str):
    who = get_jwt_identity()

    try:
        data = request.get_json()

        foreas_code = data["code"]
        regulatedObject = RegulatedObject(
            regulatedObjectType="organization",
            regulatedObjectCode=foreas_code,
        )
        level = data["level"]
        legalProvisions = data["legalProvisions"]

        existingProvisionDocs = LegalProvision.objects(regulatedObject=regulatedObject).exclude("id")
        existingProvisions = [provision.to_json() for provision in existingProvisionDocs]

        updates = {}

        newLegalProvisionDocs = []
        for provision in legalProvisions:
            legalProvision = LegalProvision(
                regulatedObject=regulatedObject,
                legalActKey=provision["legalActKey"],
                legalProvisionSpecs=provision["legalProvisionSpecs"],
                legalProvisionText=provision["legalProvisionText"],
            )
            if legalProvision.to_json() not in existingProvisions:
                newLegalProvisionDocs.append(legalProvision)

        if newLegalProvisionDocs:
            updates["legalProvisions"] = [
                provision
                for provision in [x.to_mongo() for x in newLegalProvisionDocs]
                + [x.to_mongo() for x in existingProvisionDocs]
            ]
            LegalProvision.objects.insert(newLegalProvisionDocs)

        foreas = Foreas.objects.get(code=foreas_code)
        if foreas.level != level:
            updates["level"] = level
            foreas.level = level
            foreas.save()

        if updates:
            what = {"entity": "organization", "key": {"code": foreas_code}}
            Change(action="update", who=who, what=what, change=updates).save()

            return Response(
                json.dumps({"message": "<strong>Επιτυχής ενημέρωση του φορέα</strong>"}),
                mimetype="application/json",
                status=201,
            )
        else:
            return Response(
                json.dumps({"message": "<strong>Δεν υπήρξε κάποια αλλαγή</strong>"}),
                mimetype="application/json",
                status=211,
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
