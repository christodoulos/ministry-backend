from flask import request, Response
from flask_jwt_extended import get_jwt_identity, get_jwt
from functools import wraps
import json


def can_edit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # current_user = get_jwt_identity()
        claims = get_jwt()
        # print(current_user, claims)

        user_roles = claims["roles"]
        type_roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
        code = kwargs.get("code", "")
        type_roles = [x for x in type_roles if code in x["foreas"] or code in x["monades"]]

        if not type_roles:
            return Response(
                json.dumps({"error": f"Δεν επιτρέπεται η αλλαγή του φορέα {code}"}),
                mimetype="application/json",
                status=403,
            )

        return f(*args, **kwargs)

    return decorated_function
