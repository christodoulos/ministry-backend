from flask import Blueprint, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models.psped.foreas import Foreas
from src.models.psped.remit import Remit
from src.models.apografi.organizational_unit import OrganizationalUnit as Monada
from src.models.psped.legal_act import LegalAct
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
from src.models.psped.change import Change
from .utils import debug_print
import json
from src.blueprints.decorators import can_update_delete
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

    legal_provisions = [provision.to_dict() for provision in LegalProvision.objects(regulatedObject=regulatedObject)]
    # debug_print("LEGAL PROVISIONS BY ORGANIZATION CODE", legal_provisions)

    for provision in legal_provisions:
        # Determize legalActKey from legalActRef
        legalActRef = provision["legalAct"]

        legalAct = LegalAct.objects.get(id=legalActRef)
        legalActKey = legalAct.legalActKey

        # Add legalActKey to provision
        provision["legalActKey"] = legalActKey
        # Delete all ObjectId fields as they are not JSON serializable
        del provision["legalAct"]
        del provision["_id"]
        del provision["regulatedObject"]

    # debug_print("LEGAL PROVISIONS BY ORGANIZATION CODE", legal_provisions)

    return Response(json.dumps(legal_provisions), mimetype="application/json", status=200)


# @legal_provision.route("/by_regulated_remit/<string:code>", methods=["GET"])
# @jwt_required()
# def get_legal_provisions_by_regulated_remit(code: str):


@legal_provision.route("/delete", methods=["POST"])
@jwt_required()
@can_update_delete
def delete_legal_provision():
    data = request.get_json()
    debug_print("DELETE LEGAL PROVISION", data)

    code = data["code"]
    legalProvisionType = data["provisionType"]
    foreas = Foreas.objects.get(code=code)
    regulatedObject = RegulatedObject(
        regulatedObjectType=legalProvisionType,
        regulatedObjectId=foreas.id,
    )

    legalActKey = data["provision"]["legalActKey"]
    legalAct = LegalAct.objects.get(legalActKey=legalActKey)
    legalProvisionSpecs = data["provision"]["legalProvisionSpecs"]

    legalProvision = LegalProvision.objects(
        legalAct=legalAct, legalProvisionSpecs=legalProvisionSpecs, regulatedObject=regulatedObject
    ).first()

    if not legalProvision:
        return Response(
            json.dumps({"message": "Η διάταξη δεν είχε αποθηκευτεί στη βάση δεδομένων. Απλά διαγράφηκε από την λίστα που εμφανίζεται."}),
            mimetype="application/json",
            status=201,
        )

    debug_print("DELETE LEGAL PROVISION", legalProvision.to_dict())

    try:
        legalProvision.delete()
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
        Change(action="delete", who=who, what=what, change=legalProvision.to_mongo()).save()
        return Response(json.dumps({"message": "<strong>H διάταξη διαγράφηκε</strong>"}), mimetype="application/json", status=201)
    except Exception as e:
        print(e)
        return Response(json.dumps({"message": f"<strong>Error:</strong> {str(e)}"}), mimetype="application/json", status=500)


@legal_provision.route("/update", methods=["POST"])
@jwt_required()
@can_update_delete
def update_legal_provision():
    data = request.get_json()
    debug_print("UPDATE LEGAL PROVISION", data)

    code = data["code"]
    if data["remitID"]:
        remitID = ObjectId(data["remitID"])
    legalProvisionType = data["provisionType"]
    currentProvision = data["currentProvision"]
    updatedProvision = data["updatedProvision"]

    if legalProvisionType == "organization":
        foreas = Foreas.objects.get(code=code)
        regulatedObject = RegulatedObject(
            regulatedObjectType=legalProvisionType,
            regulatedObjectId=foreas.id,
        )
    elif legalProvisionType == "organizationalUnit":
        monada = Monada.objects.get(code=code)
        regulatedObject = RegulatedObject(
            regulatedObjectType=legalProvisionType,
            regulatedObjectId=monada.id,
        )
    else:  # legalProvisionType == "remit"
        regulatedObject = RegulatedObject(
            regulatedObjectType=legalProvisionType,
            regulatedObjectId=remitID,
        )

    # try:
    #     foreas = Foreas.objects.get(code=code)
    #     regulatedObject = RegulatedObject(
    #         regulatedObjectType=legalProvisionType,
    #         regulatedObjectId=foreas.id,
    #     )
    # except Exception:
    #     monada = Monada.objects.get(code=code)
    #     regulatedObject = RegulatedObject(
    #         regulatedObjectType=legalProvisionType,
    #         regulatedObjectId=monada.id,
    #     )

    # Will delete the current provision and insert the updated one
    legalActKey = currentProvision["legalActKey"]
    legalAct = LegalAct.objects.get(legalActKey=legalActKey)
    legalProvisionSpecs = currentProvision["legalProvisionSpecs"]
    existing_legal_provision = LegalProvision.objects(
        legalAct=legalAct, legalProvisionSpecs=legalProvisionSpecs, regulatedObject=regulatedObject
    ).first()

    if not existing_legal_provision:
        return Response(
            json.dumps({"message": "Η διάταξη δεν είχε αποθηκευτεί στη βάση δεδομένων. Απλά διαγράφηκε από την λίστα που εμφανίζεται."}),
            mimetype="application/json",
            status=201,
        )

    try:
        existing_legal_provision.delete()

        new_legalActKey = updatedProvision["legalActKey"]
        new_legalAct = LegalAct.objects.get(legalActKey=new_legalActKey)
        new_legalProvisionSpecs = updatedProvision["legalProvisionSpecs"]
        new_legalProvisionText = updatedProvision["legalProvisionText"]
        new_legal_provision = LegalProvision(
            regulatedObject=regulatedObject,
            legalAct=new_legalAct,
            legalProvisionSpecs=new_legalProvisionSpecs,
            legalProvisionText=new_legalProvisionText,
        )
        new_legal_provision.save()

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
            "old": existing_legal_provision.to_mongo(),
            "new": new_legal_provision.to_mongo(),
        }
        Change(action="update", who=who, what=what, change=change).save()
        return Response(
            json.dumps(
                {
                    "message": "<strong>H διάταξη ανανεώθηκε</strong>",
                    "updatedLegalProvision": {
                        "legalActKey": new_legalActKey,
                        "legalProvisionSpecs": new_legalProvisionSpecs,
                        "legalProvisionText": new_legalProvisionText,
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
