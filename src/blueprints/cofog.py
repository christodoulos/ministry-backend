from flask import Blueprint, request, Response
from src.models.cofog import Cofog
import json

cofog = Blueprint("cofog", __name__)


@cofog.route("")
def get_cofog():
    try:
        cofog = Cofog.objects()
        return Response(cofog.to_json(), mimetype="application/json", status=200)
    except Cofog.DoesNotExist:
        return Response(
            json.dumps({"error": "Δεν βρέθηκαν δεδομένα COFOG"}),
            mimetype="application/json",
            status=404,
        )
