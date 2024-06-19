#!venv/vin/python
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit

from src.models.psped.monada import Apografi, Monada
from pprint import pprint

i=0
for organization_unit in OrganizationalUnit.objects():
    i+=1
    print(i)
    organizational_unit_code = organization_unit.code
    # print(organizational_unit_code)
    supervisor_unit_code = organization_unit.supervisorUnitCode
    organization_code = organization_unit.organizationCode

    organization = Organization.objects(code=organization_code).first()
    organizational_unit = OrganizationalUnit.objects(code=organizational_unit_code).first()
    supervisor_unit = OrganizationalUnit.objects(code=supervisor_unit_code).first()

    apografi = Apografi(foreas=organization, monada=organizational_unit, proistamenh_monada=supervisor_unit)

    monada = Monada.objects(code=organizational_unit_code).first()
    if monada:
        monada.apografi = apografi
        monada.save(upsert=True)
        #print(monada.to_mongo().to_dict())
    else:
        monada = Monada(code=organizational_unit_code, apografi=apografi, remitsFinalized=False, provisionText=None)
        monada.save()

    # if organizational_unit_code == "800399":
    #     pprint(organization_unit.to_mongo().to_dict())
    # organization = Organization.objects(code=organization_unit.organizationCode).first()
    # monada = Monada(foreas=organization, monada=organization_unit)
    # Monada.objects(code=code).update_one(**monada.to_mongo(), upsert=True)
