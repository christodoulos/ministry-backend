import mongoengine as me
from src.models.upload import FileUpload
from datetime import datetime


class FEKdate(me.EmbeddedDocument):
    day = me.IntField(required=True)
    month = me.IntField(required=True)
    year = me.IntField(required=True)


class FEKDiataxi(me.EmbeddedDocument):
    FEKnumber = me.StringField(required=True)
    FEKissue = me.StringField(required=True)
    FEKdate = me.EmbeddedDocumentField(FEKdate)


class NomikiPraxi(me.Document):
    meta = {"collection": "nomikes_praxeis", "db_alias": "psped"}

    legalActCode = me.StringField(required=True, unique=True)
    legalActType = me.StringField(
        required=True,
        choices=[
            "ΝΟΜΟΣ",
            "ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ",
            "ΚΑΝΟΝΙΣΤΙΚΗ ΔΙΟΙΚΗΤΙΚΗ ΠΡΑΞΗ",
            "ΑΠΟΦΑΣΗ ΤΟΥ ΟΡΓΑΝΟΥ ΔΙΟΙΚΗΣΗΣ",
            "ΑΛΛΟ",
        ],
    )
    legalActTypeOther = me.StringField()
    legalActNumber = me.StringField(required=True)
    legalActDate = me.DateField(required=True)
    FEKref = me.EmbeddedDocumentField(FEKDiataxi)
    DiavgeiaNumber = me.StringField()
    legalActFile = me.ReferenceField(FileUpload)
    userCode = me.StringField(required=True)
    creationDate = me.DateTimeField(default=datetime.now())
    updateDate = me.DateTimeField()

    @classmethod
    def generate_nomiki_praxi_code(cls):
        last_code = cls.objects.order_by("-legalActCode").first()
        if last_code:
            last_number = int(last_code.legalActCode[1:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"L{new_number:08d}"

    def save(self, *args, **kwargs):
        if self.legalActType == "ΑΛΛΟ":
            if not self.legalActTypeOther:
                raise ValueError("Ο τύπος πράξης δεν μπορεί να είναι κενός ενώ επιλέξατε 'ΑΛΛΟ'")
            if self.legalActTypeOther in [
                "ΝΟΜΟΣ",
                "ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ",
                "ΚΑΝΟΝΙΣΤΙΚΗ ΔΙΟΙΚΗΤΙΚΗ ΠΡΑΞΗ",
                "ΑΠΟΦΑΣΗ ΤΟΥ ΟΡΓΑΝΟΥ ΔΙΟΙΚΗΣΗΣ",
                "ΑΛΛΟ",
            ]:
                raise ValueError(
                    "Ο τύπος πράξης δεν μπορεί να είναι κάποια από τις τιμές 'ΝΟΜΟΣ', 'ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ', 'ΚΑΝΟΝΙΣΤΙΚΗ ΔΙΟΙΚΗΤΙΚΗ ΠΡΑΞΗ', 'ΑΠΟΦΑΣΗ ΤΟΥ ΟΡΓΑΝΟΥ ΔΙΟΙΚΗΣΗΣ', 'ΑΛΛΟ'"
                )
        super(NomikiPraxi, self).save(*args, **kwargs)
