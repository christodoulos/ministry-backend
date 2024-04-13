import mongoengine as me
from datetime import datetime


class Abolition(me.EmbeddedDocument):
    abolishingLegalProvisionCode = me.StringField(required=True)
    entryDate = me.DateTimeField(required=True)
    userCode = me.StringField(required=True)


class LegalProvisionCode(me.EmbeddedDocument):
    meros = me.StringField()
    arthro = me.StringField()
    paragrafos = me.StringField()
    edafio = me.StringField()
    pararthma = me.StringField()

    def validate(self, clean=True):
        super(LegalProvisionCode, self).validate(clean)
        fields = [self.meros, self.arthro, self.paragrafos, self.edafio, self.pararthma]
        if not any(fields):
            raise me.ValidationError("LegalProvisionCode")


class Diataxi(me.Document):
    meta = {"collection": "diataxeis", "db_alias": "psped"}

    legalProvisionCode = me.StringField(required=True, unique=True)
    legalActCode = me.StringField(required=True)
    legalProvisionNumber = me.StringField(required=True)
    legalProvisionText = me.StringField(required=True)
    regulatedObjectCode = me.EmbeddedDocumentField(LegalProvisionCode)
    creationDate = me.DateTimeField(default=datetime.now)
    userCode = me.StringField(required=True)
    updateDate = me.DateTimeField()
    abolition = me.EmbeddedDocumentField(Abolition)

    @classmethod
    def generate_diataxi_code(cls):
        last_code = cls.objects.order_by("-legalProvisionCode").first()
        if last_code:
            last_number = int(last_code.legalProvisionCode[1:])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"P{new_number:08d}"
