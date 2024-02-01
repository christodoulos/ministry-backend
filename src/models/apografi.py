import json
import mongoengine as me
from datetime import datetime
import redis
from .utils import JSONEncoder

r = redis.Redis()

# A model that logs changes during synchronization of dictionaries,organizations and organizational units


class Log(me.Document):
    meta = {"collection": "synclog", "db_alias": "apografi"}

    date = me.DateTimeField(default=datetime.now())
    entity = me.StringField(
        required=True, choices=["dictionary", "organization", "organizational-unit"]
    )
    action = me.StringField(required=True, choices=["insert", "update"])
    doc_id = me.StringField(required=True)
    value = me.DictField(required=True)


# A model for every dictionary from https://hr.apografi.gov.gr/api.html#genikes-plhrofories-le3ika


class Dictionary(me.Document):
    meta = {
        "collection": "dictionaries",
        "db_alias": "apografi",
        "indexes": [{"fields": ["apografi_id", "code", "description"], "unique": True}],
    }

    apografi_id = me.IntField(required=True)
    parentId = me.IntField()
    code = me.StringField(required=True)
    code_el = me.StringField(required=True)
    description = me.StringField(required=True)


# Embeddable documents for the Organization model


class Spatial(me.EmbeddedDocument):
    countryId = me.IntField()
    cityId = me.IntField()


class ContactPoint(me.EmbeddedDocument):
    email = me.EmailField()
    telephone = me.StringField()


class FoundationFek(me.EmbeddedDocument):
    year = me.IntField()
    number = me.StringField()
    issue = me.StringField()


class Address(me.EmbeddedDocument):
    fullAddress = me.StringField()
    postCode = me.StringField()
    adminUnitLevel1 = me.IntField()
    adminUnitLevel2 = me.IntField()


# A model for every organization from https://hr.apografi.gov.gr/api.html#genikes-plhrofories-foreis


class Organization(me.Document):
    meta = {
        "collection": "organizations",
        "db_alias": "apografi",
        "indexes": ["preferredLabel"],
    }

    code = me.StringField(required=True, unique=True)
    preferredLabel = me.StringField()
    alternativeLabels = me.ListField(me.StringField())
    purpose = me.ListField(me.IntField())
    spatial = me.ListField(me.EmbeddedDocumentField(Spatial))
    identifier = me.StringField()
    subOrganizationOf = me.StringField()
    organizationType = me.IntField()
    description = me.StringField()
    url = me.StringField()
    contactPoint = me.EmbeddedDocumentField(ContactPoint)
    vatId = me.StringField()
    status = me.StringField()
    foundationDate = me.DateTimeField()
    terminationDate = me.DateTimeField()
    mainDataUpdateDate = me.DateTimeField()
    organizationStructureUpdateDate = me.DateTimeField()
    foundationFek = me.EmbeddedDocumentField(FoundationFek)
    mainAddress = me.EmbeddedDocumentField(Address)
    secondaryAddresses = me.ListField(me.EmbeddedDocumentField(Address))

    def to_mongo_dict(self):
        mongo_dict = self.to_mongo().to_dict()
        mongo_dict.pop("_id")
        return mongo_dict

    @property
    def organizationTypeDetails(self):
        id = self.organizationType
        return {
            "id": id,
            "description": Dictionary.objects(code="OrganizationTypes", apografi_id=id)
            .first()
            .description,
        }

    @property
    def purposeDetails(self):
        ids = self.purpose
        return [
            {
                "id": id,
                "description": Dictionary.objects(code="Functions", apografi_id=id)
                .first()
                .description,
            }
            for id in ids
        ]

    @property
    def spatialDetails(self):
        return [
            {
                key: value
                for key, value in {
                    "countryId": spatial.countryId,
                    "countryDescription": Dictionary.objects(
                        code="Countries", apografi_id=spatial.countryId
                    )
                    .first()
                    .description
                    if spatial.countryId is not None
                    else None,
                    "cityId": spatial.cityId,
                    "cityDescription": Dictionary.objects(
                        code="Cities", apografi_id=spatial.cityId
                    )
                    .first()
                    .description
                    if spatial.cityId is not None
                    else None,
                }.items()
                if value is not None
            }
            for spatial in self.spatial
        ]

    @property
    def subOrganizationOfDetails(self):
        if not self.subOrganizationOf:
            return None
        else:
            id = self.subOrganizationOf
            return {
                "id": id,
                "description": Organization.objects(code=id).first().preferredLabel,
            }

    @property
    def mainAddressDetails(self):
        if not self.mainAddress:
            return None
        else:
            address = self.mainAddress

            try:
                id1 = self.mainAddress.adminUnitLevel1
            except AttributeError:
                id1 = None

            try:
                id2 = self.mainAddress.adminUnitLevel2
            except AttributeError:
                id2 = None

            adminUnitLevel1 = (
                {
                    "id": id1,
                    "description": Dictionary.objects(code="Countries", apografi_id=id1)
                    .first()
                    .description,
                }
                if id1 is not None
                else None
            )

            adminUnitLevel2 = (
                {
                    "id": id2,
                    "description": Dictionary.objects(code="Cities", apografi_id=id2)
                    .first()
                    .description,
                }
                if id2 is not None
                else None
            )

            return {
                "fullAddress": address.fullAddress,
                "postCode": address.postCode,
                "adminUnitLevel1": adminUnitLevel1,
                "adminUnitLevel2": adminUnitLevel2,
            }

    @property
    def secondaryAddressesDetails(self):
        addresses = self.secondaryAddresses
        return [
            {
                "fullAddress": address.fullAddress,
                "postCode": address.postCode,
                "adminUnitLevel1": {
                    "id": address.adminUnitLevel1,
                    "description": Dictionary.objects(
                        code="Countries", apografi_id=address.adminUnitLevel1
                    )
                    .first()
                    .description,
                }
                if address.adminUnitLevel1 is not None
                else None,
                "adminUnitLevel2": {
                    "id": address.adminUnitLevel2,
                    "description": Dictionary.objects(
                        code="Cities", apografi_id=address.adminUnitLevel2
                    )
                    .first()
                    .description,
                }
                if address.adminUnitLevel2 is not None
                else None,
            }
            for address in addresses
        ]

    def to_json(self):
        data = self.to_mongo().to_dict()
        data.pop("_id")
        data = {k: v for k, v in data.items() if v}
        return json.dumps(data, cls=JSONEncoder)

    def to_json_enchanced(self):
        data = self.to_mongo().to_dict()
        data.pop("_id")
        data["purpose"] = self.purposeDetails
        data["organizationType"] = self.organizationTypeDetails
        data["spatial"] = self.spatialDetails
        data["subOrganizationOf"] = self.subOrganizationOfDetails
        data["mainAddress"] = self.mainAddressDetails
        data["secondaryAddresses"] = self.secondaryAddressesDetails
        data = {k: v for k, v in data.items() if v}
        return json.dumps(data, cls=JSONEncoder)

    def clean(self):
        print(f"Checking organization {self.code} {self.preferredLabel}")

        if self.purpose:
            print("Checking purpose")
            for id in self.purpose:
                if not r.sismember("Functions", id):
                    raise me.ValidationError(f"Λάθος τιμή στο πεδίο purpose: {id}")

        if self.spatial:
            print("Checking spatial")
            for spatial in self.spatial:
                if (
                    hasattr(spatial, "countryId")
                    and spatial.cityId is not None
                    and not r.sismember("Countries", spatial.countryId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.countryId: {spatial.countryId}"
                    )
                if (
                    hasattr(spatial, "cityId")
                    and spatial.cityId is not None
                    and not r.sismember("Cities", spatial.cityId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.cityId: {spatial.cityId}"
                    )

        if not r.sismember("OrganizationTypes", self.organizationType):
            print("Checking organizationType")
            raise me.ValidationError(
                f"Λάθος τιμή στο πεδίο organizationType: {self.organizationType}"
            )

        if self.mainAddress:
            print("Checking mainAddress")

            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Countries",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {self.mainAddress.adminUnitLevel1}"
                    )

            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "Cities",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {self.mainAddress.adminUnitLevel2}"
                    )

        if self.secondaryAddresses:
            print("Checking secondaryAddresses")

            for address in self.secondaryAddresses:
                if address.adminUnitLevel1 and not r.sismember(
                    "Countries", str(address.adminUnitLevel1).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {address.adminUnitLevel1}"
                    )

                if address.adminUnitLevel2 and not r.sismember(
                    "Cities", str(address.adminUnitLevel2).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {address.adminUnitLevel2}"
                    )


