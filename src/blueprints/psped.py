import json
from bson import ObjectId
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from deepdiff import DeepDiff
from mongoengine.errors import NotUniqueError

from src.blueprints.utils import debug_print, dict2string
from src.models.apografi.organization import Organization
from src.models.psped.foreas import Foreas
from src.models.psped.change import Change
from src.models.psped.legal_act import LegalAct
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


@psped.route("/organization/by-id/<string:id>")
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


@psped.route("/organization/by-code/<string:code>")
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
    organization_name = organization.preferredLabel

    success_message = f"<strong>Επιτυχής ενημέρωση του φορέα {organization_name}:</strong>&nbsp;"
    error_message = f"<strong>Σφάλμα κατά την ενημέρωση του φορέα {organization_name}:</strong>&nbsp;"

    data = request.get_json()
    level = data["level"]
    legalProvisions = data["legalProvisions"]
    debug_print("UPDATE FOREAS", data)

    organization = Foreas.objects.get(code=code)
    existing_level = organization.level

    if level != existing_level:
        organization.level = level
        organization.save()
        curr_change["level"] = level
        success_message += f"Ενημέρωση επιπέδου φορέα από {existing_level} σε {level}. "

    regulatedObject = RegulatedObject(
        regulatedObjectType="organization",
        regulatedObjectId=organization.id,
    )
    debug_print("REGULATED OBJECT", regulatedObject.to_mongo().to_dict())

    # Find the existing legal provisions for the organization
    existing_legal_provision_docs = LegalProvision.objects(regulatedObject=regulatedObject)
    # Find the  legal provisions from data["legalProvisions"] that are not included in the existing legal provisions

    existing_legal_provisions = [provision.to_json() for provision in existing_legal_provision_docs]
    #     legalAct = LegalAct.objects.get(id=legalActRef)
    #     legalActKey = legalAct.legalActKey
    #     provision.legalActKey = legalActKey
    debug_print("EXISTING LEGAL PROVISIONS", existing_legal_provisions)
    new_legal_provisions = [provision for provision in legalProvisions if provision not in existing_legal_provisions]
    debug_print("NEW LEGAL PROVISIONS", new_legal_provisions)

    # success_message += "Προσθήκη νέων διατάξεων: "
    legal_provisions_str = ""
    legal_provisions_changes = []
    for provision in new_legal_provisions:
        legalProvisionSpecs = provision["legalProvisionSpecs"]
        if not any(legalProvisionSpecs.values()):
            return Response(
                json.dumps({"message": f"{error_message}Κάποιο πεδίο της Διάταξης πρέπει να συμπληρωθεί"}),
                mimetype="application/json",
                status=400,
            )
        legalAct = LegalAct.objects.get(legalActKey=provision["legalActKey"])
        legalProvision = LegalProvision(
            regulatedObject=regulatedObject,
            legalAct=legalAct,
            legalProvisionSpecs=legalProvisionSpecs,
            legalProvisionText=provision["legalProvisionText"],
        )
        try:
            legalProvision.save()
            legal_provisions_str += f"{provision['legalActKey']} ({dict2string(legalProvisionSpecs)}), "
            legal_provisions_changes.append(legalProvision.to_mongo())
        except NotUniqueError:
            return Response(
                json.dumps(
                    {
                        "message": f"{error_message}Υπάρχει ήδη διάταξη με κωδικό {provision['legalActKey']} ({dict2string(legalProvisionSpecs)})"
                    }
                ),
                mimetype="application/json",
                status=409,
            )

    curr_change["legalProvisions"] = legal_provisions_changes
    if len(legalProvisions) == 1:
        success_message += f"Προσθήκη νέας διάταξης: {legal_provisions_str}"
    elif len(legalProvisions) > 1:
        success_message += f"Προσθήκη νέων διατάξεων: {legal_provisions_str}"

    who = get_jwt_identity()
    what = {"entity": "organization", "key": {"code": code}}
    Change(action="update", who=who, what=what, change=curr_change).save()

    return Response(
        json.dumps({"message": success_message}),
        mimetype="application/json",
        status=201,
    )

    # existingProvisionDocs = LegalProvision.objects(regulatedObject=regulatedObject).exclude("id")
    # existingProvisions = [provision.to_json() for provision in existingProvisionDocs]

    # updates = {}

    # newLegalProvisionDocs = []
    # for provision in legalProvisions:
    #     legalProvision = LegalProvision(
    #         regulatedObject=regulatedObject,
    #         legalActKey=provision["legalActKey"],
    #         legalProvisionSpecs=provision["legalProvisionSpecs"],
    #         legalProvisionText=provision["legalProvisionText"],
    #     )
    #     if legalProvision.to_json() not in existingProvisions:
    #         newLegalProvisionDocs.append(legalProvision)

    # if newLegalProvisionDocs:
    #     updates["legalProvisions"] = [
    #         provision
    #         for provision in [x.to_mongo() for x in newLegalProvisionDocs]
    #         + [x.to_mongo() for x in existingProvisionDocs]
    #     ]
    #     LegalProvision.objects.insert(newLegalProvisionDocs)

    # foreas = Foreas.objects.get(code=foreas_code)
    # if foreas.level != level:
    #     updates["level"] = level
    #     foreas.level = level
    #     foreas.save()

    # if updates:
    #     what = {"entity": "organization", "key": {"code": foreas_code}}
    #     Change(action="update", who=who, what=what, change=updates).save()

    #     return Response(
    #         json.dumps({"message": "<strong>Επιτυχής ενημέρωση του φορέα</strong>"}),
    #         mimetype="application/json",
    #         status=201,
    #     )
    # else:
    #     return Response(
    #         json.dumps({"message": "<strong>Δεν υπήρξε κάποια αλλαγή</strong>"}),
    #         mimetype="application/json",
    #         status=211,
    #     )
    # except Foreas.DoesNotExist:
    #     return Response(
    #         json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
    #         mimetype="application/json",
    #         status=404,
    #     )


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
