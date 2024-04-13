from src.models.apografi.organization import Organization
from src.models.apografi.embedded import Address, ContactPoint, FoundationFek, Spatial
from src.models.utils import SyncLogLog as Log
from src.apografi.utils import apografi_get
from src.apografi.constants import APOGRAFI_ORGANIZATIONS_URL
from deepdiff import DeepDiff
import requests


def sync_one_organization(organization_dict):
    doc = {k: v for k, v in organization_dict.items() if v}
    doc_id = doc["code"]

    for key, value in doc.items():
        if key in ["purpose", "alternativeLabels"]:
            value = sorted(value or [])
            doc[key] = value
        if key == "spatial":
            value = sorted(value or [], key=lambda x: (x.get("countryId", 0), x.get("cityId", 0)))
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
            Log(entity="organization", action="update", doc_id=doc_id, value=diff).save()
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
