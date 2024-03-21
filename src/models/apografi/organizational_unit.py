import mongoengine as me
from src.models.apografi.embedded import Spatial, Address
from src.models.apografi.dictionary import Dictionary
from src.models.utils import JSONEncoder, Error
import json
import redis

r = redis.Redis()

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

    dict_cache = redis.Redis(db=1)

    @property
    def supervisorUnitCodeDetails(self):
        code = self.supervisorUnitCode
        return {
            "code": code,
            "description": OrganizationalUnit.objects(code=code).first().preferredLabel,
        }

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
                    "countryDescription": self.dict_cache.get(
                        f"Countries:{spatial.countryId}"
                    ).decode("utf-8")
                    if spatial.countryId is not None
                    else None,
                    "cityId": spatial.cityId,
                    # "cityDescription": Dictionary.objects(
                    #     code="Cities", apografi_id=spatial.cityId
                    # )
                    # .first()
                    # .description
                    "cityDescription": self.dict_cache.get(
                        f"Cities:{spatial.cityId}"
                    ).decode("utf-8")
                    if spatial.cityId is not None
                    else None,
                }.items()
                if value is not None
            }
            for spatial in self.spatial
        ]

    @property
    def unitTypeDetails(self):
        id = self.unitType
        return {
            "id": id,
            # "description": Dictionary.objects(code="UnitTypes", apografi_id=id)
            # .first()
            # .description,
            "description": self.dict_cache.get(f"UnitTypes:{id}").decode("utf-8"),
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
            if Dictionary.objects(code="Functions", apografi_id=id).first()
        ]

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
                    "description": self.dict_cache.get(f"Countries:{id1}").decode(
                        "utf-8"
                    ),
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
                    "description": self.dict_cache.get(
                        f"Countries:{address.adminUnitLevel1}"
                    ).decode("utf-8"),
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
                    "description": self.dict_cache.get(
                        f"Cities:{address.adminUnitLevel2}"
                    ).decode("utf-8"),
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
        if "supervisorUnitCode" in data:
            data.pop("supervisorUnitCode")
            data["supervisorUnit"] = self.supervisorUnitCodeDetails
        data["purpose"] = self.purposeDetails
        data["unitType"] = self.unitTypeDetails
        data["spatial"] = self.spatialDetails
        data["mainAddress"] = (
            {k: v for k, v in self.mainAddressDetails.items() if v}
            if self.mainAddressDetails
            else None
        )
        data["secondaryAddresses"] = self.secondaryAddressesDetails
        data = {k: v for k, v in data.items() if v}
        return json.dumps(data, cls=JSONEncoder)

    def clean(self):
        if self.purpose:
            not_in_dict = []

            for id in self.purpose:
                if not r.sismember("Functions", id):
                    not_in_dict.append(id)

            if len(not_in_dict):
                Error(
                    entity="organizational-unit",
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
                    entity="organizational-unit",
                    doc_id=self.code,
                    value={
                        "Unknown countries": country_not_in_dict,
                        "Unknown cities": city_not_in_dict,
                    },
                ).save()

        if not r.sismember("UnitTypes", self.unitType):
            Error(
                entity="organizational-unit",
                doc_id=self.code,
                value={"Unknown unitType": self.unitType},
            ).save()

        if self.mainAddress:
            adminUnitLevel1_not_in_dict = ""
            adminUnitLevel2_not_in_dict = ""

            if self.mainAddress.adminUnitLevel1:
                if not r.sismember(
                    "Countries",
                    str(self.mainAddress.adminUnitLevel1).encode("utf-8"),
                ):
                    adminUnitLevel1_not_in_dict = self.mainAddress.adminUnitLevel1
            if self.mainAddress.adminUnitLevel2:
                if not r.sismember(
                    "Cities",
                    str(self.mainAddress.adminUnitLevel2).encode("utf-8"),
                ):
                    adminUnitLevel2_not_in_dict = self.mainAddress.adminUnitLevel2

            if adminUnitLevel1_not_in_dict or adminUnitLevel2_not_in_dict:
                Error(
                    entity="organizational-unit",
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
                if address.adminUnitLevel2 and not r.sismember(
                    "Cities", str(address.adminUnitLevel2).encode("utf-8")
                ):
                    adminUnitLevel2_not_in_dict.append(address.adminUnitLevel2)

            if len(adminUnitLevel1_not_in_dict) or len(adminUnitLevel2_not_in_dict):
                Error(
                    entity="organizational-unit",
                    doc_id=self.code,
                    value={
                        "Unknown secondaryAddresses adminUnitLevel1": adminUnitLevel1_not_in_dict,
                        "Unknown secondaryAddresses adminUnitLevel2": adminUnitLevel2_not_in_dict,
                    },
                ).save()
