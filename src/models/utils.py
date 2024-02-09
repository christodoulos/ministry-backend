import json
from datetime import datetime
import unicodedata


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def convert_greek_accented_chars(text):
    normalized_text = unicodedata.normalize("NFD", text)
    no_accent_text = "".join(
        ch for ch in normalized_text if unicodedata.category(ch) != "Mn"
    )
    uppercase_text = no_accent_text.upper()
    return uppercase_text
