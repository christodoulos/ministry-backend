import json
from bson import ObjectId
import mongoengine as me
from src.models.upload import FileUpload
from datetime import datetime
import uuid


def default_ada():
    return f"ΜΗ ΑΝΑΡΤΗΤΕΑ ΠΡΑΞΗ-{uuid.uuid4()}"


class FEK(me.EmbeddedDocument):
    number = me.StringField(default=f"ΜΗ ΔΗΜΟΣΙΕΥΤΕΑ ΠΡΑΞΗ-{uuid.uuid4()}")
    issue = me.StringField(choices=["", "Α", "Β", "Υ.Ο.Δ.Δ."])
    date = me.StringField()


class LegalAct(me.Document):
    meta = {
        "collection": "legal_acts",
        "db_alias": "psped",
        "indexes": [{"fields": ["legalActKey"], "unique": True}],
    }

    legalActKey = me.StringField(unique=True)
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
    legalActYear = me.StringField(required=True)
    fek = me.EmbeddedDocumentField(FEK, unique=True)
    ada = me.StringField(default=default_ada, unique=True)
    legalActFile = me.ReferenceField(FileUpload, required=True)

    def to_json(self):
        data = self.to_mongo()
        data["legalActFile"] = str(self.legalActFile.id)
        return json.dumps(data)

    @property
    def fek_info(self):
        if self.fek.number == "ΜΗ ΔΗΜΟΣΙΕΥΤΕΑ ΠΡΑΞΗ":
            return "ΜΗ ΔΗΜΟΣΙΕΥΤΕΑ ΠΡΑΞΗ"
        else:
            fek_date = datetime.strptime(self.fek.date, "%Y-%m-%d")
            return f"{self.fek.number}/{self.fek.issue}/{fek_date.strftime('%d-%m-%Y')}"

    @property
    def legalActTypeGeneral(self):
        return self.legalActType if self.legalActType != "ΑΛΛΟ" else self.legalActTypeOther

    @property
    def fek_filename(self):
        return f"{self.legalActTypeGeneral} {self.legalActNumber}/{self.legalActYear} ΦΕΚ {self.fek_info}"

    def create_key(self):
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
            return f"{self.legalActTypeOther} {self.legalActNumber}/{self.legalActYear} ΦΕΚ {self.fek_info}"
        else:
            return f"{self.legalActType} {self.legalActNumber}/{self.legalActYear} ΦΕΚ {self.fek_info}"

    def save(self, *args, **kwargs):
        legalActKey = self.create_key()

        existingDoc = LegalAct.objects(legalActKey=legalActKey).first()
        if existingDoc:
            raise ValueError(f"Υπάρχει ήδη νομική πράξη με κλειδί {legalActKey}")

        self.legalActKey = legalActKey

        file = FileUpload.objects.get(id=ObjectId(self.legalActFile.id))
        if not file:
            raise ValueError(f"Δεν βρέθηκε αρχείο με id {self.legalActFile.file_id}")
        file.update(file_name=self.fek_filename)

        super(LegalAct, self).save(*args, **kwargs)
