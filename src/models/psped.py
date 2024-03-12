import json
from datetime import datetime
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
        choices=[
            "ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ",
            "ΜΗ ΟΡΙΣΜΕΝΟ"
        ],
        default="MH ΟΡΙΣΜΕΝΟ",
    )
    apografi = me.EmbeddedDocumentField(Apografi, required=True)

    def to_json(self):
        organization = Organization.objects.get(
            code=self.code).to_json_enchanced()
        data = {k: v for k, v in organization.items()}
        data["level"] = self.level
        return json.dumps(data, cls=JSONEncoder)

    def to_json_enchanced(self):
        organization_id = self.apografi.foreas.id
        organizational_units_ids = [
            monada.id for monada in self.apografi.monades
        ]
        organization = Organization.objects.with_id(
            organization_id).to_json_enchanced()
        organizational_units = [
            OrganizationalUnit.objects.with_id(ou_id)
            for ou_id in organizational_units_ids
        ]

        data = {
            **json.loads(organization),
            "level":
            self.level,
            "monades": [{
                **json.loads(unit.to_json_enchanced())
            } for unit in organizational_units],
        }

        return json.dumps(data)


class Remit(me.Document):
    meta = {'collection': 'remits', 'db_alias': 'psped'} # TODO alias changed to apografi

    remitCode = me.StringField(required=True,
                               unique=True)
    remitText = me.StringField(required=True)
    remitType = me.StringField(
        required=True,
        choices=[
            'Επιτελική', 'Εκτελεστική', 'Υποστηρικτική', 'Ελεγκτική',
            'Παρακολούθηση αποτελεσματικής πολιτικής και αξιολόγηση αποτελεσμάτων'
        ])
    unitCode = me.StringField(required=True)
    COFOG_1stLevel = me.StringField(required=True)
    COFOG_2ndLevel = me.StringField(required=True)
    thematic_3rdLevel = me.StringField(required=True)
    status = me.StringField(required=True, choices=['Ενεργή', 'Ανενεργή'])
    legalProvisionsCodes = me.ListField(me.StringField(), required=True)
    creationDate = me.DateField(default=datetime.now)
    userCode = me.StringField(required=True)
    updateDate = me.DateField()

    @classmethod
    def generate_remit_code(cls):
        # Attempt to find the highest current remit code and increment it
        last_remit = cls.objects.order_by('-remitCode').first()
        if last_remit:
            last_number = int(
                last_remit.remitCode[1:]
            )  # Exclude the first character ('A') and convert to int
            new_number = last_number + 1
        else:
            new_number = 1  # Start from 1 if no remits exist
        return f'A{new_number:08d}'

    def save(self, *args, **kwargs):
        # if not self.creationDate:
        #     self.creationDate = datetime.now()
        self.updateDate = datetime.now()
        return super(Remit, self).save(*args, **kwargs)


class LegalProvision(me.Document):
    meta = {'collection': 'legal_provisions', 'db_alias': 'psped'}

    legalProvisionCode = me.StringField(required=True, unique=True)
    legalActCode = me.StringField(required=True)
    legalProvisionNumber = me.StringField(required=True)
    legalProvisionText = me.StringField(required=True)
    regulatedObjectCode = me.StringField(required=True)
    creationDate = me.DateTimeField(default=datetime.now)
    userCode = me.StringField(required=True)
    updateDate = me.DateTimeField()
    abolition = me.DictField()
    abolishingLegalProvisionCode = me.StringField()
    entryDate = me.DateTimeField()

    @classmethod
    def generate_legal_provision_code(cls):
        last_code = cls.objects.order_by('-legalProvisionCode').first()
        if last_code:
            last_number = int(last_code.legalProvisionCode[1:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f'P{new_number:09d}'


class LegalAct(me.Document):
    meta = {'collection': 'legal_acts', 'db_alias': 'psped'}

    legalActCode = me.StringField(required=True, unique=True)
    legalActType = me.StringField(required=True,
                                  choices=[
                                      'Νόμος', 'Προεδρικό Διάταγμα',
                                      'Κανονιστική Διοικητική Πράξη',
                                      'Απόφαση του οργάνου διοίκησης', 'Άλλο'
                                  ])
    legalActNumber = me.StringField(required=True)
    legalActDate = me.DateField(required=True)
    FEKref = me.DictField(required=True)
    DiavgeiaNumber = me.StringField()
    legalActFile = me.FileField()
    userCode = me.StringField(required=True)
    creationDate = me.DateTimeField(default=datetime.now)
    updateDate = me.DateTimeField()

    @classmethod
    def generate_legal_act_code(cls):
        last_code = cls.objects.order_by('-legalActCode').first()
        if last_code:
            last_number = int(last_code.legalActCode[1:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f'L{new_number:09d}'
