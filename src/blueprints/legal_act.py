from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.psped.legal_act import FEK, LegalAct
from src.models.psped.change import Change
from src.models.upload import FileUpload
import json
from bson import ObjectId
from mongoengine.errors import NotUniqueError
from src.blueprints.utils import debug_print

legal_act = Blueprint("legal_act", __name__)


@legal_act.route("", methods=["POST"])
@jwt_required()
def create_legal_act():
    who = get_jwt_identity()
    try:
        data = request.get_json()
        legalActFile = FileUpload.objects.get(id=ObjectId(data["legalActFile"]))
        del data["legalActFile"]
        legalAct = LegalAct(**data, legalActFile=legalActFile)

        legalActKey = legalAct.create_key()

        what = {"entity": "legalAct", "key": {"code": legalActKey}}

        legalAct.save()
        Change(action="create", who=who, what=what, change=legalAct.to_mongo()).save()

        return Response(
            json.dumps({"message": f"Επιτυχής δημιουργία νομικής πράξης <strong>{legalAct.key2str}</strong>"}),
            mimetype="application/json",
            status=201,
        )
    except NotUniqueError:
        return Response(
            json.dumps({"message": "Απόπειρα δημιουργίας διπλοεγγραφής."}),
            mimetype="application/json",
            status=409,
        )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Απόπειρα δημιουργίας διπλοεγγραφής."})
            if "duplicate key error" in str(e)
            else json.dumps({"message": f"Αποτυχία ενημέρωσης νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )


@legal_act.route("/<string:id>", methods=["PUT"])
@jwt_required()
def update_legalact(id):
    who = get_jwt_identity()
    try:
        data = request.get_json()
        debug_print("LEGAL ACT PUT DATA", data)
        # Find the legalAct to be updated by its id
        legalAct = LegalAct.objects.get(id=ObjectId(id))
        foundLegalActKey = legalAct.legalActKey  # Save the key of the found legalAct for "what"
        debug_print("FOUND LEGAL ACT", legalAct.to_mongo().to_dict())
        try:
            legalActFile = FileUpload.objects.get(id=ObjectId(data["legalActFile"]["$oid"]))
        except Exception:
            legalActFile = FileUpload.objects.get(id=ObjectId(data["legalActFile"]))
        # Update the found legalAct with the new data
        for key, value in data.items():
            if hasattr(legalAct, key):
                if key == "fek":
                    fek = FEK(**value)
                    setattr(legalAct, key, fek)
                elif key == "legalActFile":
                    setattr(legalAct, key, legalActFile)
                else:
                    setattr(legalAct, key, value)
        # Generate a new legalActKey based on the updated data
        legalActKey = legalAct.create_key()
        legalAct.legalActKey = legalActKey
        debug_print("UPDATED LEGAL ACT", legalAct.to_mongo().to_dict())
        updatedLegalAct = legalAct.to_mongo()  # Save the updated legalAct for "change"
        updatedLegalActDict = updatedLegalAct.to_dict()  # Convert the updated legalAct to a dictionary
        del updatedLegalActDict["_id"]  # legalAct to be updated already has an id
        legalAct.update(**updatedLegalActDict)  # Update the legalAct with the new data
        what = {"entity": "legalAct", "key": {"legalActKey": foundLegalActKey}}
        # Save the change in the database
        Change(action="update", who=who, what=what, change=updatedLegalAct).save()

        return Response(
            json.dumps({"message": "Επιτυχής ενημέρωση νομικής πράξης."}),
            mimetype="application/json",
            status=201,
        )

    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Απόπειρα δημιουργίας διπλοεγγραφής."})
            if "duplicate key error" in str(e)
            else json.dumps({"message": f"Αποτυχία ενημέρωσης νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )


@legal_act.route("", methods=["GET"])
@jwt_required()
def list_all_nomikes_praxeis():
    nomikes_praxeis = LegalAct.objects()
    return Response(nomikes_praxeis.to_json(), mimetype="application/json", status=200)


@legal_act.route("/count", methods=["GET"])
@jwt_required()
def count_all_nomikes_praxeis():
    count = LegalAct.objects().count()
    return Response(json.dumps({"count": count}), mimetype="application/json", status=200)


@legal_act.route("/by-id/<string:id>", methods=["GET"])
@jwt_required()
def get_nomiki_praxi_by_id(id: str):
    try:
        legalAct = LegalAct.objects.get(id=ObjectId(id))
        return Response(legalAct.to_json(), mimetype="application/json", status=200)
    except LegalAct.DoesNotExist:
        return Response(
            json.dumps({"message": f"Νομική πράξη με id {id} δεν βρέθηκε"}),
            mimetype="application/json",
            status=404,
        )
