from flask import Blueprint, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models.psped.foreas import Foreas
from src.models.psped.legal_act import LegalAct
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
from src.models.psped.change import Change
from .utils import dict2string, debug_print
import json
from mongoengine.errors import NotUniqueError


legal_provision = Blueprint("legal_provision", __name__)


@legal_provision.route("", methods=["POST"])
@jwt_required()
def create_legal_provision():
    who = get_jwt_identity()
    what = "legalProvision"
    try:
        data = request.get_json()
        print(data)
        legal_provision = LegalProvision(**data)
        legalActKey = legal_provision.legalActKey
        legalProvisionSpecs = legal_provision.legalProvisionSpecs

        legalProvisonSpecsStr = dict2string(legalProvisionSpecs.to_mongo().to_dict())

        key = {"legalActKey": legalActKey, "legalProvisionSpecs": legalProvisionSpecs}
        what = {"entity": "legalProvision", "key": key}

        legalProvision = legal_provision.to_mongo().to_dict()
        legal_provision.save()

        Change(action="create", who=who, what=what, change=legal_provision.to_mongo()).save()

        return Response(
            json.dumps(
                {
                    "message": f"Επιτυχής δημιουργία διάταξης από τη νομική πράξη <strong>{legalActKey} ({legalProvisonSpecsStr})</strong>",
                    "legalProvision": legalProvision,
                }
            ),
            mimetype="application/json",
            status=201,
        )
    except NotUniqueError:
        return Response(
            json.dumps(
                {"message": f"Υπάρχει ήδη διάταξη με κωδικό <strong>{legalActKey} ({legalProvisonSpecsStr})</strong>."}
            ),
            mimetype="application/json",
            status=409,
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": f"Αποτυχία δημιουργίας διάταξης: {e}"}), mimetype="application/json", status=500
        )


@legal_provision.route("", methods=["GET"])
@jwt_required()
def get_all_legal_provisions():
    legal_provisions = LegalProvision.objects().order_by("legalActNumber", "legalActYear")
    return Response(legal_provisions.to_json(), mimetype="application/json", status=200)


@legal_provision.route("/by_regulated_organization/<string:code>", methods=["GET"])
@jwt_required()
def get_legal_provision(code: str):
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
    # try:
    #     regulatedObject = RegulatedObject(
    #         regulatedObjectType="organization",
    #         regulatedObjectCode=code,
    #     )
    #     legal_provisions = LegalProvision.objects(regulatedObject=regulatedObject)
    #     return Response(legal_provisions.to_json(), mimetype="application/json", status=200)
    # except LegalProvision.DoesNotExist:
    #     return Response(
    #         json.dumps({"error": f"Δεν βρέθηκε διάταξη με κωδικό {id}"}), mimetype="application/json", status=404
    #     )


# @legal_provision.route("/from_list_of_ids", methods=["POST"])
# @jwt_required()
# def get_legal_provisions_from_list_of_ids():
#     data = request.get_json()
#     ids = [ObjectId(id["$oid"]) for id in data]
#     legal_provisions = LegalProvision.objects(id__in=ids)
#     return Response(legal_provisions.to_json(), mimetype="application/json", status=200)


# @legal_provision.route("/from_list_of_keys/update_regulated_object", methods=["POST"])
# @jwt_required()
# def update_regulated_object_from_list_of_keys():
#     data = request.get_json()
#     regulated_object = data["regulatedObject"]
#     keys = data["keys"]

#     existing_legal_provisions = LegalProvision.objects(regulatedObject=RegulatedObject(**regulated_object))
#     for prov in existing_legal_provisions:
#         prov.regulatedObject = None
#         prov.save()

#     for key in keys:
#         legal_provision = LegalProvision.objects.get(
#             legalActKey=key["legalActKey"], legalProvisionSpecs=key["legalProvisionSpecs"]
#         )
#         legal_provision.regulatedObject = RegulatedObject(**regulated_object)
#         legal_provision.save()

#     return Response(json.dumps({"msg": "Legal Provisions Updated"}), mimetype="application/json", status=200)


@legal_provision.route("/count", methods=["GET"])
@jwt_required()
def count_all_legal_provisions():
    count = LegalProvision.objects().count()
    return Response(json.dumps({"count": count}), mimetype="application/json", status=200)


# @diataxi.route("/diataxeis/<string:code>", methods=["GET"])
# def get_diataxi(code: str):
#     try:
#         diataxi = Diataxi.objects.get(legalProvisionCode=code)
#         return Response(diataxi.to_json(), mimetype="application/json", status=200)
#     except Diataxi.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Δεν βρέθηκε διάταξη με τον κωδικό {code}"}), mimetype="application/json", status=404
#         )


# @diataxi.route("/diataxeis/<string:code>", methods=["PUT"])
# def update_diataxi(code: str):
#     data = request.get_json()

#     immutable_fields: list = [
#         "legalActCode",
#         "creationDate",
#         "userCode",
#     ]
#     update_fields = data.keys()

#     if any(field in update_fields for field in immutable_fields):
#         return Response(
#             json.dumps({"error": "Μη επιτρεπτή ενημέρωση πεδίων: legalActCode, creationDate, userCode"}),
#             mimetype="application/json",
#             status=400,
#         )

#     nomiki_praxi_code = data.get("legalActCode")
#     if nomiki_praxi_code:
#         try:
#             legal_act = NomikiPraxi.objects.get(legalActCode=nomiki_praxi_code)
#         except NomikiPraxi.DoesNotExist:
#             return Response(
#                 json.dumps({"error": f"Δεν βρέθηκε νομική πράξη με κωδικό {nomiki_praxi_code}"}),
#                 mimetype="application/json",
#                 status=404,
#             )
#     try:
#         diataxi = Diataxi.objects.get(legalProvisionCode=code)
#         for key, value in data.items():
#             if hasattr(diataxi, key):
#                 if key == "abolition":
#                     if value:
#                         diataxi.abolition = Abolition(**value)
#                 else:
#                     setattr(diataxi, key, value)

#         diataxi.updateDate = datetime.now()
#         diataxi.save()
#         return Response(diataxi.to_json(), mimetype="application/json", status=200)
#     except Diataxi.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Δεν βρεθηκε διάταξη με τον κωδικό: {code}"}), mimetype="application/json", status=404
#         )
#     except Exception as e:
#         return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)


# @diataxi.route("/diataxeis/<string:code>", methods=["DELETE"])
# def delete_diataxi(code: str):
#     try:
#         diataxi = Diataxi.objects.get(legalProvisionCode=code)
#         diataxi.delete()
#         return Response(
#             json.dumps({"success": f"Η διάταξη με τον κωδικό {code} διαγράφηκε"}),
#             mimetype="application/json",
#             status=200,
#         )
#     except Diataxi.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Δεν βρέθηκε διάταξη με τον κωδικό: {code}"}), mimetype="application/json", status=404
#         )
