from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User
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
