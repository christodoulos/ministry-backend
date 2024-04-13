from flask import Blueprint, Response, request
from src.models.psped.log import PspedSystemLog as Log


log = Blueprint("log", __name__)


@log.route("/logout", methods=["POST"])
def logout():
    data = request.json
    Log(user_id=data["user_id"], action="logout", data={"email": data["email"]}).save()
    return Response(status=200)
