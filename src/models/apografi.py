from src import db
import mongoengine as me


class Dictionary(db.Document):
    apografi_id = me.IntField(required=True, db_field="id")
    parentId = me.IntField()
    code = me.StringField(required=True)
    code_el = me.StringField(required=True)
    description = me.StringField(required=True)

    meta = {
        "collection": "dictionaries",
        "db_alias": "apografi",
        "indexes": [{"fields": ["apografi_id", "code", "description"], "unique": True}],
    }
