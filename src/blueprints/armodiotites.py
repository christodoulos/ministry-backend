from datetime import datetime
import json
from flask import Blueprint, Response, request

from src.models.psped.remit import Remit
from src.models.psped.legal_provision import LegalProvision
from src.models.apografi.organizational_unit import OrganizationalUnit

remit = Blueprint("armodiotites", __name__)


@remit.route("/remit", methods=["POST"])
def create_remit():
    try:
        # Assume data contains all required fields except those that are auto-generated (shouldnt we check that?)
        data = request.get_json()
        # check if organization unit code exists
        try:
            unitcode = OrganizationalUnit.objects.get(code=data["unitCode"])
        except OrganizationalUnit.DoesNotExist:
            return Response(
                json.dumps({"error": f"Δεν βρέθηκε μονάδα με κωδικό {data['unitCode']}"}),
                mimetype="application/json",
                status=404,
            )
        # check if diataxeis codes exists
        for diataxi_code in data["diataxisCodes"]:
            try:
                diataxi = LegalProvision.objects.get(legalProvisionCode=diataxi_code)
            except LegalProvision.DoesNotExist:
                return Response(
                    json.dumps({"error": f"Δεν βρέθηκε νομική διάταξη με κωδικό {diataxi_code}"}),
                    mimetype="application/json",
                    status=404,
                )
        # create remit code
        data["remitCode"] = Remit.generate_remit_code()
        # create a remit & save it
        remit = Remit(**data)
        remit.save()
        return Response(remit.to_json(), mimetype="application/json", status=200)

    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία δημιουργίας αρμοδιότητας: {e}"}),
            mimetype="application/json",
            status=500,
        )


@remit.route("/remits/", methods=["GET"])
def retrieve_all_remit():
    remits = Remit.objects()
    return Response(
        remits.to_json(),
        mimetype="application/json",
        status=200,
    )


@remit.route("/remits/<string:remitCode>", methods=["GET"])
def retrieve_armodiotita(remitCode: str):
    try:
        remit = Remit.objects.get(remitCode=remitCode)
        return Response(
            remit.to_json(),
            mimetype="application/json",
            status=200,
        )
    except Remit.DoesNotExist:
        return Response(
            json.dumps({"error": (f"Δεν βρέθηκε αρμοδιότητα με κωδικό {remitCode}")}),
            mimetype="application/json",
            status=404,
        )


@remit.route("/remits/<string:remitCode>", methods=["PUT"])
def update_remit(remitCode: str):
    data = request.get_json()
    try:
        remit = Remit.objects.get(remitCode=remitCode)
    except Remit.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε αρμοδιότητα με κωδικό {remitCode}"}),
            mimetype="application/json",
            status=404,
        )

    # check for the immutable fields
    immutable_fields: list = ["remitCode", "creationDate", "userCode"]
    update_fields = data.keys()

    if any(field in update_fields for field in immutable_fields):
        return Response(
            json.dumps({"error": "Μη επιτρεπτή ενημέρωση πεδίων: remitCode, creationDate, userCode"}),
            mimetype="application/json",
            status=400,
        )

    # check that Organization unit code exists
    unit_code = data.get("unitCode")
    if unit_code:
        try:
            org_unit = OrganizationalUnit.objects.get(code=unit_code)
        except OrganizationalUnit.DoesNotExist:
            return Response(
                json.dumps({"error": f"Δεν βρέθηκε Μονάδα με κωδικό {unit_code}"}),
                mimetype="application/json",
                status=404,
            )

    # check that diataxeis codes exist
    diataxis_codes = data.get("diataxisCodes")
    if diataxis_codes:
        for code in diataxis_codes:
            try:
                diataxi = LegalProvision.objects.get(legalProvisionCode=code)
            except LegalProvision.DoesNotExist:
                return Response(
                    json.dumps({"error": f"Δεν βρέθηκε νομική διάταξη με κωδικό {code}"}),
                    mimetype="application/json",
                    status=404,
                )

    # Manually update each field
    try:
        for key, value in data.items():
            if hasattr(remit, key):
                setattr(remit, key, value)

        remit.save()  # This will now perform validation and other logic
        return Response(remit.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία ενημέρωσης αρμοδιότητας: {e}"}),
            mimetype="application/json",
            status=500,
        )


@remit.route("/remits/<string:remitCode>", methods=["DELETE"])
def delete_remit(remitCode: str):
    try:
        remit = Remit.objects.get(remitCode=remitCode)
        remit.detele()
        return Response(
            json.dumps({"success": f"Η αρμοδιότητα με τον κωδικό {remitCode} διαγράφηκε"}),
            mimetype="application/json",
            status=200,
        )
    except Remit.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε αρμοδιότητα με τον κωδικό: {remitCode}"}),
            mimetype="application/json",
            status=404,
        )
