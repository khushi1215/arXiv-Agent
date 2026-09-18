import re

import pymupdf as fitz
import requests

SECTION_HEADERS = [
    "abstract", "introduction", "related work", "background", "method",
    "methodology", "approach", "experiments", "results", "discussion",
    "conclusion", "limitations", "references",
]


def download_pdf(url, timeout=30):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def parse_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = doc.page_count

    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    if not full_text.strip():
        # happens with scanned/image-only pdfs, pymupdf can't pull text
        # that isn't actually encoded as text in the file
        raise ValueError("no extractable text in pdf, likely scanned or image-based")

    sections = _split_sections(full_text)
    return {"full_text": full_text, "sections": sections, "num_pages": num_pages}


def _split_sections(text):
    # naive heuristic: a short line matching a known header name starts a
    # new section. works reasonably well on most arxiv papers, will miss
    # papers with unusual formatting or two-column layouts that jumble text
    lines = text.split("\n")
    sections = {}
    current = "body"
    buffer = []

    for line in lines:
        stripped = line.strip().lower()
        clean = re.sub(r"^[\d\.\s]+", "", stripped)
        if clean in SECTION_HEADERS and len(line.strip()) < 40:
            if buffer:
                sections[current] = "\n".join(buffer).strip()
            current = clean
            buffer = []
        else:
            buffer.append(line)

    if buffer:
        sections[current] = "\n".join(buffer).strip()

    return sections
