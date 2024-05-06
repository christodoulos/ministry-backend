import json
import mongoengine as me
from src.models.psped.legal_act import LegalAct, FEK


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
    legalProvisionSpecs = me.EmbeddedDocumentField(LegalProvisionSpecs, required=True)
    legalProvisionText = me.StringField(required=True)
    legalActType = me.StringField()
    legalActNumber = me.StringField()
    legalActTypeOther = me.StringField()
    legalActYear = me.StringField()
    ada = me.StringField()
    fek = me.EmbeddedDocumentField(FEK)
    abolition = me.EmbeddedDocumentField(Abolition)

    def save(self, *args, **kwargs):
        legalActRef = LegalAct.objects.get(legalActKey=self.legalActKey)
        self.fek = legalActRef.fek
        self.legalActType = legalActRef.legalActType
        self.legalActNumber = legalActRef.legalActNumber
        self.legalActTypeOther = legalActRef.legalActTypeOther
        self.legalActNumber = legalActRef.legalActNumber
        self.legalActYear = legalActRef.legalActYear
        self.ada = legalActRef.ada
        super(LegalProvision, self).save(*args, **kwargs)
