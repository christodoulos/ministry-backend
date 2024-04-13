from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.apografi.embedded import Address, Spatial
from src.models.utils import SyncLog as Log
from src.apografi.utils import apografi_get
from src.apografi.constants import APOGRAFI_ORGANIZATIONAL_UNITS_URL
from deepdiff import DeepDiff


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
            Log(entity="organizational-unit", action="insert", doc_id=doc_id, value=doc).save()


def sync_organizational_units():
    print("Συγχρονισμός οργανωτικών μονάδων από την Απογραφή...")
    for organization in Organization.objects():
        print(f"{organization['code']} {organization['preferredLabel']}\n")
        response = apografi_get(f"{APOGRAFI_ORGANIZATIONAL_UNITS_URL}{organization['code']}")

        if response.status_code != 404:
            units = response.json()["data"]
            sync_one_organization_units(units)

    print("Τέλος συγχρονισμού οργανωτικών μονάδων από την Απογραφή.")
