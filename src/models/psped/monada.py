import mongoengine as me
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit


class Apografi(me.EmbeddedDocument):
    foreas = me.ReferenceField(Organization)
    monada = me.ReferenceField(OrganizationalUnit)
    proistamenh_monada = me.ReferenceField(OrganizationalUnit)


class Monada(me.Document):
    meta = {"collection": "monades", "db_alias": "psped"}

    code = me.StringField(required=True, unique=True)
    apografi = me.EmbeddedDocumentField(Apografi)
    remitsFinalized = me.BooleanField()
    provisionText = me.StringField()
