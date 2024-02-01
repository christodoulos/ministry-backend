import mongoengine as me
from src.models.apografi import Organization, OrganizationalUnit


class Foreas(me.Document):
    meta = {"collection": "foreis", "db_alias": "psped"}

    foreas_code = me.StringField(required=True, unique=True)
    level = me.StringField(
        choices=["ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ"]
    )

    def to_mongo_dict(self):
        mongo_dict = self.to_mongo().to_dict()
        mongo_dict.pop("_id")
        return mongo_dict
