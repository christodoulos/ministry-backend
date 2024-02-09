import unicodedata


def convert_greek_accented_chars(text):
    normalized_text = unicodedata.normalize("NFD", text)
    no_accent_text = "".join(
        ch for ch in normalized_text if unicodedata.category(ch) != "Mn"
    )
    uppercase_text = no_accent_text.upper()
    return uppercase_text
