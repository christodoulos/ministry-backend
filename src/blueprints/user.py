from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole
from src.models.psped.change import Change
from src.blueprints.decorators import has_helpdesk_role
import json


user = Blueprint("user", __name__)


@user.route("/myaccesses")
@jwt_required()
def get_my_organizations():
    user = User.get_user_by_email(get_jwt_identity())
    roles = user.roles
    organizationCodesListofLists = [role.foreas for role in roles if role.active and role.role in ["ADMIN", "EDITOR"]]
    organizationCodes = [item for sublist in organizationCodesListofLists for item in sublist]
    monadesCodesListofLists = [role.monades for role in roles if role.active and role.role in ["ADMIN", "EDITOR"]]
    monadesCodes = [item for sublist in monadesCodesListofLists for item in sublist]

    return Response(json.dumps({"organizations": organizationCodes, "organizational_units": monadesCodes}), status=200)


@user.route("/all")
@jwt_required()
@has_helpdesk_role
def get_all_users():
    users = User.objects()
    return Response(users.to_json(), status=200)

@user.route("/<string:email>", methods=["PUT"])
@jwt_required()
@has_helpdesk_role
def set_user_accesses(email: str):

    data = request.get_json()

    orgarganizationCodes = data["organizationCodes"]
    organizationalUnitCodes = data["organizationalUnitCodes"]

    user = User.objects.get(email=email)

    editor_role = None
    for role in user.roles:
        if role.role == 'EDITOR':
            editor_role = role
            break

    if editor_role:
        editor_role.foreas = orgarganizationCodes
        editor_role.monades = organizationalUnitCodes
    else:
        new_role = UserRole(role='EDITOR', foreas=orgarganizationCodes, monades=organizationalUnitCodes)
        user.roles.append(new_role)
    
    user.save()

    who = get_jwt_identity()
    what = {"entity": "user", "key": {"email": email}}
    Change(action="update", who=who, what=what, change={"foreas": orgarganizationCodes, "monades":organizationalUnitCodes}).save()

    return Response(
        json.dumps({"message": "<strong>Ο χρηστης ενημερώθηκε</strong>"}),
        mimetype="application/json",
        status=201,
    )