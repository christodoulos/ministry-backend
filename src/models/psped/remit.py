import mongoengine as me
from datetime import datetime


class Remit(me.Document):
    meta = {"collection": "remits", "db_alias": "psped"}

    remitCode = me.StringField(required=True, unique=True)
    remitText = me.StringField(required=True)
    remitType = me.StringField(
        required=True,
        choices=[
            "ΕΠΙΤΕΛΙΚΗ",
            "ΕΚΤΕΛΕΣΤΙΚΗ",
            "ΥΠΟΣΤΗΡΙΚΤΙΚΗ",
            "ΕΛΕΓΚΤΙΚΗ",
            "ΠΑΡΑΚΟΛΟΥΘΗΣΗΣ ΑΠΟΤΕΛΕΣΜΑΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ ΚΑΙ ΑΞΙΟΛΟΓΗΣΗΣ ΑΠΟΤΕΛΕΣΜΑΤΩΝ",
        ],
    )
    unitCode = me.StringField(required=True)
    COFOG_1stLevel = me.StringField(required=True)
    COFOG_2ndLevel = me.StringField(required=True)
    thematic_3rdLevel = me.StringField(required=True)
    status = me.StringField(required=True, choices=["ΕΝΕΡΓΗ", "ΑΝΕΝΕΡΓΗ"])
    diataxisCodes = me.ListField(me.StringField(), required=True)
    creationDate = me.DateField(default=datetime.now)
    userCode = me.StringField(required=True)
    updateDate = me.DateField()

    @classmethod
    def generate_remit_code(cls):
        # Attempt to find the highest current remit code and increment it
        last_remit = cls.objects.order_by("-remitCode").first()
        if last_remit:
            last_number = int(last_remit.remitCode[1:])  # Exclude the first character ('A') and convert to int
            new_number = last_number + 1
        else:
            new_number = 1  # Start from 1 if no remits exist
        return f"A{new_number:08d}"

    def save(self, *args, **kwargs):
        self.updateDate = datetime.now()
        return super(Remit, self).save(*args, **kwargs)
