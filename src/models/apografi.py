import mongoengine as me
from datetime import datetime
import redis

r = redis.Redis()

# A model that logs changes during synchronization of dictionaries,organizations and organizational units


class Log(me.Document):
    meta = {
        "collection": "synclog",
        "db_alias": "apografi",
    }

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
    url = me.URLField()
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

    def clean(self):
        if self.url and not self.url.startswith("http"):
            self.url = "http://" + self.url
        if self.purpose:
            for id in self.purpose:
                if not r.sismember("Function", id):
                    raise me.ValidationError(f"Λάθος τιμή στο πεδίο purpose: {id}")
        if self.spatial:
            for spatial in self.spatial:
                if not r.sismember("Country", spatial.countryId):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.countryId: {spatial.countryId}"
                    )
                if not r.sismember("City", spatial.cityId):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.cityId: {spatial.cityId}"
                    )
        if not r.sismember("OrganizationType", self.organizationType):
            raise me.ValidationError(
                f"Λάθος τιμή στο πεδίο organizationType: {self.organizationType}"
            )
        if self.mainAddress:
            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Country",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {self.mainAddress.adminUnitLevel1}"
                    )
            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "City",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {self.mainAddress.adminUnitLevel2}"
                    )
        if self.secondaryAddresses:
            for address in self.secondaryAddresses:
                if address.adminUnitLevel1 and not r.sismember(
                    "Country", str(address.adminUnitLevel1).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {address.adminUnitLevel1}"
                    )
                if address.adminUnitLevel2 and not r.sismember(
                    "City", str(address.adminUnitLevel2).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {address.adminUnitLevel2}"
                    )


# A model for every organizational unit from https://hr.apografi.gov.gr/api.html#genikes-plhrofories-monades


class OrganizationalUnit(me.Document):
    meta = {
        "collection": "organizationalUnits",
        "db_alias": "apografi",
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
    url = me.URLField()
    mainAddress = me.EmbeddedDocumentField(Address)
    secondaryAddresses = me.ListField(me.EmbeddedDocumentField(Address))

    def clean(self):
        if self.url and not self.url.startswith("http"):
            print("Checking url")
            self.url = "http://" + self.url
        if self.purpose:
            print("Checking purpose")
            print(self.purpose)
            for id in self.purpose:
                if not r.sismember("Function", id):
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
                    and not r.sismember("Country", spatial.countryId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.countryId: {spatial.countryId}"
                    )
                if (
                    hasattr(spatial, "cityId")
                    and spatial.cityId is not None
                    and not r.sismember("City", spatial.cityId)
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο spatial.cityId: {spatial.cityId}"
                    )
        if self.mainAddress:
            print("Checking mainAddress")
            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Country",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {self.mainAddress.adminUnitLevel1}"
                    )
            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "City",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {self.mainAddress.adminUnitLevel2}"
                    )
        if self.secondaryAddresses:
            print("Checking secondaryAddresses")
            for address in self.secondaryAddresses:
                if address.adminUnitLevel1 and not r.sismember(
                    "Country", str(address.adminUnitLevel1).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel1: {address.adminUnitLevel1}"
                    )
                if address.adminUnitLevel2 and not r.sismember(
                    "City", str(address.adminUnitLevel2).encode("utf-8")
                ):
                    raise me.ValidationError(
                        f"Λάθος τιμή στο πεδίο address.adminUnitLevel2: {address.adminUnitLevel2}"
                    )
