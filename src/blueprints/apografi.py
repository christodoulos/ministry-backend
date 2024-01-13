from flask import Blueprint, request, Response
import json

from src.models.apografi import Dictionary

apografi = Blueprint("apografi", __name__)


@apografi.route("/dictionary", methods=["POST"])
def post_lejiko():
    post_data = request.get_json()
    data = {
        "apografi_id": post_data["id"],
        "code": post_data["code"],
        "code_el": post_data["code_el"],
        "description": post_data["description"],
    }
    lejiko = Dictionary(**data)
    lejiko.save()
    return Response(json.dumps(data), mimetype="application/json")


@apografi.route("/dictionary/<string:dictionary>", methods=["GET"])
def get_dictionary(dictionary: str):
    lejika = Dictionary.objects(code=dictionary)
    return Response(lejika.to_json(), mimetype="application/json")


@apografi.route("/dictionary/<string:dictionary>/ids", methods=["GET"])
def get_dictionary_ids(dictionary: str):
    docs = Dictionary.objects(code=dictionary)
    ids = [doc["id"] for doc in docs]
    return Response(json.dumps(ids), mimetype="application/json")
