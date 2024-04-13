import mongoengine as me
from datetime import datetime


class Change(me.EmbeddedDocument):
    action = me.StringField(required=True, choices=["create", "read", "update", "delete"])
    who = me.StringField(required=True)
    when = me.DateTimeField(default=datetime.now)
    change = me.DictField(required=True)
