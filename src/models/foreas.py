from src import db
import mongoengine as me


class Foreas(db.Document):
    nomikes_morfes = {
        "0": "Υπηρεσία του Νομικού Προσώπου του Κράτους",
        "1": "Νομικό Πρόσωπο Δημοσίου Δικαίου",
        "2": "Νομικό Πρόσωπο Ιδιωτικού Δικαίου",
        "3": "Ανώνυμη Εταιρεία",
        "4": "Οργανισμός Τοπικής Αυτοδιοίκησης Αποκεντρωμένης Διοίκησης",
        "5": "Οργανισμός Τοπικής Αυτοδιοίκησης Βασικής Διοίκησης",
        "6": "Νομικό Πρόσωπο Δημοσίου Δικαίου Οργανισμού Τοπικής Αυτοδιοίκησης",
        "7": "Νομικό Πρόσωπο Ιδιωτικού Δικαίου Οργανισμού Τοπικής Αυτοδιοίκησης",
        "8": "Ανώνυμη Εταιρεία Οργανισμού Τοπικής Αυτοδιοίκησης",
    }

    tomeis_politikhs = {
        "0": "ΑΘΛΗΤΙΣΜΟΣ",
        "1": "ΑΛΙΕΙΑ",
        "2": "ΑΜΥΝΑ",
        "3": "ΑΝΘΡΩΠΙΝΑ ΔΙΚΑΙΩΜΑΤΑ",
        "4": "ΑΠΑΣΧΟΛΗΣΗ ΚΑΙ ΕΡΓΑΣΙΑ",
        "5": "ΒΙΟΜΗΧΑΝΙΑ",
        "6": "ΓΕΩΡΓΙΑ",
        "7": "ΔΑΣΟΚΟΜΙΑ",
        "8": "ΔΗΜΟΣΙΑ ΔΙΟΙΚΗΣΗ",
        "9": "ΔΗΜΟΣΙΑ ΤΑΞΗ",
        "10": "ΔΗΜΟΣΙΟΝΟΜΙΚΑ",
        "11": "ΔΙΑΣΤΗΜΑ",
        "12": "ΔΙΑΤΡΟΦΗ ΚΑΙ ΓΕΩΡΓΙΚΑ ΠΡΟΪΟΝΤΑ",
        "13": "ΔΙΑΦΑΝΕΙΑ - ΚΑΤΑΠΟΛΕΜΗΣΗ ΔΙΑΦΘΟΡΑΣ",
        "14": "ΔΙΕΘΝΕΙΣ ΟΡΓΑΝΙΣΜΟΙ",
        "15": "ΔΙΕΘΝΕΙΣ ΣΧΕΣΕΙΣ",
        "16": "ΔΙΚΑΙΟΣΥΝΗ",
        "17": "ΕΚΠΑΙΔΕΥΣΗ ΚΑΤΑΡΤΙΣΗ ΝΕΟΛΑΙΑ",
        "18": "ΕΝΕΡΓΕΙΑ",
        "19": "ΕΞΩΤΕΡΙΚΗ ΠΟΛΙΤΙΚΗ",
        "20": "ΕΠΙΧΕΙΡΗΣΕΙΣ ΚΑΙ ΑΝΤΑΓΩΝΙΣΜΟΣ",
        "21": "ΕΥΡΩΠΑΪΚΗ ΈΝΩΣΗ",
        "22": "ΘΑΛΑΣΣΙΑ ΚΑΙ ΛΙΜΕΝΙΚΗ ΠΟΛΙΤΙΚΗ",
        "23": "ΘΡΗΣΚΕΙΑ",
        "24": "ΙΘΑΓΕΝΕΙΑ",
        "25": "ΚΟΙΝΩΝΙΚΗ ΑΛΛΗΛΕΓΓΥΗ",
        "26": "ΜΕΣΑ ΕΠΙΚΟΙΝΩΝΙΑΣ",
        "27": "ΜΕΤΑΝΑΣΤΕΥΣΗ",
        "28": "ΜΕΤΑΦΟΡΕΣ",
        "29": "ΟΙΚΟΝΟΜΙΚΕΣ ΚΑΙ ΕΜΠΟΡΙΚΕΣ ΣΥΝΑΛΛΑΓΕΣ",
        "30": "ΠΑΡΑΓΩΓΗ",
        "31": "ΠΕΡΙΒΑΛΛΟΝ",
        "32": "ΠΟΛΙΤΙΚΗ ΖΩΗ",
        "33": "ΠΟΛΙΤΙΚΗ ΠΡΟΣΤΑΣΙΑ",
        "34": "ΠΟΛΙΤΙΣΜΟΣ",
        "35": "ΤΕΧΝΟΛΟΓΙΑ ΚΑΙ ΕΡΕΥΝΑ",
        "36": "ΤΟΥΡΙΣΜΟΣ",
        "37": "ΥΓΕΙΑ",
        "38": "ΧΩΡΟΤΑΞΙΑ - ΥΠΟΔΟΜΕΣ",
        "39": "ΨΗΦΙΑΚΗ ΟΙΚΟΝΟΜΙΑ ΚΑΙ ΚΟΙΝΩΝΙΑ",
    }

    epipeda_diakubernhshs = {
        "1": "Κεντρικό",
        "2": "Περιφερειακό",
        "3": "Τοπικό",
    }

    kwdikos = me.StringField(required=True, unique=True)
    onomasia = me.StringField(required=True, max_length=255)
    nomikh_morfh = me.StringField(
        required=True, choices=nomikes_morfes.keys(), max_length=2
    )
    tomeas_politikhs = me.StringField(
        required=True, choices=tomeis_politikhs.keys(), max_length=2
    )
    epipedo_diakubernhshs = me.StringField(
        required=True, choices=epipeda_diakubernhshs.keys(), max_length=2
    )
    skopos = me.StringField(required=True, max_length=255)

    @property
    def nomikh_morfh_display(self):
        return self.nomikes_morfes[self.nomikh_morfh]

    @property
    def tomeas_politikhs_display(self):
        return self.tomeis_politikhs[self.tomeas_politikhs]

    @property
    def epipedo_diakubernhshs_display(self):
        return self.epipeda_diakubernhshs[self.epipedo_diakubernhshs]
