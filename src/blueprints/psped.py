import json
from bson import ObjectId
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt


from src.blueprints.utils import debug_print, dict2string
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.psped.foreas import Foreas
from src.models.psped.change import Change
from src.models.psped.legal_act import LegalAct
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
from src.blueprints.decorators import can_edit, can_update_delete, can_finalize_remits
from src.models.psped.monada import Monada

psped = Blueprint("psped", __name__)


@psped.route("/foreas/count", methods=["GET"])
def get_foreas_count():
    count = Foreas.objects.count()
    return Response(
        json.dumps({"count": count}),
        mimetype="application/json",
        status=200,
    )


@psped.route("/foreas/<string:code>", methods=["GET"])
def get_foreas(code: str):
    try:
        foreas = Foreas.objects.get(code=code)
        return Response(
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


# @psped.route("/monada/<string:code>", methods=["GET"])
# def get_monada(code: str):
#     try:
#         monada = Monada.objects.get(code=code)
#         return Response(
#             monada.to_json(),
#             mimetype="application/json",
#             status=200,
#         )
#     except Monada.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Δεν βρέθηκε μονάδα με κωδικό {code}"}),
#             mimetype="application/json",
#             status=404,
#         )


@psped.route("/organization/by-id/<string:id>", methods=["GET"])
@jwt_required()
def get_organization_by_id(id: str):
    foreas = Foreas.objects.get(id=ObjectId(id))
    if foreas:
        return Response(
            json.dumps(foreas.to_json()),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(
            json.dumps({"message": f"Δεν βρέθηκε φορέας με ObjectID {id}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/organization/by-code/<string:code>", methods=["GET"])
@jwt_required()
def get_organization_by_code(code: str):
    foreas = Foreas.objects.get(code=code)
    if foreas:
        return Response(
            json.dumps(foreas.to_json()),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(
            json.dumps({"message": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/organization/<string:code>", methods=["PUT"])
@jwt_required()
@can_edit
def update_foreas(code: str):
    curr_change = {}

    organization = Organization.objects.get(code=code)

    data = request.get_json()
    level = data["level"]
    provisionText = data["provisionText"]
    legalProvisions = data["legalProvisions"]
    debug_print("UPDATE FOREAS", data)

    organization = Foreas.objects.get(code=code)
    existing_level = organization.level
    existing_provisionText = organization.provisionText

    if level != existing_level:
        organization.level = level
        organization.save()
        curr_change["level"] = level

    if provisionText != existing_provisionText:
        organization.provisionText = provisionText
        organization.save()
        curr_change["provisionText"] = provisionText

    regulatedObject = RegulatedObject(
        regulatedObjectType="organization",
        regulatedObjectId=organization.id,
    )
    debug_print("REGULATED OBJECT", regulatedObject.to_mongo().to_dict())

    legal_provisions_changes_updates = []
    legal_provisions_changes_inserts = []
    for provision in legalProvisions:
        legalActKey = provision["legalActKey"]
        legalAct = LegalAct.objects.get(legalActKey=legalActKey)
        legalProvisionSpecs = provision["legalProvisionSpecs"]
        legalProvisionText = provision["legalProvisionText"]
        existing = LegalProvision.objects(
            regulatedObject=regulatedObject, legalAct=legalAct, legalProvisionSpecs=legalProvisionSpecs
        ).first()
        debug_print("CURRENT LEGAL PROVISION", provision)
        if existing:
            print("EXISTING LEGAL PROVISION FOUND")
            existing.update(legalProvisionText=legalProvisionText)
            legal_provisions_changes_updates.append(existing.to_mongo())
        else:
            print("NO EXISTING LEGAL PROVISION FOUND")
            legalProvision = LegalProvision(
                regulatedObject=regulatedObject,
                legalAct=legalAct,
                legalProvisionSpecs=legalProvisionSpecs,
                legalProvisionText=legalProvisionText,
            )
            legalProvision.save()
            legal_provisions_changes_inserts.append(legalProvision.to_mongo())

    curr_change["legalProvisions"] = {
        "inserts": legal_provisions_changes_inserts,
        "updates": legal_provisions_changes_updates,
    }

    who = get_jwt_identity()
    what = {"entity": "organization", "key": {"code": code}}
    Change(action="update", who=who, what=what, change=curr_change).save()

    return Response(
        json.dumps({"message": "<strong>Ο φορέας ενημερώθηκε</strong>"}),
        mimetype="application/json",
        status=201,
    )


@psped.route("organizationalUnit/<string:code>", methods=["PUT"])
@jwt_required()
@can_edit
def update_monada(code: str):
    curr_change = {}

    data = request.get_json()
    provisionText = data["provisionText"]
    legalProvisions = data["legalProvisions"]
    debug_print("UPDATE MONADA", data)

    try:
        organizationalUnit = Monada.objects.get(code=code)
        existing_provisionText = organizationalUnit.provisionText

        if provisionText != existing_provisionText:
            organizationalUnit.provisionText = provisionText
            organizationalUnit.save()
            curr_change["provisionText"] = provisionText
    except Monada.DoesNotExist:
        organizationalUnit = Monada(code=code, provisionText=provisionText)
        organizationalUnit.save()

    regulatedObject = RegulatedObject(
        regulatedObjectType="organizationalUnit",
        regulatedObjectId=organizationalUnit.apografi.monada.id,
    )
    debug_print("REGULATED OBJECT", regulatedObject.to_mongo().to_dict())

    legal_provisions_changes_updates = []
    legal_provisions_changes_inserts = []
    for provision in legalProvisions:
        legalActKey = provision["legalActKey"]
        legalAct = LegalAct.objects.get(legalActKey=legalActKey)
        legalProvisionSpecs = provision["legalProvisionSpecs"]
        legalProvisionText = provision["legalProvisionText"]
        existing = LegalProvision.objects(
            regulatedObject=regulatedObject, legalAct=legalAct, legalProvisionSpecs=legalProvisionSpecs
        ).first()
        debug_print("CURRENT LEGAL PROVISION", provision)
        if existing:
            print("EXISTING LEGAL PROVISION FOUND")
            existing.update(legalProvisionText=legalProvisionText)
            legal_provisions_changes_updates.append(existing.to_mongo())
        else:
            print("NO EXISTING LEGAL PROVISION FOUND")
            legalProvision = LegalProvision(
                regulatedObject=regulatedObject,
                legalAct=legalAct,
                legalProvisionSpecs=legalProvisionSpecs,
                legalProvisionText=legalProvisionText,
            )
            legalProvision.save()
            legal_provisions_changes_inserts.append(legalProvision.to_mongo())

    curr_change["legalProvisions"] = {
        "inserts": legal_provisions_changes_inserts,
        "updates": legal_provisions_changes_updates,
    }

    who = get_jwt_identity()
    what = {"entity": "organizationalUnit", "key": {"code": code}}
    Change(action="update", who=who, what=what, change=curr_change).save()

    return Response(
        json.dumps({"message": "<strong>Η μονάδα ενημερώθηκε</strong>"}),
        mimetype="application/json",
        status=201,
    )


@psped.route("/foreas/<string:code>/tree", methods=["GET"])
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


@psped.route("/monada/<string:code>", methods=["GET"])
def get_monada(code: str):
    try:
        monada = Monada.objects.get(code=code)
        return Response(
            monada.to_json(),
            mimetype="application/json",
            status=200,
        )
    except Monada.DoesNotExist:
        return Response(
            json.dumps({"remitsFinalized": False}),
            mimetype="application/json",
            status=200,
        )


@psped.route("/monada/all", methods=["GET"])
def get_all_monades():
    monades = Monada.objects()
    return Response(
        monades.to_json(),
        mimetype="application/json",
        status=200,
    )


@psped.route("/monada/aggregate/all", methods=["GET"])
def get_all_monades_aggregate():
    organizationalUnits = OrganizationalUnit.objects()
    for unit in organizationalUnits:
        monada = Monada.objects(code=unit.code).first()
        # if monada exists then the organizational unit has remitsFinalized False
        if monada:
            unit.remitsFinalized = monada.remitsFinalized
        else:
            unit.remitsFinalized = False
    return Response(
        organizationalUnits.to_json(),
        mimetype="application/json",
        status=200,
    )


@psped.route("/monada/<string:code>/finalize_remits", methods=["PUT"])
@jwt_required()
@can_finalize_remits
def finalize_remits(code: str):
    data = request.get_json()
    debug_print("FINALIZE REMITS", data)

    remitsFinalized = data["status"]

    monada = Monada.objects(code=code).first()

    if monada:
        monada.update(remitsFinalized=remitsFinalized)
    else:
        monada = Monada(code=code, remitsFinalized=remitsFinalized)
        monada.save()

    who = get_jwt_identity()
    what = {"entity": "organizationalUnit", "key": {"code": code}}
    Change(action="update", who=who, what=what, change={"remitsFinalized": remitsFinalized}).save()

    return Response(
        json.dumps(
            {
                "message": "Οι αρμοδιότητες της μονάδας ολοκληρώθηκαν" if remitsFinalized else "Αναίρεση ολοκλήρωσης αρμοδιοτήτων",
                "remitsFinalized": remitsFinalized,
            }
        ),
        mimetype="application/json",
        status=201,
    )
