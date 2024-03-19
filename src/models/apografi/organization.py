import json
import mongoengine as me
from src.models.apografi.embedded import Spatial, ContactPoint, FoundationFek, Address
from src.models.apografi.dictionary import Dictionary
import redis

from src.models.utils import JSONEncoder, Error


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

    dict_cache = redis.Redis(db=1)

    def to_mongo_dict(self):
        mongo_dict = self.to_mongo().to_dict()
        mongo_dict.pop("_id")
        return mongo_dict

    @property
    def organizationTypeDetails(self):
        id = self.organizationType
        return {
            "id": id,
            # "description": Dictionary.objects(code="OrganizationTypes", apografi_id=id)
            # .first()
            # .description,
            "description": self.dict_cache.get(f"OrganizationTypes:{id}").decode("utf-8"),
        }

    @property
    def purposeDetails(self):
        ids = self.purpose
        return [
            {
                "id": id,
                # "description": Dictionary.objects(code="Functions", apografi_id=id)
                # .first()
                # .description,
                "description": self.dict_cache.get(f"Functions:{id}").decode("utf-8"),
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
                    # "countryDescription": Dictionary.objects(
                    #     code="Countries", apografi_id=spatial.countryId
                    # )
                    # .first()
                    # .description
                    "countryDescription": self.dict_cache.get(f"Countries:{spatial.countryId}").decode("utf-8")
                    if spatial.countryId is not None
                    else None,
                    "cityId": spatial.cityId,
                    # "cityDescription": Dictionary.objects(
                    #     code="Cities", apografi_id=spatial.cityId
                    # )
                    # .first()
                    # .description
                    "cityDescription": self.dict_cache.get(f"Cities:{spatial.cityId}").decode("utf-8")
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
                    # "description": Dictionary.objects(code="Countries", apografi_id=id1)
                    # .first()
                    # .description,
                    "description": self.dict_cache.get(f"Countries:{id1}").decode("utf-8"),
                }
                if id1 is not None
                else None
            )

            adminUnitLevel2 = (
                {
                    "id": id2,
                    # "description": Dictionary.objects(code="Cities", apografi_id=id2)
                    # .first()
                    # .description,
                    "description": self.dict_cache.get(f"Cities:{id2}").decode("utf-8"),
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
                    # "description": Dictionary.objects(
                    #     code="Countries", apografi_id=address.adminUnitLevel1
                    # )
                    # .first()
                    # .description,
                    "description": self.dict_cache.get(f"Countries:{address.adminUnitLevel1}").decode("utf-8"),
                }
                if address.adminUnitLevel1 is not None
                else None,
                "adminUnitLevel2": {
                    "id": address.adminUnitLevel2,
                    # "description": Dictionary.objects(
                    #     code="Cities", apografi_id=address.adminUnitLevel2
                    # )
                    # .first()
                    # .description,
                    "description": self.dict_cache.get(f"Cities:{address.adminUnitLevel2}").decode("utf-8"),
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

    def to_json_enhanced(self):
        data = self.to_mongo().to_dict()
        data.pop("_id")
        data["purpose"] = self.purposeDetails
        data["organizationType"] = self.organizationTypeDetails
        data["spatial"] = self.spatialDetails
        data["subOrganizationOf"] = self.subOrganizationOfDetails
        data["mainAddress"] = {k: v for k, v in self.mainAddressDetails.items() if v} if self.mainAddress else None
        data["secondaryAddresses"] = self.secondaryAddressesDetails
        data = {k: v for k, v in data.items() if v}
        return json.dumps(data, cls=JSONEncoder)

    def clean(self):
        r = redis.Redis(db=0)
        if self.purpose:
            not_in_dict = []

            for id in self.purpose:
                if not r.sismember("Functions", id):
                    not_in_dict.append(id)

            if len(not_in_dict):
                Error(
                    entity="organization",
                    doc_id=self.code,
                    value={"Unknown purposes": not_in_dict},
                ).save()

        if self.spatial:
            city_not_in_dict = []
            country_not_in_dict = []

            for spatial in self.spatial:
                if (
                    hasattr(spatial, "countryId")
                    and spatial.cityId is not None
                    and not r.sismember("Countries", spatial.countryId)
                ):
                    country_not_in_dict.append(spatial.countryId)
                if (
                    hasattr(spatial, "cityId")
                    and spatial.cityId is not None
                    and not r.sismember("Cities", spatial.cityId)
                ):
                    city_not_in_dict.append(spatial.cityId)

            if len(country_not_in_dict) or len(city_not_in_dict):
                Error(
                    entity="organization",
                    doc_id=self.code,
                    value={
                        "Unknown countries": country_not_in_dict,
                        "Unknown cities": city_not_in_dict,
                    },
                ).save()

        if not r.sismember("OrganizationTypes", self.organizationType):
            Error(
                entity="organization",
                doc_id=self.code,
                value={"Unknown organizationType": self.organizationType},
            ).save()

        if self.mainAddress:
            adminUnitLevel1_not_in_dict = ""
            adminUnitLevel2_not_in_dict = ""

            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Countries",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    adminUnitLevel1_not_in_dict = self.mainAddress.adminUnitLevel

            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "Cities",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    adminUnitLevel2_not_in_dict = self.mainAddress.adminUnitLevel2

            if adminUnitLevel1_not_in_dict or adminUnitLevel2_not_in_dict:
                Error(
                    entity="organization",
                    doc_id=self.code,
                    value={
                        "Unknown mainAddress adminUnitLevel1": adminUnitLevel1_not_in_dict,
                        "Unknown mainAddress adminUnitLevel2": adminUnitLevel2_not_in_dict,
                    },
                ).save()

        if self.secondaryAddresses:
            adminUnitLevel1_not_in_dict = []
            adminUnitLevel2_not_in_dict = []

            for address in self.secondaryAddresses:
                if address.adminUnitLevel1 and not r.sismember(
                    "Countries", str(address.adminUnitLevel1).encode("utf-8")
                ):
                    adminUnitLevel1_not_in_dict.append(address.adminUnitLevel1)

                if address.adminUnitLevel2 and not r.sismember("Cities", str(address.adminUnitLevel2).encode("utf-8")):
                    adminUnitLevel2_not_in_dict.append(address.adminUnitLevel2)

            if len(adminUnitLevel1_not_in_dict) or len(adminUnitLevel2_not_in_dict):
                Error(
                    entity="organization",
                    doc_id=self.code,
                    value={
                        "Unknown secondaryAddresses adminUnitLevel1": adminUnitLevel1_not_in_dict,
                        "Unknown secondaryAddresses adminUnitLevel2": adminUnitLevel2_not_in_dict,
                    },
                ).save()
