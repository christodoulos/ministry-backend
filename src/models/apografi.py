from src import db, r
import mongoengine as me


class Dictionary(db.Document):
    apografi_id = me.IntField(required=True, db_field="id")
    parentId = me.IntField()
    code = me.StringField(required=True)
    code_el = me.StringField(required=True)
    description = me.StringField(required=True)

    meta = {
        "collection": "dictionaries",
        "db_alias": "apografi",
        "indexes": [{"fields": ["apografi_id", "code", "description"], "unique": True}],
    }


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


class Organization(db.Document):
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

    meta = {
        "collection": "organizations",
        "db_alias": "apografi",
    }
