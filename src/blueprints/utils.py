import unicodedata

ATTRIBUTE_DICT_TO_GREEK = {
    "meros": "Μέρος",
    "arthro": "Άρθρο",
    "paragrafos": "Παράγραφος",
    "edafio": "Έδαφιο",
    "pararthma": "Παράρτημα",
}


def convert_greek_accented_chars(text):
    normalized_text = unicodedata.normalize("NFD", text)
    no_accent_text = "".join(ch for ch in normalized_text if unicodedata.category(ch) != "Mn")
    uppercase_text = no_accent_text.upper()
    return uppercase_text


def attribute_to_greek(attribute):
    return ATTRIBUTE_DICT_TO_GREEK.get(attribute, attribute)


def dict2string(d):
    return ", ".join([f"{attribute_to_greek(k)} {v}" for k, v in d.items() if v])


def debug_print(message, what):
    print(f"{80*'='}\n{message}\n{80*'='}")
    try:
        for key, value in what.items():
            print(f"{key}: {value}")
    except Exception:
        print(what)
