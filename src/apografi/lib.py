import sys
from src.apografi.constants import (
    APOGRAFI_DICTIONARIES_URL,
    APOGRAFI_DICTIONARIES,
    APOGRAFI_ORGANIZATIONS_URL,
    APOGRAFI_ORGANIZATIONAL_UNITS_URL,
)
from src.models.apografi import (
    Log,
    Dictionary,
    Organization,
    OrganizationalUnit,
    Address,
    Spatial,
    ContactPoint,
    FoundationFek,
)
import requests
from requests.adapters import HTTPAdapter, Retry
import redis
import mongoengine as me
from deepdiff import DeepDiff


def apografi_dictionary_get(endpoint):
    url = f"{APOGRAFI_DICTIONARIES_URL}{endpoint}"
    print(url)
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()["data"]


def apografi_get(URL):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount(URL, HTTPAdapter(max_retries=retries))
    headers = {"Accept": "application/json"}
    return session.get(URL, headers=headers)


def sync_apografi_dictionaries():
    print("Συγχρονισμός λεξικών από την Απογραφή...")

    for dictionary in APOGRAFI_DICTIONARIES.keys():
        for item in apografi_dictionary_get(dictionary):
            doc = {
                "code": dictionary,
                "code_el": APOGRAFI_DICTIONARIES[dictionary],
                "apografi_id": item["id"],
                "description": item["description"],
            }
            if "parentId" in item:
                doc["parentId"] = item["parentId"]
            doc_id = f"{dictionary}:{item['id']}:{item['description']}"

            existing = Dictionary.objects(
                code=dictionary,
                apografi_id=item["id"],
                description=item["description"],
            ).first()

            if existing:
                existing_dict = existing.to_mongo().to_dict()
                existing_dict.pop("_id")
                diff = DeepDiff(
                    existing_dict,
                    doc,
                )
                if diff:
                    for key, value in doc.items():
                        setattr(existing, key, value)
                    existing.save()
                    Log(
                        entity="dictionary", action="update", doc_id=doc_id, value=diff
                    ).save()
            else:
                Dictionary(**doc).save()
                Log(
                    entity="dictionary", action="insert", doc_id=doc_id, value=doc
                ).save()

    print("Τέλος συγχρονισμού λεξικών από την Απογραφή.")


def cache_dictionaries():
    r = redis.Redis()
    print("Καταχώρηση λεξικών στην cache...")
    for dictionary in APOGRAFI_DICTIONARIES.keys():
        r.delete(dictionary)
        docs = Dictionary.objects(code=dictionary)
        ids = set([doc["apografi_id"] for doc in docs])
        print(ids)
        r.sadd(dictionary, *ids)
    print("Τέλος καταχώρησης λεξικών στην cache.")


def sync_one_organization(organization_dict):
    doc = {k: v for k, v in organization_dict.items() if v}
    doc_id = doc["code"]

    for key, value in doc.items():
        if key in ["purpose", "alternativeLabels"]:
            value = sorted(value or [])
            doc[key] = value
        if key == "spatial":
            value = sorted(
                value or [], key=lambda x: (x.get("countryId", 0), x.get("cityId", 0))
            )
            value = [Spatial(**item) for item in value]
            doc[key] = value
        if key == "contactPoint":
            value = ContactPoint(**value)
            doc[key] = value
        if key == "foundationFek":
            value = FoundationFek(**value)
            doc[key] = value
        if key in ["mainAddress", "secondaryAddresses"]:
            if isinstance(value, list):
                value = sorted(
                    value or [],
                    key=lambda x: (
                        x.get("fullAddress", ""),
                        x.get("postCode", ""),
                        x.get("adminUnitLevel1", 0),
                        x.get("adminUnitLevel2", 0),
                    ),
                )
                value = [Address(**item) for item in value]
            else:
                value = Address(**value)
            doc[key] = value

    existing = Organization.objects(code=doc["code"]).first()

    if existing:
        existing_dict = existing.to_mongo().to_dict()
        existing_dict.pop("_id")
        new_doc = Organization(**doc).to_mongo().to_dict()
        diff = DeepDiff(existing_dict, new_doc)
        if diff:
            for key, value in doc.items():
                setattr(existing, key, value)
            existing.save()
            Log(
                entity="organization", action="update", doc_id=doc_id, value=diff
            ).save()
    else:
        Organization(**doc).save()
        Log(entity="organization", action="insert", doc_id=doc_id, value=doc).save()


def sync_organizations():
    print("Συγχρονισμός φορέων από την Απογραφή...")

    headers = {"Accept": "application/json"}
    response = requests.get(APOGRAFI_ORGANIZATIONS_URL, headers=headers)
    for item in response.json()["data"]:
        organization_code = item["code"]

        response = apografi_get(f"{APOGRAFI_ORGANIZATIONS_URL}/{organization_code}")
        organization = response.json()["data"]

        sync_one_organization(organization)

    print("Τέλος συγχρονισμού φορέων από την Απογραφή.")


def sync_one_organization_units(units):
    for unit in units:
        doc = {k: v for k, v in unit.items() if v}
        doc_id = doc["code"]

        for key, value in doc.items():
            if key in ["purpose", "alternativeLabels"]:
                value = sorted(value or [])
                doc[key] = value
            if key == "spatial":
                value = sorted(
                    value or [],
                    key=lambda x: (x.get("countryId", 0), x.get("cityId", 0)),
                )
                value = [Spatial(**item) for item in value]
                doc[key] = value
            if key in ["mainAddress", "secondaryAddresses"]:
                if isinstance(value, list):
                    value = sorted(
                        value or [],
                        key=lambda x: (
                            x.get("fullAddress", ""),
                            x.get("postCode", ""),
                            x.get("adminUnitLevel1", 0),
                            x.get("adminUnitLevel2", 0),
                        ),
                    )
                    value = [Address(**item) for item in value]
                else:
                    value = Address(**value)
                doc[key] = value

        existing = OrganizationalUnit.objects(code=doc["code"]).first()
        if existing:
            existing_dict = existing.to_mongo().to_dict()
            existing_dict.pop("_id")
            new_doc = OrganizationalUnit(**doc).to_mongo().to_dict()
            diff = DeepDiff(existing_dict, new_doc)
            if diff:
                for key, value in doc.items():
                    setattr(existing, key, value)
                existing.save()
                Log(
                    entity="organizational-unit",
                    action="update",
                    doc_id=doc_id,
                    value=diff,
                ).save()
        else:
            OrganizationalUnit(**doc).save()
            Log(
                entity="organizational-unit", action="insert", doc_id=doc_id, value=doc
            ).save()


def sync_organizational_units():
    print("Συγχρονισμός οργανωτικών μονάδων από την Απογραφή...")
    headers = {"Accept": "application/json"}
    for organization in Organization.objects():
        print(f"{organization['code']} {organization['preferredLabel']}\n")
        response = apografi_get(
            f"{APOGRAFI_ORGANIZATIONAL_UNITS_URL}{organization['code']}"
        )

        if response.status_code != 404:
            units = response.json()["data"]
            sync_one_organization_units(units)

    print("Τέλος συγχρονισμού οργανωτικών μονάδων από την Απογραφή.")
