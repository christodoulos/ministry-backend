import mongoengine as me


class RegulatedObjectCode(me.EmbeddedDocument):
    foreas = me.StringField(required=True)
    monada = me.StringField(required=True)


class COFOG(me.EmbeddedDocument):
    cofog1 = me.StringField(required=True)
    cofog2 = me.StringField(required=True)
    cofog3 = me.StringField(required=True)


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
    cofog = me.EmbeddedDocumentField(COFOG, required=True)
    status = me.StringField(choices=["ΕΝΕΡΓΗ", "ΑΝΕΝΕΡΓΗ"], default="ΕΝΕΡΓΗ")
    regularedObject = me.EmbeddedDocumentField(RegulatedObjectCode, required=True)
    diataxisCodes = me.ListField(me.StringField(), required=True)
