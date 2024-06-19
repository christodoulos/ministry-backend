from flask import Blueprint, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from mongoengine import DoesNotExist
from src.models.psped.foreas import Foreas
from src.models.psped.remit import Remit
from src.models.apografi.organizational_unit import OrganizationalUnit as Monada
from src.models.psped.legal_act import LegalAct
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
from src.models.psped.change import Change
from .utils import debug_print
import json
from src.blueprints.decorators import can_update_delete, can_delete_legal_provision
from bson import ObjectId


legal_provision = Blueprint("legal_provision", __name__)


@legal_provision.route("/by_regulated_organization/<string:code>", methods=["GET"])
@jwt_required()
def get_legal_provisions_by_regulated_organization(code: str):
    organization = Foreas.objects.get(code=code)
    # debug_print("LEGAL PROVISIONS BY ORGANIZATION CODE", organization.to_mongo().to_dict())
    organization_id = organization.id
    regulatedObject = RegulatedObject(
        regulatedObjectType="organization",
        regulatedObjectId=organization_id,
    )

    legal_provisions = [provision.to_mongo().to_dict() for provision in LegalProvision.objects(regulatedObject=regulatedObject)]
    # debug_print("LEGAL PROVISIONS BY ORGANIZATION CODE", legal_provisions)

    for provision in legal_provisions:
        # Determize legalActKey from legalActRef
        legalActRef = provision["legalAct"]

        legalAct = LegalAct.objects.get(id=legalActRef)
        legalActKey = legalAct.legalActKey

        # Add legalActKey to provision
        provision["legalActKey"] = legalActKey
        provision["_id"] = str(provision["_id"])
        # Delete all ObjectId fields as they are not JSON serializable
        del provision["legalAct"]
        del provision["regulatedObject"]

    # debug_print("LEGAL PROVISIONS BY ORGANIZATION CODE", legal_provisions)

    return Response(json.dumps(legal_provisions), mimetype="application/json", status=200)


@legal_provision.route("by_regulated_organization_unit/<string:code>", methods=["GET"])
@jwt_required()
def get_legal_provisions_by_regulated_organization_unit(code: str):
    organization_unit = Monada.objects.get(code=code)
    debug_print("LEGAL PROVISIONS BY ORGANIZATION UNIT CODE", organization_unit.to_mongo().to_dict())
    organization_unit_id = organization_unit.id
    regulatedObject = RegulatedObject(
        regulatedObjectType="organizationUnit",
        regulatedObjectId=organization_unit_id,
    )
    print(regulatedObject.to_mongo().to_dict())

    legal_provisions = [provision.to_mongo().to_dict() for provision in LegalProvision.objects(regulatedObject=regulatedObject)]
    # debug_print("LEGAL PROVISIONS BY ORGANIZATION UNIT CODE", legal_provisions)

    for provision in legal_provisions:
        # Determize legalActKey from legalActRef
        legalActRef = provision["legalAct"]

        legalAct = LegalAct.objects.get(id=legalActRef)
        legalActKey = legalAct.legalActKey

        # Add legalActKey to provision
        provision["legalActKey"] = legalActKey
        provision["_id"] = str(provision["_id"])
        # Delete all ObjectId fields as they are not JSON serializable
        del provision["legalAct"]
        del provision["regulatedObject"]

    # debug_print("LEGAL PROVISIONS BY ORGANIZATION UNIT CODE", legal_provisions)

    return Response(json.dumps(legal_provisions), mimetype="application/json", status=200)


