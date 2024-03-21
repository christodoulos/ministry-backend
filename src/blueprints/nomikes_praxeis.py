from calendar import c
import json
from datetime import datetime
from flask import Blueprint, request, Response
from src.models.psped import NomikiPraxi, FEKDiataxi  # Ensure this import matches your project structure

nomikes_praxeis = Blueprint("nomikes_praxeis", __name__)


@nomikes_praxeis.route("/nomikes_praxeis", methods=["POST"])
def create_nomiki_praxi():
    try:
        data = request.get_json()
        data["legalActCode"] = NomikiPraxi.generate_nomiki_praxi_code()  # Assumes auto-generation logic
        nomiki_praxi = NomikiPraxi(**data)
        nomiki_praxi.save()
        return Response(nomiki_praxi.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία δημιουργίας νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )


@nomikes_praxeis.route("/nomikes_praxeis/<string:code>", methods=["GET"])
def get_nomiki_praxi(code):
    try:
        nomiki_praxi = NomikiPraxi.objects.get(legalActCode=code)
        return Response(nomiki_praxi.to_json(), mimetype="application/json", status=200)
    except NomikiPraxi.DoesNotExist:
        return Response(
            json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
            mimetype="application/json",
            status=404,
        )


@nomikes_praxeis.route("/nomikes_praxeis/", methods=["GET"])
def list_all_nomikes_praxeis():
    nomikes_praxeis = NomikiPraxi.objects()
    return Response(nomikes_praxeis.to_json(), mimetype="application/json", status=200)


@nomikes_praxeis.route("/nomikes_praxeis/<string:code>", methods=["PUT"])
def update_nomiki_praxi(code):
    data = request.get_json()

    immutable_fields: list = ["legalActCode", "creationDate", "userCode"]
    update_fields = data.keys()

    if any(field in update_fields for field in immutable_fields):
        return Response(
            json.dumps({"error": "Μη επιτρεπτή ενημέρωση πεδίων: legalActCode, creationDate, userCode"}),
            mimetype="application/json",
            status=400,
        )
    try:
        nomiki_praxi = NomikiPraxi.objects.get(legalActCode=code)
    except NomikiPraxi.DoesNotExist:
        return Response(
            json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
            mimetype="application/json",
            status=404,
        )
    try:
        for key, value in data.items():
            if hasattr(nomiki_praxi, key):
                if key == "FEKref":
                    fek = FEKDiataxi(**value)
                    setattr(nomiki_praxi, key, fek)
                else:
                    setattr(nomiki_praxi, key, value)

        nomiki_praxi.updateDate = datetime.now()
        nomiki_praxi.save()
        return Response(nomiki_praxi.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία ενημέρωσης νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )


# @nomikes_praxeis.route("/nomikes_praxeis/<string:code>", methods=["DELETE"])
# def delete_nomiki_praxi(code):
#     try:
#         nomiki_praxi = NomikiPraxi.objects.get(legalActCode=code)

#         nomiki_praxi.delete()
#         return Response(
#             json.dumps(
#                 {"success": f"Η νομική πράξη με κωδικό {code} διαγράφηκε"}),
#             mimetype="application/json",
#             status=204,
#         )
#     except NomikiPraxi.DoesNotExist:
#         return Response(
#             json.dumps({"error":
#                         f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
#             mimetype="application/json",
#             status=404,
#         )
