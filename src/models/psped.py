import json
import mongoengine as me
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.utils import JSONEncoder


class Apografi(me.EmbeddedDocument):
    foreas = me.ReferenceField(Organization)
    monades = me.ListField(me.ReferenceField(OrganizationalUnit))


class Foreas(me.Document):
    meta = {"collection": "foreis", "db_alias": "psped"}

    code = me.StringField(required=True, unique=True)
    level = me.StringField(
        choices=["ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ", "ΜΗ ΟΡΙΣΜΕΝΟ"],
        default="MH ΟΡΙΣΜΕΝΟ",
    )
    apografi = me.EmbeddedDocumentField(Apografi, required=True)

    def to_json(self):
        organization = Organization.objects.get(code=self.code).to_json_enchanced()
        data = {k: v for k, v in organization.items()}
        data["level"] = self.level
        return json.dumps(data, cls=JSONEncoder)

    def to_json_enchanced(self):
        organization_id = self.apografi.foreas.id
        organizational_units_ids = [monada.id for monada in self.apografi.monades]
        organization = Organization.objects.with_id(organization_id).to_json_enchanced()
        organizational_units = [
            OrganizationalUnit.objects.with_id(ou_id)
            for ou_id in organizational_units_ids
        ]

        data = {
            **json.loads(organization),
            "level": self.level,
            "monades": [
                {**json.loads(unit.to_json_enchanced())}
                for unit in organizational_units
            ],
        }

        return json.dumps(data)
