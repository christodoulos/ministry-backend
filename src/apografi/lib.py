from src.apografi.constants import (
    APOGRAFI_DICTIONARIES_URL,
    APOGRAFI_DICTIONARIES,
    APOGRAFI_DICTIONARIES_SINGULAR,
    APOGRAFI_ORGANIZATIONS_URL,
)
from src.models.apografi import Dictionary, Organization
import requests
import redis

r = redis.Redis()


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
