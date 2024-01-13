from src.apografi.constants import (
    APOGRAFI_DICTIONARIES_URL,
    APOGRAFI_DICTIONARIES,
    APOGRAFI_DICTIONARIES_SINGULAR,
)
from src.models.apografi import Dictionary
import requests


def lejiko_get(endpoint):
    url = f"{APOGRAFI_DICTIONARIES_URL}{endpoint}"
    print(url)
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()["data"]


def sync_dictionaries():
    print("Συγχρονισμός λεξικών από την Απογραφή...")
    for lejiko in APOGRAFI_DICTIONARIES.keys():
        for item in lejiko_get(lejiko):
            doc = {
                "code": APOGRAFI_DICTIONARIES_SINGULAR[lejiko],
                "code_el": APOGRAFI_DICTIONARIES[lejiko],
                "apografi_id": item["id"],
                "parentId": item["parentId"] if "parentId" in item else None,
                "description": item["description"],
            }
            try:
                Dictionary(**doc).save()
            except Exception as e:
                pass
    print("Τέλος συγχρονισμού λεξικών από την Απογραφή.")
