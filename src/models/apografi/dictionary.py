import mongoengine as me

# A model for every dictionary from https://hr.apografi.gov.gr/api.html#genikes-plhrofories-le3ika


class Dictionary(me.Document):
    meta = {
        "collection": "dictionaries",
        "db_alias": "apografi",
        "indexes": [
            {"fields": ["apografi_id", "code", "description"], "unique": True},
            "apografi_id",
            "code",
            "description",
        ],
    }

    apografi_id = me.IntField(required=True)
    parentId = me.IntField()
    code = me.StringField(required=True)
    code_el = me.StringField(required=True)
    description = me.StringField(required=True)
