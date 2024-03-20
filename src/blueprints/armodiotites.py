import json
from flask import Blueprint, Response, request

from src.models.psped import Remit, LegalProvision
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.utils import Log

from deepdiff import DeepDiff

remit = Blueprint("armodiotites", __name__)

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
            json.dumps(
                {"error": (f"Δεν βρέθηκε αρμοδιότητα με κωδικό {remitCode}")}),
            mimetype="application/json",
            status=404,
        )

@remit.route("/remit", methods=["POST"])
def create_remit():
    try:
        data = request.get_json()
        # Assume data contains all required fields except those that are auto-generated (shouldnt we check that?)
        remit_code: str = Remit.generate_remit_code()
        data['remitCode'] = remit_code
        # check if unitCode exists 
        exists = OrganizationalUnit.objects(code=data["unitCode"]).first()
        if not exists:
            # TODO - Edw ti na kanoyme an exei kanei lathos
        # check if legalProvisionsCodes exist
        lpCodes = data['legalProvisionsCodes']
        for provisioncode in lpCodes:
            exists = LegalProvision.objects(code=provisioncode).first()
            if not exists:
                # TODO - na to petaw isws an den vriskei tipota
        new_remit = Remit(**data) 
        new_remit.save()
        return Response(new_remit.to_json(),
                        mimetype="application/json",
                        status=200)

    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία δημιουργίας αρμοδιότητας: {e}"}),
            mimetype="application/json",
            status=500,
        )


@remit.route("/remits/<string:remitCode>", methods=["PUT"])
def update_remit(remitCode):
    data = request.get_json()
    try:
        remit = Remit.objects.get(remitCode=remitCode)
    except Remit.DoesNotExist:
        return Response(
            json.dumps(
                {"error": f"Δεν βρέθηκε αρμοδιότητα με κωδικό {remitCode}"}),
            mimetype="application/json",
            status=404,
        )

    # Log the differences
    diff = DeepDiff(data, remit)
    if diff: Log(entity="remit", action="update", doc_id=data["remitCode"], value=diff)

    # Manually update each field
    try:
        for key, value in data.items():
            if hasattr(remit, key):
                setattr(remit, key, value)

        remit.save()  # This will now perform validation and other logic
        return Response(remit.to_json(),
                        mimetype="application/json",
                        status=200)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Αποτυχία ενημέρωσης αρμοδιότητας: {e}"}),
            mimetype="application/json",
            status=500,
        )


# @remit.route("/remits/<string:remitCode>", methods=["PUT"])
# def update_remit(remitCode):
#     data = request.get_json()
#     try:
#         Remit.objects(remitCode=remitCode).update_one(**data)
#         # Reload the document from the database to reflect the update
#         updated_remit = Remit.objects.get(remitCode=remitCode)
#         return Response(updated_remit.to_json(), mimetype="application/json", status=200)

#     except Remit.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Δεν βρέθηκε αρμοδιότητα με κωδικό {remitCode}"}),
#             mimetype="application/json",
#             status=404,
#         )
