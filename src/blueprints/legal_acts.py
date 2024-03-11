import json
from flask import Blueprint, request, Response
from src.models.psped import LegalAct  # Ensure this import matches your project structure

legal_acts = Blueprint("legal_acts", __name__)

@legal_acts.route("/legal_acts", methods=["POST"])
def create_legal_act():
    try:
        data = request.get_json()
        data['legalActCode'] = LegalAct.generate_legal_act_code()  # Assumes auto-generation logic
        legal_act = LegalAct(**data)
        legal_act.save()
        return Response(legal_act.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία δημιουργίας νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )

@legal_acts.route("/legal_acts/<string:code>", methods=["GET"])
def get_legal_act(code):
    try:
        legal_act = LegalAct.objects.get(legalActCode=code)
        return Response(legal_act.to_json(), mimetype="application/json", status=200)
    except LegalAct.DoesNotExist:
        return Response(
            json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
            mimetype="application/json",
            status=404,
        )
    
@legal_acts.route("/legal_acts/<string:code>", methods=["PUT"])
def update_legal_act(code):
    data = request.get_json()
    try:
        legal_act = LegalAct.objects.get(legalActCode=code)
    except LegalAct.DoesNotExist:
        return Response(
            json.dumps({"error": f"Νομική πράξη με κωδικό {code} δεν βρέθηκε"}),
            mimetype="application/json",
            status=404,
        )
    try:
        for key, value in data.items():
            if hasattr(legal_act, key):
                setattr(legal_act, key, value)
        
        legal_act.save()  # This will now perform validation and other logic
        return Response(legal_act.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία ενημέρωσης νομικής πράξης: {e}"}),
            mimetype="application/json",
            status=500,
        )