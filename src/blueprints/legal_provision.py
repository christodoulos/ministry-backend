from flask import Blueprint, request, Response
from src.models.psped.legal_provision import LegalProvision
import json


legal_provision = Blueprint("legal_provision", __name__)


@legal_provision.route("", methods=["POST"])
def create_legal_provision():
    try:
        data = request.get_json()
        print(data)

        legal_provision = LegalProvision(**data)
        legal_provision.save()
        index = {
            "regulatedObject": legal_provision.regulatedObject.to_mongo().to_dict(),
            "legalAct": legal_provision.legalAct,
            "legalProvision": legal_provision.legalProvision.to_mongo().to_dict(),
        }

        return Response(
            json.dumps({"msg": "Επιτυχής δημιουργία διάταξης", "index": index}), mimetype="application/json", status=201
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"msg": f"Αποτυχία δημιουργίας διάταξης: {e}"}), mimetype="application/json", status=500
        )


# @diataxi.route("/diataxeis/", methods=["GET"])
# def list_all_diataxi():
#     diataxeis = Diataxi.objects()
#     return Response(diataxeis.to_json(), mimetype="application/json", status=200)


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
