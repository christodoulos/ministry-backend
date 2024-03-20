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
