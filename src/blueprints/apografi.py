from flask import Blueprint, request, Response
import json

from src.models.apografi import Dictionary, Organization


apografi = Blueprint("apografi", __name__)

# Dictionary Routes


@apografi.route("/dictionary", methods=["POST"])
def post_dictionary():
    post_data = request.get_json()
    data = {
        "apografi_id": post_data["id"],
        "code": post_data["code"],
        "code_el": post_data["code_el"],
        "description": post_data["description"],
    }
    dictionary = Dictionary(**data)
    dictionary.save()
    return Response(json.dumps(data), mimetype="application/json")


@apografi.route("/dictionary/<string:dictionary>/<int:id>/description", methods=["GET"])
def get_dictionary_id(dictionary: str, id: int):
    try:
        doc = Dictionary.objects().get(code=dictionary, apografi_id=id)
        description = {"description": doc["description"]}
        return Response(
            json.dumps(description), mimetype="application/json", status=200
        )
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route( "/dictionary/<string:dictionary>/<string:description>/id", methods=["GET"] )  # fmt: skip
def get_dictionary_code(dictionary: str, description: str):
    try:
        doc = Dictionary.objects().get(code=dictionary, description=description)
        print(doc)
        id = {"id": doc["id"]}
        return Response(json.dumps(id), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route("/dictionary/<string:dictionary>", methods=["GET"])
def get_dictionary(dictionary: str):
    dictionary = Dictionary.objects(code=dictionary)
    return Response(dictionary.to_json(), mimetype="application/json", status=200)


@apografi.route("/dictionary/<string:dictionary>/ids", methods=["GET"])
def get_dictionary_ids(dictionary: str):
    docs = Dictionary.objects(code=dictionary)
    ids = [doc["id"] for doc in docs]
    return Response(json.dumps(ids), mimetype="application/json", status=200)


# Organization Routes


@apografi.route("/organization", methods=["GET"])
def get_organization():
    organization = Organization.objects()
    return Response(organization.to_json(), mimetype="application/json", status=200)


@apografi.route("/organization/<string:code>", methods=["GET"])
def get_organization_id(code: str):
    try:
        doc = Organization.objects().get(code=code)
        return Response(doc.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route("/organization/<string:label>/label", methods=["GET"])
def get_organization_label(label: str):
    try:
        doc = Organization.objects(preferredLabel__icontains=label)
        return Response(doc.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)
