"""Automatic, conservative TOR evidence assessment (no external AI service).

Results are provisional: extracted text cannot authenticate credentials or dates.
"""
import re

HEADINGS = re.compile(r'(?i)\b(?:minimum qualifications?|required qualifications?|education|academic qualifications?|experience|training|certifications?|licenses?|eligibility|skills|requirements?|qualification standards?)\b')
BULLET = re.compile(r'^\s*(?:[-•*]|\d+[.)])\s+')
STOPWORDS = set('the and for with from have that this shall must should minimum required requirement years year experience relevant professional qualification qualifications candidate applicant work project projects national international similar including at least knowledge ability proven demonstrated degree of in a an to or as on by is be not than any'.split())
YEAR_REQ = re.compile(r'(?i)(?:at least|minimum(?: of)?|not less than|more than|over)?\s*(\d{1,2})\s*(?:\+\s*)?years?\b')
YEAR_CV = re.compile(r'(?i)\b(\d{1,2})\s*\+?\s*years?\b')

def extract_requirements(tor_text, limit=40):
    """Identify likely qualification statements without inventing missing TOR rules."""
    lines = [re.sub(r'\s+', ' ', x).strip() for x in tor_text.splitlines()]
    lines = [x for x in lines if x]
    selected, active = [], False
    for line in lines:
        heading = bool(HEADINGS.search(line))
        if heading and len(line) < 100 and not YEAR_REQ.search(line) and (line.endswith(':') or len(line.split()) <= 5):
            active = True
            continue
        is_requirement = bool(YEAR_REQ.search(line) or re.search(r'(?i)\b(?:bachelor|master|phd|doctorate|licensed|certified|must have|required|at least|minimum)\b', line))
        if (active or is_requirement) and (BULLET.match(line) or heading or is_requirement or 20 <= len(line) <= 250):
            cleaned = BULLET.sub('', line).strip()
            if len(cleaned) >= 12 and cleaned.lower() not in {x.lower() for x in selected}:
                selected.append(cleaned[:500])
        if len(selected) >= limit:
            break
    return selected

def _terms(s):
    return list(dict.fromkeys(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z+#.-]{2,}', s) if w.lower() not in STOPWORDS))

def compare_requirements(requirements, cv_text):
    """Return automatic evidence statuses. No false definitive failure for missing text."""
    cv_lower = cv_text.lower()
    rows = []
    for req in requirements:
        terms = _terms(req)
        matches = [w for w in terms if re.search(r'(?<!\w)'+re.escape(w)+r'(?!\w)', cv_lower)]
        coverage = len(matches)/len(terms) if terms else 0
        yr = YEAR_REQ.search(req)
        stated_years = [int(x) for x in YEAR_CV.findall(cv_text)]
        # Generic years stated anywhere in a CV cannot prove years in a specific field.
        if yr:
            minimum = int(yr.group(1))
            if stated_years and max(stated_years) < minimum:
                status = 'Potential gap'
                reason = f'TOR asks for {minimum} years; largest explicit CV claim is {max(stated_years)} years. Confirm relevance and dates.'
            elif stated_years and max(stated_years) >= minimum and coverage >= 0.5:
                status = 'Evidence found — provisional'
                reason = f'CV mentions {max(stated_years)} years, but relevance and dates are not independently validated.'
            else:
                status = 'Not verified'
                reason = f'Cannot confirm {minimum} relevant years from extracted CV text.'
        elif coverage >= 0.75 and len(matches) >= 2:
            status = 'Evidence found — provisional'
            reason = 'Multiple requirement terms found in CV; context and authenticity are not independently verified.'
        elif coverage >= 0.35:
            status = 'Partial evidence'
            reason = 'Some matching qualification terms were detected.'
        else:
            status = 'Not verified'
            reason = 'Insufficient matching evidence in extracted CV text; this does not prove the candidate fails.'
        rows.append({'TOR requirement':req, 'Automatic assessment':status,
                     'Evidence':', '.join(matches[:8]) if matches else 'None identified',
                     'Explanation':reason})
    return rows

def summarize_assessment(rows):
    if not rows:
        return 'Unable to assess', 'No requirements were extracted reliably from the TOR.'
    counts = {status:sum(r['Automatic assessment']==status for r in rows) for status in
              ['Evidence found — provisional','Partial evidence','Potential gap','Not verified']}
    if counts['Potential gap']:
        outcome = 'Potential qualification gaps'
    elif counts['Not verified'] or counts['Partial evidence']:
        outcome = 'Further evidence needed'
    else:
        outcome = 'Provisionally aligned'
    return outcome, (f"{counts['Evidence found — provisional']} supported; "
                     f"{counts['Partial evidence']} partial; {counts['Potential gap']} potential gaps; "
                     f"{counts['Not verified']} not verified. Results are provisional, not a formal eligibility decision.")
