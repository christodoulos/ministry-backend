import json
from bson import ObjectId
import mongoengine as me
from src.models.upload import FileUpload
from src.models.psped.change import Change
from datetime import datetime


class FEK(me.EmbeddedDocument):
    number = me.StringField(default="ΜΗ ΔΗΜΟΣΙΕΥΤΕΑ ΠΡΑΞΗ")
    issue = me.StringField(choices=["", "Α", "Β", "Υ.Ο.Δ.Δ."])
    date = me.StringField()


class NomikiPraxi(me.Document):
    meta = {
        "collection": "nomikes_praxeis",
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
    fek = me.EmbeddedDocumentField(FEK)
    ada = me.StringField(default="ΜΗ ΑΝΑΡΤΗΤΕΑ ΠΡΑΞΗ")
    legalActFile = me.ReferenceField(FileUpload, required=True)
    changes = me.EmbeddedDocumentListField(Change, default=[])

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
            legalActKey = f"{self.legalActTypeOther} {self.legalActNumber}/{self.legalActYear} ΦΕΚ {self.fek_info}"
        else:
            legalActKey = f"{self.legalActType} {self.legalActNumber}/{self.legalActYear} ΦΕΚ {self.fek_info}"

        existingDoc = NomikiPraxi.objects(legalActKey=legalActKey).first()
        if existingDoc:
            raise ValueError(f"Υπάρχει ήδη νομική πράξη με κλειδί {legalActKey}")

        self.legalActKey = legalActKey

        file = FileUpload.objects.get(id=ObjectId(self.legalActFile.id))
        if not file:
            raise ValueError(f"Δεν βρέθηκε αρχείο με id {self.legalActFile.file_id}")
        file.update(file_name=self.fek_filename)

        super(NomikiPraxi, self).save(*args, **kwargs)
