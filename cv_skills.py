"""Conservative extraction of explicitly stated skills and credentials from CV text."""
import re

SKILL_TERMS = [
    "AutoCAD", "Civil 3D", "Revit", "BIM", "Primavera P6", "MS Project",
    "Microsoft Excel", "Microsoft Word", "Power BI", "Python", "SQL", "QGIS", "ArcGIS",
    "GIS", "Quantity Surveying", "Cost Estimation", "Project Management",
    "Construction Management", "Quality Assurance", "Quality Control", "QA/QC",
    "Site Inspection", "Structural Design", "Road Design", "Highway Design",
    "Surveying", "Contract Administration", "Risk Management", "Scheduling",
    "Technical Writing", "Data Analysis", "Stakeholder Coordination",
    "Occupational Safety and Health", "OSH", "ISO 9001", "SAP", "ETABS", "STAAD.Pro",
]
LICENSE_PATTERNS = [
    ("PRC Licensed Civil Engineer", r"\b(?:PRC\s*(?:licensed|registered)|licensed\s*civil\s*engineer|registered\s*civil\s*engineer)\b"),
    ("PRC Licensed Architect", r"\b(?:licensed|registered)\s*architect\b"),
    ("Professional Engineer", r"\bprofessional\s+engineer\b"),
    ("COSH", r"\bCOSH\b|\bconstruction\s+occupational\s+safety\s+and\s+health\b"),
    ("BOSH", r"\bBOSH\b|\bbasic\s+occupational\s+safety\s+and\s+health\b"),
    ("PMP", r"\bPMP\b|\bproject\s+management\s+professional\b"),
    ("ISO 9001", r"\bISO\s*9001(?::2015)?\b"),
]
HEADINGS = r"(?:technical\s+skills|core\s+competenc(?:y|ies)|skills|software\s+proficiency|licenses?\s*(?:/|and|&)\s*certifications?|professional\s+licen[sc]e|certifications?|licenses?|professional\s+affiliations?|training(?:s)?\s*(?:/|and|&)\s*certifications?)"
OTHER_HEADINGS = r"(?:education|employment\s+history|work\s+experience|professional\s+experience|selected\s+projects|projects|references|profile|summary|contact|awards|languages|personal\s+information|geographic\s+project\s+experience)"

def _sections(text):
    lines=text.splitlines()
    result={"skills":[],"licenses":[]}
    active=None
    for line in lines:
        clean=line.strip().strip(":").strip()
        if not clean: continue
        if len(clean)<85 and re.fullmatch(HEADINGS,clean,re.I):
            active="skills" if re.search(r"skills|competenc|software",clean,re.I) else "licenses"
            continue
        if len(clean)<85 and re.fullmatch(OTHER_HEADINGS,clean,re.I): active=None;continue
        if active and len(clean)<220:
            result[active].append(re.sub(r"^[•*\-\d.)\s]+", "",clean))
    return result

def extract_skills_licenses(text):
    if not text or not text.strip(): return {"skills":"", "licenses":""}
    sections=_sections(text)
    skills=[]
    for term in SKILL_TERMS:
        if re.search(r"(?<!\w)"+re.escape(term)+r"(?!\w)",text,re.I): skills.append(term)
    # Use explicit skills-section entries when a dictionary term wasn't recognized.
    for line in sections["skills"]:
        for item in re.split(r"[,;|•]",line):
            item=item.strip(" -•\t")
            if 2<len(item)<65 and not re.search(r"\b(?:phone|email|address|years?)\b",item,re.I):
                if not any(item.casefold()==s.casefold() for s in skills): skills.append(item)
    licenses=[]
    for label,pattern in LICENSE_PATTERNS:
        if re.search(pattern,text,re.I): licenses.append(label)
    for line in sections["licenses"]:
        for item in re.split(r"[,;|•]",line):
            item=item.strip(" -•\t")
            if 3<len(item)<100 and not re.search(r"\b(?:phone|email|address)\b",item,re.I):
                if not any(item.casefold()==s.casefold() for s in licenses): licenses.append(item)
    return {"skills":", ".join(skills[:3]), "licenses":"; ".join(licenses[:12])}
