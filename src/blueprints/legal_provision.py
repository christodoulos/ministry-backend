from flask import Blueprint, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models.psped.legal_provision import LegalProvision
from src.models.psped.legal_act import LegalAct
from src.models.psped.change import Change
import json


legal_provision = Blueprint("legal_provision", __name__)


@legal_provision.route("", methods=["POST"])
@jwt_required()
def create_legal_provision():
    who = get_jwt_identity()
    what = "legalProvision"
    try:
        data = request.get_json()
        print(data)
        legalActRef = LegalAct.objects.get(legalActKey=data["legalActKey"])

        legal_provision = LegalProvision(**data, legalActRef=legalActRef)
        legal_provision.save()
        index = {
            "legalActKey": legal_provision.legalActKey,
            "legalProvisionSpecs": legal_provision.legalProvisionSpecs.to_mongo().to_dict(),
        }
        Change(action="create", who=who, what=what, change=legal_provision.to_mongo()).save()

        return Response(
            json.dumps({"msg": "Επιτυχής δημιουργία διάταξης", "index": index}), mimetype="application/json", status=201
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"msg": f"Αποτυχία δημιουργίας διάταξης: {e}"}), mimetype="application/json", status=500
        )


@legal_provision.route("", methods=["GET"])
@jwt_required()
def list_all_legal_provisions():
    legal_provisions = LegalProvision.objects()
    return Response(legal_provisions.to_json(), mimetype="application/json", status=200)


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
