import mongoengine as me


class Monada(me.Document):
    meta = {"collection": "monades", "db_alias": "psped"}

    code = me.StringField(required=True, unique=True)
    remitsFinalized = me.BooleanField()
    provisionText = me.StringField()
