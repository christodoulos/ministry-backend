import json
import mongoengine as me
from src.models.apografi import Organization, OrganizationalUnit
from src.models.utils import JSONEncoder


class Foreas(Organization):
    meta = {"collection": "foreis", "db_alias": "psped"}

    code = me.StringField(required=True, unique=True)

    level = me.StringField(
        choices=["ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ", "ΜΗ ΟΡΙΣΜΕΝΟ"],
        default="MH ΟΡΙΣΜΕΝΟ",
    )

    def to_json(self):
        organization = Organization.objects.get(code=self.code).to_json_enchanced()
        data = {k: v for k, v in organization.items()}
        data["level"] = self.level
        return json.dumps(data, cls=JSONEncoder)
