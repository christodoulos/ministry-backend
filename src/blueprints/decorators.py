from flask import request, Response
from flask_jwt_extended import get_jwt_identity, get_jwt
from functools import wraps
import json


from src.models.psped.legal_provision import LegalProvision
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.psped.foreas import Foreas
from src.models.psped.remit import Remit


def can_edit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # current_user = get_jwt_identity()
        claims = get_jwt()
        # print(claims)

        user_roles = claims["roles"]
        type_roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
        code = kwargs.get("code", "")
        # print(">>>>>> CODE >>", code)
        type_roles = [x for x in type_roles if code in x["foreas"] or code in x["monades"]]

        if not type_roles:
            return Response(
                json.dumps({"message": f"Δεν επιτρέπεται η αλλαγή του φορέα {code}"}),
                mimetype="application/json",
                status=403,
            )

        return f(*args, **kwargs)

    return decorated_function


def can_update_delete(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()

        user_roles = claims["roles"]
        roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
        print(">>>>>> ROLES >>", roles)
        all_codes = [code for entry in roles for code_list in (entry["foreas"], entry["monades"]) for code in code_list]
        print(">>>>>> ALL CODES >>", all_codes)
        data = request.get_json()
        code = data.get("code", "")
        print(">>>>>> CODE >>", code)

        if code not in all_codes:
            return Response(
                json.dumps({"message": "<strong>Δεν έχετε τέτοιο δικαίωμα διαγραφής</strong>"}),
                mimetype="application/json",
                status=403,
            )

        return f(*args, **kwargs)

    return decorated_function


def can_delete_legal_provision(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(">>>>>> CAN DELETE DECORATOR")
        claims = get_jwt()
        # print(">>>>>> CLAIMS >>", claims)

        user_roles = claims["roles"]
        roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
        # print(">>>>>> ROLES >>", roles)
        all_codes = [code for entry in roles for code_list in (entry["foreas"], entry["monades"]) for code in code_list]
        # print(">>>>>> ALL CODES >>", all_codes)

        legal_provision_id = kwargs.get("legalProvisionID", "")
        print("LEGAL PROVISION ID >>>>", legal_provision_id)

        legal_provision = LegalProvision.objects.get(id=legal_provision_id)
        regulatedObject = legal_provision.regulatedObject
        regulatedObjectType = regulatedObject.regulatedObjectType
        regulatedObjectId = regulatedObject.regulatedObjectId

        code = ""
        if regulatedObjectType == "organization":
            foreas = Foreas.objects.get(id=regulatedObjectId)
            code = foreas.code
        elif regulatedObjectType == "organizationalUnit":
            organizationalUnit = OrganizationalUnit.objects.get(id=regulatedObjectId)
            code = organizationalUnit.code
        elif regulatedObjectType == "remit":
            remit = Remit.objects.get(id=regulatedObjectId)
            code = remit.organizationalUnitCode

        if code not in all_codes:
            return Response(
                json.dumps({"message": "<strong>Δεν έχετε τέτοιο δικαίωμα διαγραφής</strong>"}),
                mimetype="application/json",
                status=403,
            )
        print(">>>>>>>>>>>>> GO ON DELETE THE FUCKING LEGAL PROVISION !!!!")

        return f(*args, **kwargs)

    return decorated_function


def can_finalize_remits(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        user_roles = claims["roles"]
        roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
        all_codes = [code for entry in roles for code_list in (entry["foreas"], entry["monades"]) for code in code_list]

        code = kwargs.get("code", "")

        if code not in all_codes:
            return Response(
                json.dumps({"message": "<strong>Δεν έχετε τέτοιο δικαίωμα τροποποίησης</strong>"}),
                mimetype="application/json",
                status=403,
            )

        return f(*args, **kwargs)

    return decorated_function


def has_helpdesk_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        user_roles = claims["roles"]
        roles = [x for x in user_roles]
        # check if user has helpdesk role
        helpdesk_roles = [x for x in roles if x["role"] == "HELPDESK"]

        if not helpdesk_roles:
            return Response(
                json.dumps({"message": "<strong>Δεν έχετε τέτοιο δικαίωμα</strong>"}),
                mimetype="application/json",
                status=403,
            )
        return f(*args, **kwargs)

    return decorated_function
