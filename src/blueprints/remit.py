from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.models.psped.legal_act import LegalAct
from src.models.psped.remit import Remit
from src.models.psped.legal_provision import LegalProvision, RegulatedObject
from src.models.psped.change import Change
import json

from .utils import debug_print

remit = Blueprint("remit", __name__)


@remit.route("", methods=["POST"])
@jwt_required()
def create_remit():
    curr_change = {}
    try:
        data = request.get_json()

        debug_print("POST REMIT", data)

        # regulatedObject = data["regulatedObject"]
        organizationalUnitCode = data["regulatedObject"]["regulatedObjectCode"]
        remitText = data["remitText"]
        remitType = data["remitType"]
        cofog = data["cofog"]

        newRemit = Remit(
            organizationalUnitCode=organizationalUnitCode,
            remitText=remitText,
            remitType=remitType,
            cofog=cofog,
        ).save()

        newRemitID = newRemit.id
        regulatedObject = RegulatedObject(
            regulatedObjectType="remit",
            regulatedObjectId=newRemitID,
        )

        legalProvisions = data["legalProvisions"]
        legal_provisions_changes_inserts = []
        legal_provisions_docs = []
        for provision in legalProvisions:
            legalActKey = provision["legalActKey"]
            legalAct = LegalAct.objects.get(legalActKey=legalActKey)
            legalProvisionSpecs = provision["legalProvisionSpecs"]
            legalProvisionText = provision["legalProvisionText"]

            legalProvision = LegalProvision(
                regulatedObject=regulatedObject,
                legalAct=legalAct,
                legalProvisionSpecs=legalProvisionSpecs,
                legalProvisionText=legalProvisionText,
            ).save()
            legal_provisions_docs.append(legalProvision)
            legal_provisions_changes_inserts.append(legalProvision.to_mongo())

        curr_change["legalProvisions"] = {
            "inserts": legal_provisions_changes_inserts,
            # "updates": legal_provisions_changes_updates,
        }

        who = get_jwt_identity()
        what = {"entity": "remit", "key": {"organizationalUnitCode": organizationalUnitCode}}
        Change(action="insert", who=who, what=what, change=curr_change).save()

        newRemit.legalProvisionRefs = legal_provisions_docs
        newRemit.save()

        return Response(
            json.dumps({"message": "Η αρμοδιότητα δημιουργήθηκε με επιτυχία"}),
            mimetype="application/json",
            status=201,
        )

    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": f"<strong>Αποτυχία δημιουργίας αρμοδιότητας:</strong> {e}"}),
            mimetype="application/json",
            status=500,
        )


@remit.route("", methods=["GET"])
@jwt_required()
def retrieve_all_remit():
    remits = Remit.objects()
    return Response(
        remits.to_json(),
        mimetype="application/json",
        status=200,
    )


@remit.route("/count", methods=["GET"])
@jwt_required()
def count_all_remits():
    count = Remit.objects().count()
    return Response(json.dumps({"count": count}), mimetype="application/json", status=201)


@remit.route("/by_code/<string:code>", methods=["GET"])
@jwt_required()
def retrieve_remit_by_code(code):
    # print(code)
    remits = Remit.objects(organizationalUnitCode=code).exclude("id")
    # debug_print("GET REMIT BY CODE", remits.to_json())

    remitsToReturn = []
    for remit in remits:
        # print(remit.to_json())
        data = {
            "organizationalUnitCode": remit.organizationalUnitCode,
            "remitText": remit.remitText,
            "remitType": remit.remitType,
            "cofog": remit.cofog.to_mongo().to_dict(),
            "legalProvisions": [],
        }
        # legal_provisions = [provision.to_dict() for provision in remit.legalProvisionRefs]
        legal_provisions = [provision for provision in remit.legalProvisionRefs]

        for provision in legal_provisions:
            legalActRef = provision["legalAct"]
            legalActKey = legalActRef.legalActKey
            legalProvisionSpecs = provision["legalProvisionSpecs"].to_mongo().to_dict()
            legalProvisionText = provision["legalProvisionText"]
            data["legalProvisions"].append(
                {
                    "legalActKey": legalActKey,
                    "legalProvisionSpecs": legalProvisionSpecs,
                    "legalProvisionText": legalProvisionText,
                }
            )

            # legalAct = LegalAct.objects.get(id=legalActRef)
            # legalActKey = legalAct.legalActKey
            # legalProvisionSpecs = provision["legalProvisionSpecs"]
            # legalProvisionText = provision["legalProvisionText"]
            # data["legalProvisions"].append(
            #     {
            #         "legalActKey": legalActKey,
            #         "legalProvisionSpecs": legalProvisionSpecs,
            #         "legalProvisionText": legalProvisionText,
            #     }
            # )

        remitsToReturn.append(data)

    # print(remitsToReurn)

    return Response(
        json.dumps(remitsToReturn),
        mimetype="application/json",
        status=200,
    )