@legal_provision.route("/<string:legalProvisionID>", methods=["DELETE"])
@jwt_required()
@can_delete_legal_provision
def delete_legal_provision(legalProvisionID: str):
    legal_provision = LegalProvision.objects.get(id=legalProvisionID)
    regulatedObject = legal_provision.regulatedObject

    try:
        existing_legal_provision = LegalProvision.objects.get(id=legalProvisionID)
        existing_legal_provision.delete()
    except DoesNotExist:
        return Response(json.dumps({"message": "Η διάταξη δεν υπάρχει"}), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps({"message": f"<strong>Error:</strong> {str(e)}"}), mimetype="application/json", status=500)

    if regulatedObject.regulatedObjectType == "remit":
        try:
            remit = Remit.objects.get(id=regulatedObject.regulatedObjectId)
            remit.legalProvisionRefs = [provision for provision in remit.legalProvisionRefs if str(provision.id) != legalProvisionID]
            remit.save()
        except DoesNotExist:
            return Response(json.dumps({"message": "Η αρμοδιότητα δεν υπάρχει"}), mimetype="application/json", status=404)
        except Exception as e:
            return Response(json.dumps({"message": f"<strong>Error:</strong> {str(e)}"}), mimetype="application/json", status=500)

    who = get_jwt_identity()
    what = {"entity": "legalProvision", "key": {"legalProvisionID": legalProvisionID}}
    change = existing_legal_provision.to_mongo().to_dict()
    Change(action="delete", who=who, what=what, change=change).save()
    return Response(json.dumps({"message": "<strong>H διάταξη διαγράφηκε</strong>"}), mimetype="application/json", status=201)


@legal_provision.route("", methods=["PUT"])
@jwt_required()
@can_update_delete
def update_legal_provision():
    data = request.get_json()
    debug_print("UPDATE LEGAL PROVISION", data)

    code = data["code"]
    if data["remitID"]:
        code = ObjectId(data["remitID"])
    legalProvisionType = data["provisionType"]
    currentProvision = data["currentProvision"]
    updatedProvision = data["updatedProvision"]

    regulatedObject = LegalProvision.regulated_object(code, legalProvisionType)
    print("REGULATED OBJECT >>>>", regulatedObject.to_mongo().to_dict())

    legalActKey = currentProvision["legalActKey"]
    legalAct = LegalAct.objects.get(legalActKey=legalActKey)
    legalProvisionSpecs = currentProvision["legalProvisionSpecs"]
    existing_legal_provision = LegalProvision.objects(
        legalAct=legalAct, legalProvisionSpecs=legalProvisionSpecs, regulatedObject=regulatedObject
    ).first()

    try:
        updated_legalActKey = updatedProvision["legalActKey"]
        updated_legalAct = LegalAct.objects.get(legalActKey=updated_legalActKey)
        updated_legalProvisionSpecs = updatedProvision["legalProvisionSpecs"]
        updated_legalProvisionText = updatedProvision["legalProvisionText"]
        existing_legal_provision.update(
            legalAct=updated_legalAct,
            legalProvisionSpecs=updated_legalProvisionSpecs,
            legalProvisionText=updated_legalProvisionText,
        )

        who = get_jwt_identity()
        what = {
            "entity": "legalProvision",
            "key": {
                "code": code,
                "legalProvisionType": legalProvisionType,
                "legalActKey": legalActKey,
                "legalProvisionSpecs": legalProvisionSpecs,
            },
        }
        change = {
            "old": currentProvision,
            "new": updatedProvision,
        }
        Change(action="update", who=who, what=what, change=change).save()
        return Response(
            json.dumps(
                {
                    "message": "<strong>H διάταξη ανανεώθηκε</strong>",
                    "updatedLegalProvision": {
                        "legalActKey": updated_legalActKey,
                        "legalProvisionSpecs": updated_legalProvisionSpecs,
                        "legalProvisionText": updated_legalProvisionText,
                    },
                }
            ),
            mimetype="application/json",
            status=201,
        )
    except Exception as e:
        print(e)
        return Response(json.dumps({"message": f"<strong>Error:</strong> {str(e)}"}), mimetype="application/json", status=500)


@legal_provision.route("/count", methods=["GET"])
@jwt_required()
def count_all_legal_provisions():
    count = LegalProvision.objects().count()
    return Response(json.dumps({"count": count}), mimetype="application/json", status=200)
