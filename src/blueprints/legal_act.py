from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.psped.legal_act import LegalAct, FEK
from src.models.psped.change import Change
from src.models.upload import FileUpload
from datetime import datetime
import json
from bson import ObjectId

legal_act = Blueprint("legal_act", __name__)


@legal_act.route("", methods=["POST"])
@jwt_required()
def create_legalact():
    who = get_jwt_identity()
    what = "legalAct"
    try:
        data = request.get_json()
        legalActFile = FileUpload.objects.get(id=ObjectId(data["legalActFile"]))
        del data["legalActFile"]
        legalAct = LegalAct(**data, legalActFile=legalActFile)
        legalAct.save()
        Change(action="create", who=who, what=what, change=legalAct.to_mongo()).save()
        return Response(
            json.dumps({"msg": "Επιτυχής δημιουργία νομικής πράξης"}), mimetype="application/json", status=201
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"msg": f"Αποτυχία δημιουργίας νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )


@legal_act.route("", methods=["GET"])
def list_all_nomikes_praxeis():
    nomikes_praxeis = LegalAct.objects()
    return Response(nomikes_praxeis.to_json(), mimetype="application/json", status=200)


# @legal_act.route("/nomikes_praxeis/<string:code>", methods=["GET"])
# def get_nomiki_praxi(code):
#     try:
#         nomiki_praxi = LegalAct.objects.get(legalActCode=code)
#         return Response(nomiki_praxi.to_json(), mimetype="application/json", status=200)
#     except LegalAct.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
#             mimetype="application/json",
#             status=404,
#         )


# @legal_act.route("/nomikes_praxeis/<string:code>", methods=["PUT"])
# def update_nomiki_praxi(code):
#     data = request.get_json()

#     immutable_fields: list = ["legalActCode", "creationDate", "userCode"]
#     update_fields = data.keys()

#     if any(field in update_fields for field in immutable_fields):
#         return Response(
#             json.dumps({"error": "Μη επιτρεπτή ενημέρωση πεδίων: legalActCode, creationDate, userCode"}),
#             mimetype="application/json",
#             status=400,
#         )
#     try:
#         nomiki_praxi = LegalAct.objects.get(legalActCode=code)
#     except LegalAct.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
#             mimetype="application/json",
#             status=404,
#         )
#     try:
#         for key, value in data.items():
#             if hasattr(nomiki_praxi, key):
#                 if key == "fek":
#                     fek = FEK(**value)
#                     setattr(nomiki_praxi, key, fek)
#                 else:
#                     setattr(nomiki_praxi, key, value)

#         nomiki_praxi.updateDate = datetime.now()
#         nomiki_praxi.save()
#         return Response(nomiki_praxi.to_json(), mimetype="application/json", status=200)
#     except Exception as e:
#         return Response(
#             json.dumps({"error": f"Αποτυχία ενημέρωσης νομικής πράξης: {e}"}),
#             mimetype="application/json",
#             status=500,
#         )