REPLACEMENTS = {
    "\u2011": "-",   # non-breaking hyphen
    "\u2010": "-",   # hyphen
    "\u2012": "-",   # figure dash
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2212": "-",   # minus sign
    "\u00a0": " ",   # non-breaking space
}


def clean_text(text):
    if not isinstance(text, str):
        return text
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text


def clean_briefing(briefing):
    for key, value in briefing.items():
        if isinstance(value, str):
            briefing[key] = clean_text(value)
        elif isinstance(value, list):
            briefing[key] = [clean_text(v) for v in value]
    return briefing
