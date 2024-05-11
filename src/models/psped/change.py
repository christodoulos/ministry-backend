import mongoengine as me
from src.config import MONGO_PSPED_DB
from datetime import datetime


class What(me.EmbeddedDocument):
    entity = me.StringField(
        required=True, choices=["user", "organization", "organizationalUnit", "remit", "legalAct", "legalProvision"]
    )
    key = me.DictField(required=True)


class Change(me.Document):
    meta = {"collection": "changes", "db_alias": MONGO_PSPED_DB}

    action = me.StringField(required=True, choices=["create", "read", "update", "delete"])
    who = me.StringField(required=True)
    what = me.EmbeddedDocumentField(What, required=True)
    when = me.DateTimeField(default=datetime.now)
    change = me.DictField(required=True)
