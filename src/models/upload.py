import mongoengine as me


class FileUpload(me.Document):
    google_id = me.StringField(required=True)
    file_id = me.StringField(unique=True, required=True)
    file_name = me.StringField(required=True)
    file_type = me.StringField(required=True)
    file_size = me.IntField(required=True)
    file_location = me.StringField(required=True)

    meta = {"collection": "file_uploads", "db_alias": "psped"}
