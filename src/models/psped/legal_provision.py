import mongoengine as me
from src.models.psped.change import Change


class RegulatedObjectCode(me.EmbeddedDocument):
    foreas = me.StringField(required=True)
    monada = me.StringField(required=True)


class Abolition(me.EmbeddedDocument):
    abolishingLegalProvisionCode = me.StringField(required=True)
    entryDate = me.DateTimeField(required=True)
    userCode = me.StringField(required=True)


class LegalProvisionFields(me.EmbeddedDocument):
    meros = me.StringField()
    arthro = me.StringField()
    paragrafos = me.StringField()
    edafio = me.StringField()
    pararthma = me.StringField()

    def validate(self, clean=True):
        super(LegalProvisionFields, self).validate(clean)
        fields = [self.meros, self.arthro, self.paragrafos, self.edafio, self.pararthma]
        if not any(fields):
            raise me.ValidationError("LegalProvisionFields must have at least one field filled")


class LegalProvision(me.Document):
    meta = {
        "collection": "diataxeis",
        "db_alias": "psped",
        "indexes": [{"fields": ["regulatedObject", "legalAct", "legalProvision"], "unique": True}],
    }

    regulatedObject = me.EmbeddedDocumentField(RegulatedObjectCode, required=True)
    legalAct = me.StringField(required=True)
    legalProvision = me.EmbeddedDocumentField(LegalProvisionFields, required=True)
    changes = me.EmbeddedDocumentListField(Change, default=[])
    abolition = me.EmbeddedDocumentField(Abolition)
