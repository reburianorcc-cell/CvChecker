"""Conservative, transparent CV pre-screening. Suggestions require human confirmation."""
import re
from datetime import date
from config import ACADEMIC, TRAINING, POSITIONS, ELIGIBILITY

DEGREES=[('Doctorate',r'\b(ph\.?d\.?|doctorate|doctoral)\b'),("Master's degree",r"\b(master(?:'s)?|m\.?sc\.?|m\.?eng\.?|mba)\b"), ("Bachelor's degree",r"\b(bachelor(?:'s)?|b\.?s\.?\s*(?:in|of)?|b\.?a\.?\s*(?:in|of)?|b\.?eng\.?|bsit|bsc)\b")]

def _years(text):
    """Estimate elapsed work experience only from employment-history date ranges.

    Never count education, certifications or selected project dates as employment.
    Merge overlapping employment periods and use month precision where available.
    """
    section = re.search(
        r"(?im)^\s*(?:EMPLOYMENT HISTORY|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT EXPERIENCE|CAREER HISTORY)\s*$"
        r"([\s\S]*?)(?=^\s*(?:RELEVANT TRAINING(?:S)?(?:\s*&\s*CERTIFICATIONS)?|TRAINING(?:S)?|TECHNICAL SKILLS|GEOGRAPHIC PROJECT EXPERIENCE|SELECTED PROJECTS|EDUCATION|REFERENCES|CERTIFICATIONS|PROFESSIONAL LICENSE)\s*$|\Z)",
        text,
        re.M,
    )
    if not section:
        return None
    work = section.group(1)
    months = {name: idx for idx, name in enumerate(
        ('january','february','march','april','may','june','july','august','september','october','november','december'), 1)}
    month_re = '|'.join(months)
    pattern = re.compile(
        rf"\b({month_re})\s+(19\d{{2}}|20\d{{2}})\s*(?:[-–—]|to)\s*(?:({month_re})\s+(19\d{{2}}|20\d{{2}})|(present|current|now))\b",
        re.I,
    )
    today = date.today()
    occupied = set()
    for match in pattern.finditer(work):
        start = int(match.group(2))*12 + months[match.group(1).lower()] - 1
        if match.group(5):
            end = today.year*12 + today.month - 1
        else:
            end = int(match.group(4))*12 + months[match.group(3).lower()] - 1
        if start <= end and end <= today.year*12 + today.month - 1:
            occupied.update(range(start, end + 1))
    if not occupied:
        return None  # Don't guess using education or project years.
    return round(len(occupied)/12, 2)

def _bucket(years, options):
    if years is None: return None
    for label in options:
        if label.lower()=='none': continue
        if 'or more' in label and years>=int(re.search(r'\d+',label).group()): return label
        if '–' in label or '-' in label:
            nums=re.findall(r'\d+',label)
            if len(nums)>=2 and int(nums[0])<=years<=int(nums[1]): return label
        if label.lower().startswith('below') and years<int(re.search(r'\d+',label).group()): return label
        if re.fullmatch(r'\d+ years?',label) and years==int(re.search(r'\d+',label).group()): return label
    return None

def analyze_cv(text, position):
    suggestions={}; evidence={}; warnings=[]
    for label,pattern in DEGREES:
        match=re.search(pattern,text,re.I)
        if match:
            suggestions['academic']=label; evidence['academic']=match.group(0); break
    if 'academic' not in suggestions: warnings.append('Academic degree not reliably identified')
    years=_years(text)
    professional=_bucket(years,POSITIONS[position]['professional'])
    if professional:
        suggestions['professional']=professional
        evidence['professional']=f'Approx. {years} calendar years from detected date ranges; overlapping periods combined. Verify employment dates.'
    else: warnings.append('Professional experience requires date verification')
    # Training section: count distinct bullet/course lines, avoiding the rest of the CV.
    section=re.search(r"(?im)^\s*(?:RELEVANT TRAINING(?:S)?(?:\s*&\s*CERTIFICATIONS)?|TRAINING(?:S)?(?:\s*&\s*CERTIFICATIONS)?)\s*$([\s\S]*?)(?=^\s*(?:TECHNICAL SKILLS|EMPLOYMENT HISTORY|GEOGRAPHIC PROJECT EXPERIENCE|SELECTED PROJECTS|REFERENCES|EDUCATION)\s*$|\Z)",text,re.M)
    if section:
        lines=[x.strip() for x in section.group(1).splitlines() if x.strip()]
        courses=[x for x in lines if re.search(r"[A-Za-z]{4}",x) and (re.search(r"[—–-]\s*20\d{2}|\d+\s*(?:hours|hrs)",x,re.I) or x.startswith(('•','-','*')))]
        n=len(courses)
        if n:
            label="Over 5 trainings" if n>5 else "4 trainings" if n==4 else "3 trainings" if n==3 else "2 or fewer trainings"
            suggestions['training']=label; evidence['training']=f'{n} training entries found in training section; confirm relevance and completion.'
    # Count named entries in a dedicated projects section only, not employer count.
    projects_section=re.search(r"(?im)^\s*SELECTED PROJECTS\s*$([\s\S]*?)(?=^\s*(?:REFERENCES|CERTIFICATIONS|EDUCATION|TECHNICAL SKILLS)\s*$|\Z)",text,re.M)
    if projects_section:
        named=[x.strip() for x in projects_section.group(1).splitlines() if re.search(r"\(\s*20\d{2}\s*[-–]\s*(?:20\d{2}|present)\s*\)",x,re.I)]
        if named:
            opts=POSITIONS[position]['projects']
            label=('2 or more projects' if len(named)>=2 else '1 project')
            if label not in opts and len(named)>=1 and '1 or more projects' in opts: label='1 or more projects'
            if label in opts:
                suggestions['projects']=label
                evidence['projects']=f'{len(named)} named projects found; verify they meet the TOR geographic requirements.'
    # Relevant years are a conservative hint only when the CV clearly describes
    # infrastructure duties. They are NOT a verified TOR match.
    if years is not None and re.search(r'road|bridge|infrastructure|construction|engineering',text,re.I):
        rel=_bucket(years,POSITIONS[position]['relevant'])
        if rel:
            suggestions['relevant']=rel
            evidence['relevant']=f'Approx. {years} years of dated work and infrastructure keywords; verify each role against TOR.'
    # Relevant experience cannot be established from years alone; needs TOR and project responsibilities.
    warnings.append('Relevant experience must be matched to the TOR and actual duties')
    warnings.append('Training count requires confirmation of completed, relevant courses')
    warnings.append('Geographic project experience requires project-level verification')
    warnings.append('Professional eligibility or licensing must be verified')
    return {'suggestions':suggestions,'evidence':evidence,'warnings':warnings,'years':years}
