import json
from flask import Blueprint, request, Response
from src.models.psped import LegalProvision
from src.models.psped import LegalAct

legal_provisions = Blueprint("legal_provisions", __name__)

@legal_provisions.route("/legal_provisions", methods=["POST"])
def create_legal_provision():
    try:
        data = request.get_json()
        try:
            legal_act = LegalAct.objects.get(legalActCode=data['legalActCode'])
        except LegalAct.DoesNotExist:
            return Response(json.dumps({"error": f"Legal act with code {data['legalActCode']} not found"}), mimetype="application/json", status=404)
        data['legalProvisionCode'] = LegalProvision.generate_legal_provision_code()  # Assumes auto-generation logic
        legal_provision = LegalProvision(**data)
        legal_provision.save()
        return Response(legal_provision.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)

@legal_provisions.route("/legal_provisions/<string:code>", methods=["GET"])
def get_legal_provision(code):
    try:
        legal_provision = LegalProvision.objects.get(legalProvisionCode=code)
        return Response(legal_provision.to_json(), mimetype="application/json", status=200)
    except LegalProvision.DoesNotExist:
        return Response(json.dumps({"error": f"Legal provision with code {code} not found"}), mimetype="application/json", status=404)

@legal_provisions.route("/legal_provisions/<string:code>", methods=["PUT"])
def update_legal_provision(code):
    data = request.get_json()
    try:
        legal_provision = LegalProvision.objects.get(legalProvisionCode=code)
        legal_provision.update(**data)
        return Response(legal_provision.to_json(), mimetype="application/json", status=200)
    except LegalProvision.DoesNotExist:
        return Response(json.dumps({"error": f"Legal provision with code {code} not found"}), mimetype="application/json", status=404)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)

@legal_provisions.route("/legal_provisions/<string:code>", methods=["DELETE"])
def delete_legal_provision(code):
    try:
        legal_provision = LegalProvision.objects.get(legalProvisionCode=code)
        legal_provision.delete()
        return Response(json.dumps({"success": f"Legal provision with code {code} deleted"}), mimetype="application/json", status=204)
    except LegalProvision.DoesNotExist:
        return Response(json.dumps({"error": f"Legal provision with code {code} not found"}), mimetype="application/json", status=404)
