import io
import re
from docx import Document
from pypdf import PdfReader

def extract_text(file):
    suffix=file.name.rsplit(".",1)[-1].lower(); raw=file.getvalue()
    if suffix=="pdf": return "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(raw)).pages)
    if suffix=="docx": return "\n".join(p.text for p in Document(io.BytesIO(raw)).paragraphs)
    return raw.decode("utf-8",errors="replace")

def extracted_identity(text):
    email=re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",text)
    phone=re.search(r"(?:\+?63|0)\s?9\d{2}[\s-]?\d{3}[\s-]?\d{4}",text)
    name=""
    for line in text.splitlines()[:15]:
        clean=re.sub(r"\s+"," ",line).strip()
        if 3<=len(clean)<=70 and not re.search(r"curriculum|vitae|resume|profile",clean,re.I): name=clean; break
    return name,email.group(0) if email else "",phone.group(0) if phone else ""
