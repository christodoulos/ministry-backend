import mongoengine as me
from src.models.psped.legal_act import LegalAct


class Abolition(me.EmbeddedDocument):
    abolishingLegalProvisionCode = me.StringField(required=True)
    entryDate = me.DateTimeField(required=True)
    userCode = me.StringField(required=True)


class LegalProvisionSpecs(me.EmbeddedDocument):
    meros = me.StringField()
    arthro = me.StringField()
    paragrafos = me.StringField()
    edafio = me.StringField()
    pararthma = me.StringField()

    def validate(self, clean=True):
        super(LegalProvisionSpecs, self).validate(clean)
        fields = [self.meros, self.arthro, self.paragrafos, self.edafio, self.pararthma]
        if not any(fields):
            raise me.ValidationError("LegalProvisionSpecs must have at least one field filled")


class LegalProvision(me.Document):
    meta = {
        "collection": "legal_provisions",
        "db_alias": "psped",
        "indexes": [{"fields": ["legalActKey", "legalProvisionSpecs"], "unique": True}],
    }

    legalActKey = me.StringField(required=True)
    legalActRef = me.ReferenceField(LegalAct, required=True)
    legalProvisionSpecs = me.EmbeddedDocumentField(LegalProvisionSpecs, required=True)
    abolition = me.EmbeddedDocumentField(Abolition)
