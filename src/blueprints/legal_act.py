from flask import Blueprint, request, Response
from src.models.psped.legal_act import NomikiPraxi, FEK
from src.models.upload import FileUpload
from datetime import datetime
import json
from bson import ObjectId

legal_act = Blueprint("legal_act", __name__)


@legal_act.route("", methods=["POST"])
def create_legalact():
    try:
        data = request.get_json()
        legalActFile = FileUpload.objects.get(id=ObjectId(data["legalActFile"]))
        del data["legalActFile"]
        NomikiPraxi(**data, legalActFile=legalActFile).save()
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
    nomikes_praxeis = NomikiPraxi.objects()
    return Response(nomikes_praxeis.to_json(), mimetype="application/json", status=200)


@legal_act.route("/nomikes_praxeis/<string:code>", methods=["GET"])
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


@legal_act.route("/nomikes_praxeis/<string:code>", methods=["PUT"])
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
                if key == "fek":
                    fek = FEK(**value)
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
