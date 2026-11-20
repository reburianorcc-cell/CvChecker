import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

def create_excel(data):
    out=io.BytesIO(); wb=Workbook(); ws=wb.active; ws.title="CV Evaluation"
    blue="0070C0"; thin=Side(style="thin",color=blue); border=Border(left=thin,right=thin,top=thin,bottom=thin)
    for col,width in {"A":34,"B":12,"C":28,"D":12,"E":15}.items(): ws.column_dimensions[col].width=width
    ws.merge_cells("A1:E1"); ws["A1"]="CV CHECKER — EXPERT EVALUATION SHEET"
    ws["A1"].fill=PatternFill("solid",fgColor=blue); ws["A1"].font=Font(bold=True,color="FFFFFF",size=14); ws["A1"].alignment=Alignment(horizontal="center")
    info=[("Project Name",data.get("project_name","")),("TOR",data.get("tor_name","")),("Client Name",data.get("client_name","")),("Name of Expert",data["candidate_name"]),("Age",data.get("age","")),("Number",data.get("candidate_number") or data.get("mobile","")),("Email",data.get("email","")),("Pro Level",data["pos_level"]),("Applied Position",data["applied_position"]),("Key / Non-Key",data.get("key_classification","Non-Key")),("Key Category",data.get("key_scope") or "Not applicable"),("Evaluation Date",data["evaluation_date"])]
    row=2
    for label,value in info: ws.cell(row,1,label); ws.merge_cells(start_row=row,start_column=2,end_row=row,end_column=5); ws.cell(row,2,value); row+=1
    ws.merge_cells(start_row=row,start_column=1,end_row=row,end_column=5); ws.cell(row,1,"QUALIFICATIONS, EXPERTISE AND EXPERIENCE"); ws.cell(row,1).fill=PatternFill("solid",fgColor=blue); ws.cell(row,1).font=Font(bold=True,color="FFFFFF"); row+=1
    for col,value in enumerate(["Criteria","Weight","Performance Index","Rating Index","Score (pts)"],1): ws.cell(row,col,value); ws.cell(row,col).font=Font(bold=True)
    row+=1
    for item in data["criteria"]:
        ws.cell(row,1,item["criterion"]); ws.cell(row,2,item["weight"]); ws.cell(row,2).number_format="0%"; ws.cell(row,3,item["selected"]); ws.cell(row,4,item["rating"]); ws.cell(row,4).number_format="0%"; ws.cell(row,5,item["points"]); ws.cell(row,5).number_format="0.00"; row+=1
    ws.cell(row,1,"OVERALL TOTAL"); ws.cell(row,4,data["overall_percentage"]/100); ws.cell(row,4).number_format="0.00%"; ws.cell(row,5,data["total_score"]); ws.cell(row,5).number_format='0.00 "pts"'
    for cell in ws[row]: cell.fill=PatternFill("solid",fgColor=blue); cell.font=Font(bold=True,color="FFFFFF")
    row+=1
    for title,value in [("TECHNICAL SKILLS",data.get("skills","")),("LICENSES / CERTIFICATIONS / AFFILIATIONS",data.get("licenses","")),("OTHER EVALUATION REMARKS",data.get("remarks","")),("FINAL CLASSIFICATION",data.get("key_classification","Non-Key")),("DECISION",data.get("decision",data["result"]))]:
        ws.cell(row,1,title); ws.merge_cells(start_row=row,start_column=2,end_row=row,end_column=5); ws.cell(row,2,value); row+=1
    for cells in ws.iter_rows(min_row=1,max_row=row-1,min_col=1,max_col=5):
        for cell in cells: cell.border=border; cell.alignment=Alignment(vertical="center",wrap_text=True)
    ws.sheet_view.showGridLines=False; ws.page_setup.orientation="landscape"; ws.page_setup.fitToWidth=1
    wb.save(out); out.seek(0); return out.getvalue()


def create_all_evaluations_excel(records):
    """Export all Supabase records with openpyxl (no artifact_tool dependency)."""
    import json
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    criteria_labels = [
        "Academic Qualification",
        "Number of Relevant Trainings",
        "Total Professional Experience",
        "Relevant Experience for Pro C",
        "Philippines/Similar Geographic Experience",
        "Eligibility",
    ]
    headers = ["Name", "Age", "Applied Position", "Email", "Phone Number",
               "Professional Level", "Personnel Classification"]
    headers += [f"{label} (Points)" for label in criteria_labels]
    headers += ["Skills", "Remarks"]
    headers += ["Overall Rating (%)"]

    def details_of(record):
        details = record.get("details_json") or {}
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except (ValueError, TypeError):
                details = {}
        return details if isinstance(details, dict) else {}

    def field(record, details, key, fallback=None):
        value = details.get(key)
        if value is None or value == "":
            value = record.get(key)
        if (value is None or value == "") and fallback:
            value = details.get(fallback) or record.get(fallback)
        return "" if value is None else value

    def number(value):
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    wb = Workbook()
    ws = wb.active
    ws.title = "All CV Evaluations"
    ws.append(headers)
    for record in records:
        details = details_of(record)
        criteria = details.get("criteria") or []
        def match(label):
            for item in criteria:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("criterion") or "").strip().lower()
                if name == label.lower() or (label == "Relevant Experience for Pro C" and
                        name.startswith("relevant experience for ")):
                    return item
            return {}
        matched = [match(label) for label in criteria_labels]
        row = [field(record, details, "candidate_name"), field(record, details, "age"),
               field(record, details, "applied_position"), field(record, details, "email"),
               field(record, details, "candidate_number", "mobile"),
               field(record, details, "pos_level"),
               field(record, details, "key_classification") or "Non-Key"]
        row += [number(item.get("points")) for item in matched]
        row += [field(record, details, "skills"), field(record, details, "remarks")]
        overall = number(field(record, details, "overall_percentage"))
        row.append(overall / 100 if overall is not None else None)
        ws.append(row)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[1].height = 43
    for cell in ws[1]:
        cell.fill = PatternFill("solid", fgColor="174B86")
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for i in range(1, len(headers) + 1):
        letter = get_column_letter(i)
        ws.column_dimensions[letter].width = (38 if i in (14, 15) else 30 if i in (1, 3, 4) else 24)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if cell.row % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F3F7FC")
        row[15].number_format = "0.00%"  # Overall Rating (%) is column P
        for col in range(8, 14):
            row[col - 1].number_format = "0.00"
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
