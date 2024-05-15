import mongoengine as me
from src.models.psped.legal_act import LegalAct, FEK


class RegulatedObject(me.EmbeddedDocument):
    regulatedObjectType = me.StringField(required=True, choices=["organization", "organizationUnit", "remit"])
    regulatedObjectObjectId = me.StringField(required=True)


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

    regulatedObject = me.EmbeddedDocumentField(RegulatedObject)
    legalActKey = me.StringField(required=True)
    legalProvisionSpecs = me.EmbeddedDocumentField(LegalProvisionSpecs, required=True)
    legalProvisionText = me.StringField(required=True)
    abolition = me.EmbeddedDocumentField(Abolition)
    # The following fields are populated from LegalAct on save
    legalActType = me.StringField()
    legalActNumber = me.StringField()
    legalActTypeOther = me.StringField()
    legalActYear = me.StringField()
    ada = me.StringField()
    fek = me.EmbeddedDocumentField(FEK)

    def save(self, *args, **kwargs):
        legalActRef = LegalAct.objects.get(legalActKey=self.legalActKey)
        self.legalActType = legalActRef.legalActType
        self.legalActNumber = legalActRef.legalActNumber
        self.legalActTypeOther = legalActRef.legalActTypeOther
        self.legalActYear = legalActRef.legalActYear
        self.ada = legalActRef.ada
        self.fek = legalActRef.fek
        super(LegalProvision, self).save(*args, **kwargs)

    def to_dict(self):
        return self.to_mongo().to_dict()
