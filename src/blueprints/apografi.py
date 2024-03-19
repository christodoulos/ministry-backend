from flask import Blueprint, Response
import json

from src.blueprints.utils import convert_greek_accented_chars
from src.models.apografi.dictionary import Dictionary
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit


apografi = Blueprint("apografi", __name__)

# Dictionary Routes


@apografi.route("/dictionary/<string:dictionary>/<int:id>/description")
def get_dictionary_id(dictionary: str, id: int):
    try:
        doc = Dictionary.objects().get(code=dictionary, apografi_id=id)
        description = {"description": doc["description"]}
        return Response(json.dumps(description), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route( "/dictionary/<string:dictionary>/<string:description>/id" )  # fmt: skip
def get_dictionary_code(dictionary: str, description: str):
    try:
        doc = Dictionary.objects().get(code=dictionary, description=description)
        print(doc)
        id = {"id": doc["apografi_id"]}
        return Response(json.dumps(id), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route("/dictionary/<string:dictionary>")
def get_dictionary(dictionary: str):
    dictionary = Dictionary.objects(code=dictionary).only("apografi_id", "description").exclude("id")
    return Response(dictionary.to_json(), mimetype="application/json", status=200)


@apografi.route("/dictionary/<string:dictionary>/ids")
def get_dictionary_ids(dictionary: str):
    docs = Dictionary.objects(code=dictionary)
    ids = [doc["apografi_id"] for doc in docs]
    return Response(json.dumps(ids), mimetype="application/json", status=200)


# Organization Routes


@apografi.route("/organization")
def get_organization():
    organization = Organization.objects().only("code", "preferredLabel").exclude("id")
    return Response(organization.to_json(), mimetype="application/json", status=200)


@apografi.route("/organization/<string:code>")
def get_organization_id(code: str):
    try:
        doc = Organization.objects().get(code=code)
        return Response(doc.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)

@apografi.route("/organization/<string:code>/enhanced")
def get_organization_enhanced(code: str):
    try:
        doc = Organization.objects().get(code=code)
        return Response(doc.to_json_enhanced(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)

@apografi.route("/organization/<string:label>/label")
def get_organization_label(label: str):
    try:
        doc = Organization.objects(preferredLabel__icontains=convert_greek_accented_chars(label))
        return Response(doc.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


# Organization Units Routes


@apografi.route("/organizationUnit")
def get_organization_unit():
    organization = OrganizationalUnit.objects().only("code", "preferredLabel").exclude("id")
    return Response(organization.to_json(), mimetype="application/json", status=200)


@apografi.route("/organization/<string:code>/units")
def get_organization_units(code: str):
    try:
        docs = OrganizationalUnit.objects(organizationCode=code)
        return Response(docs.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route("/organization/<string:code>/general-directorates")
def get_organization_general_directorates(code: str):
    try:
        docs = OrganizationalUnit.objects(organizationCode=code, unitType=3)
        return Response(docs.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route( "/organization/<string:code>/<string:gen_dir_code>/directorates" )  # fmt: skip
def get_organization_directorates(code: str, gen_dir_code: str):
    try:
        docs = OrganizationalUnit.objects(organizationCode=code, supervisorUnitCode=gen_dir_code)
        return Response(docs.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)


@apografi.route( "/organization/<string:code>/<string:dir_code>/departments", )  # fmt: skip
def get_organization_departments(code: str, dir_code: str):
    try:
        docs = OrganizationalUnit.objects(organizationCode=code, supervisorUnitCode=dir_code, unitType=2)
        return Response(docs.to_json(), mimetype="application/json", status=200)
    except Exception as e:
        error = {"error": str(e)}
        return Response(json.dumps(error), mimetype="application/json", status=404)
