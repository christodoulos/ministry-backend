import json
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt

from src.models.psped import Foreas
from src.blueprints.decorators import can_edit

psped = Blueprint("psped", __name__)


@psped.route("/foreas/<string:code>")
def get_foreas(code: str):
    try:
        foreas = Foreas.objects.only("code", "level").exclude("id").get(code=code)
        return Response(
            # json.dumps(foreas.to_json()),
            foreas.to_json(),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


# @psped.route("/foreas/<string:code>", methods=["PUT"])
# @jwt_required()
# def update_poliepipedi(code: str):
#     current_user = get_jwt_identity()
#     claims = get_jwt()
#     print(current_user, claims)

#     user_roles = claims["roles"]
#     type_roles = [x for x in user_roles if x["role"] in ["EDITOR", "ADMIN", "ROOT"]]
#     type_roles = [x for x in type_roles if code in x["foreas"] or code in x["monades"]]

#     if type_roles:
#         try:
#             data = request.get_json()
#             foreas = Foreas.objects.get(code=data["code"])
#             foreas.update(**data)
#             return Response(
#                 json.dumps(foreas.to_json()),
#                 mimetype="application/json",
#                 status=200,
#             )
#         except Foreas.DoesNotExist:
#             return Response(
#                 json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
#                 mimetype="application/json",
#                 status=404,
#             )


#     else:
#         return Response(
#             json.dumps({"error": f"Δεν επιτρέπεται η αλλαγή του φορέα {code}"}),
#             mimetype="application/json",
#             status=403,
#         )
@psped.route("/foreas/<string:code>", methods=["PUT"])
@jwt_required()
@can_edit
def update_poliepipedi(code: str):
    try:
        data = request.get_json()
        foreas = Foreas.objects.get(code=data["code"])
        foreas.update(**data)
        return Response(
            json.dumps(foreas.to_json()),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )


@psped.route("/foreas/<string:code>/tree")
def get_foreas_tree(code: str):
    try:
        foreas = Foreas.objects.get(code=code)
        return Response(
            json.dumps(foreas.tree_to_json()),
            mimetype="application/json",
            status=200,
        )
    except Foreas.DoesNotExist:
        return Response(
            json.dumps({"error": f"Δεν βρέθηκε φορέας με κωδικό {code}"}),
            mimetype="application/json",
            status=404,
        )
