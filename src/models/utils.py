import json
from datetime import datetime
import unicodedata
import mongoengine as me


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def convert_greek_accented_chars(text):
    normalized_text = unicodedata.normalize("NFD", text)
    no_accent_text = "".join(ch for ch in normalized_text if unicodedata.category(ch) != "Mn")
    uppercase_text = no_accent_text.upper()
    return uppercase_text


class SyncLog(me.Document):
    meta = {"collection": "synclog", "db_alias": "apografi"}

    date = me.DateTimeField(default=datetime.now())
    entity = me.StringField(required=True, choices=["dictionary", "organization", "organizational-unit"])
    action = me.StringField(required=True, choices=["insert", "update"])
    doc_id = me.StringField(required=True)
    value = me.DictField(required=True)


class Error(me.Document):
    meta = {"collection": "errors", "db_alias": "apografi"}

    date = me.DateTimeField(default=datetime.now())
    entity = me.StringField(required=True, choices=["dictionary", "organization", "organizational-unit"])
    doc_id = me.StringField(required=True)
    value = me.DictField(required=True)
