import json
from datetime import datetime
from flask import Blueprint, request, Response
from src.models.psped import Diataxi
from src.models.psped import NomikiPraxi, Abolition
from mongoengine import ValidationError

diataxeis = Blueprint("diataxeis", __name__)


@diataxeis.route("/diataxeis", methods=["POST"])
def create_diataxi():
    try:
        data = request.get_json()

        try:
            legal_act = NomikiPraxi.objects.get(legalActCode=data["legalActCode"])
        except NomikiPraxi.DoesNotExist:
            return Response(
                json.dumps({"error": f"Δεν βρέθηκε νομική πράξη με κωδικό {data['legalActCode']}"}),
                mimetype="application/json",
                status=404,
            )
        data["legalProvisionCode"] = Diataxi.generate_diataxi_code()
        diataxi = Diataxi(**data)

        diataxi.save()
        return Response(diataxi.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)


@diataxeis.route("/diataxeis/", methods=["GET"])
def list_all_diataxi():
    diataxeis = Diataxi.objects()
    return Response(diataxeis.to_json(), mimetype="application/json", status=200)


@diataxeis.route("/diataxeis/<string:code>", methods=["GET"])
def get_diataxi(code: str):
    try:
        diataxi = Diataxi.objects.get(legalProvisionCode=code)
        return Response(diataxi.to_json(), mimetype="application/json", status=200)
    except Diataxi.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε διάταξη με τον κωδικό {code}"}), mimetype="application/json", status=404
        )


@diataxeis.route("/diataxeis/<string:code>", methods=["PUT"])
def update_diataxi(code: str):
    data = request.get_json()

    immutable_fields: list = [
        "legalActCode",
        "creationDate",
        "userCode",
    ]
    update_fields = data.keys()

    if any(field in update_fields for field in immutable_fields):
        return Response(
            json.dumps({"error": "Μη επιτρεπτή ενημέρωση πεδίων: legalActCode, creationDate, userCode"}),
            mimetype="application/json",
            status=400,
        )

    nomiki_praxi_code = data.get("legalActCode")
    if nomiki_praxi_code:
        try:
            legal_act = NomikiPraxi.objects.get(legalActCode=nomiki_praxi_code)
        except NomikiPraxi.DoesNotExist:
            return Response(
                json.dumps({"error": f"Δεν βρέθηκε νομική πράξη με κωδικό {nomiki_praxi_code}"}),
                mimetype="application/json",
                status=404,
            )
    try:
        diataxi = Diataxi.objects.get(legalProvisionCode=code)
        for key, value in data.items():
            if hasattr(diataxi, key):
                if key == "abolition":
                    if value:
                        diataxi.abolition = Abolition(**value)
                else:
                    setattr(diataxi, key, value)

        diataxi.updateDate = datetime.now()
        diataxi.save()
        return Response(diataxi.to_json(), mimetype="application/json", status=200)
    except Diataxi.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρεθηκε διάταξη με τον κωδικό: {code}"}), mimetype="application/json", status=404
        )
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)


@diataxeis.route("/diataxeis/<string:code>", methods=["DELETE"])
def delete_diataxi(code: str):
    try:
        diataxi = Diataxi.objects.get(legalProvisionCode=code)
        diataxi.delete()
        return Response(
            json.dumps({"success": f"Η διάταξη με τον κωδικό {code} διαγράφηκε"}),
            mimetype="application/json",
            status=200,
        )
    except Diataxi.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε διάταξη με τον κωδικό: {code}"}), mimetype="application/json", status=404
        )
