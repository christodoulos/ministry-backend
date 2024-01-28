from src.apografi.constants import (
    APOGRAFI_DICTIONARIES_URL,
    APOGRAFI_DICTIONARIES,
    APOGRAFI_DICTIONARIES_SINGULAR,
    APOGRAFI_ORGANIZATIONS_URL,
    APOGRAFI_ORGANIZATIONAL_UNITS_URL,
    APOGRAFI_ORGANIZATION_TREE_URL,
)
from src.models.apografi import (
    Dictionary,
    Organization,
    OrganizationalUnit,
    Address,
    Spatial,
)
import requests
import redis
import mongoengine as me


def apografi_dictionary_get(endpoint):
    url = f"{APOGRAFI_DICTIONARIES_URL}{endpoint}"
    print(url)
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()["data"]


def sync_apografi_dictionaries():
    print("Συγχρονισμός λεξικών από την Απογραφή...")
    for dictionary in APOGRAFI_DICTIONARIES.keys():
        for item in apografi_dictionary_get(dictionary):
            doc = {
                "code": APOGRAFI_DICTIONARIES_SINGULAR[dictionary],
                "code_el": APOGRAFI_DICTIONARIES[dictionary],
                "apografi_id": item["id"],
                "parentId": item["parentId"] if "parentId" in item else None,
                "description": item["description"],
            }
            try:
                Dictionary(**doc).save()
            except Exception as e:
                pass
    print("Τέλος συγχρονισμού λεξικών από την Απογραφή.")


def cache_dictionaries():
    r = redis.Redis()
    print("Καταχώρηση λεξικών στην μνήμη...")
    for dictionary in APOGRAFI_DICTIONARIES_SINGULAR.values():
        r.delete(dictionary)
        docs = Dictionary.objects(code=dictionary)
        ids = set([doc["id"] for doc in docs])
        r.sadd(dictionary, *ids)
    print("Τέλος καταχώρησης λεξικών στην μνήμη.")


def sync_organizations():
    print("Συγχρονισμός φορέων από την Απογραφή...")
    headers = {"Accept": "application/json"}
    response = requests.get(APOGRAFI_ORGANIZATIONS_URL, headers=headers)
    for item in response.json()["data"]:
        organization_code = item["code"]

        response = requests.get(
            f"{APOGRAFI_ORGANIZATIONS_URL}/{organization_code}", headers=headers
        )
        organization = response.json()["data"]

        doc = {k: v for k, v in organization.items() if v}
        print(doc["code"])

        try:
            Organization(**doc).save()
        except Exception as e:
            pass
    print("Τέλος συγχρονισμού φορέων από την Απογραφή.")


def sync_organization_units(organization_code):
    print(
        f"Συγχρονισμός οργανωτικών μονάδων του φορέα {organization_code} από την Απογραφή..."
    )
    headers = {"Accept": "application/json"}
    response = requests.get(
        f"{APOGRAFI_ORGANIZATIONAL_UNITS_URL}{organization_code}", headers=headers
    )

    print(len(response.json()))
    print(len(response.json()["data"]))
    for unit in response.json()["data"]:
        print(unit["code"])
        doc = {k: v for k, v in unit.items() if v}

        for key, value in doc.items():
            if key in ["mainAddress", "secondaryAddresses"]:
                # If the key is 'mainAddress' or 'secondaryAddresses',
                # we need to create Address instances
                if isinstance(value, list):
                    value = [Address(**item) for item in value]
                else:
                    value = Address(**value)
                doc[key] = value
            if key in ["spatial"]:
                print("VALUE", value)
                # If the key is 'spatial',
                # we need to create Spatial instances
                if isinstance(value, list):
                    value = [Spatial(**item) for item in value]
                else:
                    value = Spatial(**value)
                doc[key] = value

        existing = OrganizationalUnit.objects(code=doc["code"]).first()
        if existing:
            for key, value in doc.items():
                setattr(existing, key, value)
            try:
                existing.save()
            except me.ValidationError as e:
                print(e.to_dict())
        else:
            try:
                OrganizationalUnit(**doc).save()
            except me.ValidationError as e:
                print(e.to_dict())


def sync_organizational_units():
    print("Συγχρονισμός οργανωτικών μονάδων από την Απογραφή...")
    headers = {"Accept": "application/json"}
    for organization in Organization.objects():
        print(f"{organization['code']} {organization['preferredLabel']}\n")
        response = requests.get(
            f"{APOGRAFI_ORGANIZATIONAL_UNITS_URL}{organization['code']}",
            headers=headers,
        )

        if response.status_code != 404 and hasattr(response.json(), "data"):
            units = response.json()["data"]

            for unit in units:
                print(f"\t{unit['code']} {unit['preferredLabel']}\n")

                doc = {k: v for k, v in unit.items() if v}

                for key, value in doc.items():
                    if key in ["mainAddress", "secondaryAddresses"]:
                        # If the key is 'mainAddress' or 'secondaryAddresses',
                        # we need to create Address instances
                        if isinstance(value, list):
                            value = [Address(**item) for item in value]
                        else:
                            value = Address(**value)
                        doc[key] = value
                    if key in ["spatial"]:
                        # If the key is 'spatial',
                        # we need to create Spatial instances
                        if isinstance(value, list):
                            value = [Spatial(**item) for item in value]
                        else:
                            value = Spatial(**value)
                        doc[key] = value

                existing = OrganizationalUnit.objects(code=doc["code"]).first()
                if existing:
                    for key, value in doc.items():
                        setattr(existing, key, value)
                    try:
                        existing.save()
                    except me.ValidationError as e:
                        print(e.to_dict())
                else:
                    try:
                        OrganizationalUnit(**doc).save()
                    except me.ValidationError as e:
                        print(e.to_dict())
    print("Τέλος συγχρονισμού οργανωτικών μονάδων από την Απογραφή.")