# A model for every organizational unit from https://hr.apografi.gov.gr/api.html#genikes-plhrofories-monades


class OrganizationalUnit(me.Document):
    meta = {
        "collection": "organizational-units",
        "db_alias": "apografi",
        "indexes": ["organizationCode", "supervisorUnitCode", "preferredLabel"],
    }

    code = me.StringField(required=True, unique=True)
    organizationCode = me.StringField(required=True)
    supervisorUnitCode = me.StringField()
    preferredLabel = me.StringField()
    alternativeLabels = me.ListField(me.StringField())
    purpose = me.ListField(me.IntField())
    spatial = me.ListField(me.EmbeddedDocumentField(Spatial))
    identifier = me.StringField()
    unitType = me.IntField()
    description = me.StringField()
    email = me.EmailField()
    telephone = me.StringField()
    url = me.StringField()
    mainAddress = me.EmbeddedDocumentField(Address)
    secondaryAddresses = me.ListField(me.EmbeddedDocumentField(Address))

    def clean(self):
        if self.purpose:
            print("Checking purpose")
            print(self.purpose)
            for id in self.purpose:
                if not r.sismember("Functions", id):
                    print(
                        f"Λάθος τιμή στο πεδίο purpose: {id} στη μονάδα {self.code} {self.preferredLabel}"
                    )
                    self.purpose.remove(id)
                    print(self.purpose)

        if self.spatial:
            print("Checking spatial")

            for spatial in self.spatial:
                if (
                    hasattr(spatial, "countryId")
                    and spatial.cityId is not None
                    and not r.sismember("Countries", spatial.countryId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.countryId: {spatial.countryId}"
                    )

                if (
                    hasattr(spatial, "cityId")
                    and spatial.cityId is not None
                    and not r.sismember("Cities", spatial.cityId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.cityId: {spatial.cityId}"
                    )

        if not r.sismember("UnitTypes", self.unitType):
            print("Checking unitType")
            raise me.ValidationError(f"Λάθος τιμή στο πεδίο unitType: {self.unitType}")

        if self.mainAddress:
            print("Checking mainAddress")
            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Countries",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {self.mainAddress.adminUnitLevel1}"
                    )
            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "Cities",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {self.mainAddress.adminUnitLevel2}"
                    )

        if self.secondaryAddresses:
            print("Checking secondaryAddresses")
            for address in self.secondaryAddresses:
                if address.adminUnitLevel1 and not r.sismember(
                    "Countries", str(address.adminUnitLevel1).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {address.adminUnitLevel1}"
                    )
                if address.adminUnitLevel2 and not r.sismember(
                    "Cities", str(address.adminUnitLevel2).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {address.adminUnitLevel2}"
                    )
