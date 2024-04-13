import mongoengine as me
from datetime import datetime


class PspedLog(me.Document):
    meta = {"collection": "psped_logs", "db_alias": "psped"}

    date = me.DateTimeField(default=datetime.now)
    entity = me.StringField(required=True, choices=["foreas", "remit", "diataxi", "nomiki_praxi"])
    action = me.StringField(required=True, choices=["insert", "update"])
    doc_id = me.StringField(required=True)
    value = me.DictField(required=True)


class PspedSystemLog(me.Document):
    meta = {"collection": "psped_system_logs", "db_alias": "psped"}

    date = me.DateTimeField(default=datetime.now)
    user_id = me.StringField(required=True)
    action = me.StringField(
        required=True,
        choices=[
            "login",
            "logout",
            "create",
            "update",
        ],
    )
    data = me.DictField()
