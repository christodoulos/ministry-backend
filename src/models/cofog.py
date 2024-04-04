import mongoengine as me


class Cofog3(me.EmbeddedDocument):
    code = me.StringField(required=True)
    name = me.StringField(required=True)


class Cofog2(me.EmbeddedDocument):
    code = me.StringField(required=True)
    name = me.StringField(required=True)
    cofog3 = me.ListField(me.EmbeddedDocumentField(Cofog3), required=True)


class Cofog(me.Document):
    code = me.StringField(required=True)
    name = me.StringField(required=True)
    cofog2 = me.ListField(me.EmbeddedDocumentField(Cofog2), required=True)

    meta = {"collection": "cofog", "db_alias": "psped"}
