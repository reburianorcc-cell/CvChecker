import streamlit as st
import base64
import io
from pathlib import Path
from html import escape
from cv_skills import extract_skills_licenses
from html import escape as html_escape
from docx import Document
from collections import defaultdict
from auth import logout, require_login
from database import delete_evaluation, get_attachment, get_evaluation, initialize_database, list_evaluations, list_all_evaluations_for_export
from evaluator import evaluation_form
from excel_report import create_excel, create_all_evaluations_excel
from ui import detail_grid, inject_styles, metric_grid, page_header

@st.dialog("Non-Key Qualification Overview",width="large")
def non_key_overview(evaluation_id):
    data=get_evaluation(evaluation_id)
    if not data:
        st.error("Evaluation not found."); return
    metric_grid([("Candidate Name",data.get("candidate_name")),("TOR",data.get("tor_name") or "Unspecified"),("Score Average",f"{float(data.get('total_score') or 0):.2f}%"),("Decision",data.get("decision") or "FAIL")])
    candidate_information=[
        {"Field":"Project Name","Information":data.get("project_name") or "Not provided"},
        {"Field":"Candidate Name","Information":data.get("candidate_name") or "Not provided"},
        {"Field":"Age","Information":data.get("age") or "Not provided"},
        {"Field":"Number","Information":data.get("candidate_number") or data.get("mobile") or "Not provided"},
        {"Field":"Email","Information":data.get("email") or "Not provided"},
        {"Field":"Applied Position","Information":data.get("applied_position") or "Not provided"},
    ]
    st.markdown("#### Candidate Information")
    st.dataframe(
        candidate_information,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Field":st.column_config.TextColumn("Field",width="small"),
            "Information":st.column_config.TextColumn("Information",width="large"),
        },
    )
    table=[{"Criteria":item["criterion"],"Weight":f"{item['weight']:.0%}","Qualification":item["selected"],"Rating":f"{item['rating']:.0%}","Points":f"{item['points']:.2f}"} for item in data.get("criteria",[])]
    st.dataframe(table,use_container_width=True,hide_index=True)

@st.dialog("Delete Evaluation")
def confirm_delete(evaluation_id,candidate_name):
    st.warning(f"Delete the saved evaluation for {candidate_name}? This also removes the uploaded CV and cannot be undone.")
    left,right=st.columns(2)
    if left.button("Cancel",use_container_width=True): st.rerun()
    if right.button("Delete permanently",type="primary",use_container_width=True):
        if delete_evaluation(evaluation_id):
            st.session_state.pop("selected_evaluation",None); st.success("Evaluation deleted."); st.rerun()
        else: st.error("Evaluation could not be found.")


def render_cv_preview(filename, content):
    """Preview stored CV bytes without publishing them to a public URL."""
    extension = Path(filename or "").suffix.lower()
    if isinstance(content, memoryview):
        content = content.tobytes()
    if not isinstance(content, bytes):
        content = bytes(content)
    if extension == ".pdf":
        encoded = base64.b64encode(content).decode("ascii")
        st.components.v1.html(
            '<iframe title="Candidate CV PDF preview" '
            'src="data:application/pdf;base64,' + encoded + '" '
            'style="width:100%;height:650px;border:1px solid #dce6f2;border-radius:10px;"></iframe>',
            height=675, scrolling=False,
        )
        st.caption("If your browser blocks embedded PDFs, use Download original CV below.")
    elif extension == ".docx":
        document = Document(io.BytesIO(content))
        sections = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                sections.append(f'<p>{html_escape(paragraph.text)}</p>')
        for table in document.tables:
            rows = []
            for row in table.rows:
                cells = ''.join(f'<td>{html_escape(cell.text)}</td>' for cell in row.cells)
                rows.append(f'<tr>{cells}</tr>')
            sections.append('<table>' + ''.join(rows) + '</table>')
        st.markdown('''<div style="height:510px;overflow-y:auto;padding:20px;border:1px solid #dce6f2;border-radius:10px;background:white;color:#1e3554;line-height:1.6;">
          <style>table{border-collapse:collapse;width:100%;margin:12px 0}td{border:1px solid #dce6f2;padding:6px}</style>''' + ''.join(sections) + '</div>', unsafe_allow_html=True)
        st.caption("Text preview of the Word document; original formatting may differ.")
    elif extension == ".txt":
        st.text_area("CV content", content.decode("utf-8", errors="replace"), height=510, disabled=True)
    else:
        st.info("Preview is supported for PDF, DOCX and TXT files. Download this CV to view it.")


def category_of(record):
    """Local is the historical stored name for National."""
    category = str(record.get("key_scope") or "").strip().lower()
    if category in ("local", "national"):
        return "National"
    if category == "international":
        return "International"
    return "Unspecified"

@st.dialog("Candidate Evaluation Details", width="large")
def evaluation_details(evaluation_id):
    from html import escape
    data = get_evaluation(evaluation_id)
    if not data:
        st.error("Evaluation not found.")
        return

    def safe(value, default="Not provided"):
        return escape(str(value)) if value is not None and str(value).strip() else default

    score = float(data.get("total_score") or 0)
    decision = data.get("decision") or data.get("result") or "Pending"
    passed = str(decision).upper() in ("PASS", "QUALIFIED")
    candidate_name = str(data.get("candidate_name") or "Unnamed Candidate")
    initials = "".join(part[0] for part in candidate_name.split()[:2]).upper()
    classification = data.get("key_classification") or "Non-Key"
    tor = data.get("tor_name") or "Unspecified TOR"
    st.markdown(f"""
    <div class="cv-modal-top">
      <div class="cv-modal-kicker">CANDIDATE PROFILE <span>•</span> {safe(tor)}</div>
      <div class="cv-modal-hero">
        <div class="cv-modal-avatar">{safe(initials)}</div>
        <div class="cv-modal-person"><div class="cv-modal-name">{safe(candidate_name)}</div>
          <div class="cv-modal-meta">{safe(data.get('pos_level'))} <span>•</span> {safe(classification)} Personnel</div>
          <div class="cv-modal-project">{safe(data.get('project_name'), 'Project not specified')}</div>
        </div>
        <div class="cv-modal-result"><div class="cv-modal-score">{score:.2f}<span>%</span></div>
          <span class="cv-modal-status {'pass' if passed else 'fail'}">{safe(decision)}</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    overview, qualifications, notes = st.tabs(["Overview", "Qualifications", "Skills & Remarks"])
    with overview:
        st.markdown('<div class="cv-modal-section-title">Personal & project information</div>', unsafe_allow_html=True)
        fields = [
            ("Applied position", data.get("applied_position")),
            ("Project", data.get("project_name")),
            ("Age", data.get("age")),
            ("Phone number", data.get("candidate_number") or data.get("mobile")),
            ("Email address", data.get("email")),
            ("Professional level", data.get("pos_level")),
            ("Evaluation date", data.get("evaluation_date")),
            ("Key category", data.get("key_scope") or "Not applicable"),
        ]
        st.markdown('<div class="cv-modal-info-grid">' + ''.join(
            f'<div class="cv-modal-info"><div class="cv-modal-label">{safe(label)}</div><div class="cv-modal-value">{safe(value)}</div></div>'
            for label, value in fields
        ) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="cv-modal-section-title">Evaluation Insights — Automatic Assessment</div>', unsafe_allow_html=True)
        st.caption("All four categories are checked from the same six-criteria score. "
                   "Key International uses the existing 70% rule; the other categories "
                   "use the existing 50% rule. Non-Key results do not display percentages. "
                   "Separate Non-Key eligibility criteria have not been supplied.")
        for group, geography, threshold in [
            ("Key", "International", 70),
            ("Key", "National", 50),
            ("Non-Key", "International", 50),
            ("Non-Key", "National", 50),
        ]:
            status = "PASS" if score >= threshold else "FAIL"
            with st.container(border=True):
                label_col, status_col, rating_col = st.columns([3, 1, 1], vertical_alignment="center")
                label_col.markdown(f"**{group} — {geography}**")
                status_col.markdown(f":{'green' if status == 'PASS' else 'red'}[**{status}**]")
                rating_col.markdown(f"**{score:.2f}%**" if group == "Key" else "—")
    with qualifications:
        st.markdown('<div class="cv-modal-section-title">TOR qualification preview</div>', unsafe_allow_html=True)
        tor_rows = data.get("tor_assessment") or []
        if tor_rows:
            outcome = data.get("tor_assessment_outcome") or "Automatic TOR screening"
            explanation = data.get("tor_assessment_explanation") or ""
            st.info(f"**{outcome}** — {explanation}")
            # Full-width, wrapping TOR requirement cards (no horizontal or nested table scrolling).
            st.markdown("""<style>
            .tor-detail-card {border:1px solid #dce7f3;border-radius:12px;padding:15px 18px;
                margin:10px 0;background:#ffffff;box-shadow:0 2px 8px rgba(22,55,90,.035);
                overflow-wrap:anywhere;word-break:normal}
            .tor-detail-card .tor-label {font-size:11px;font-weight:750;letter-spacing:.065em;
                color:#54749a;text-transform:uppercase;margin-bottom:5px}
            .tor-detail-card .tor-requirement {font-size:14px;font-weight:650;color:#173454;
                line-height:1.5;margin-bottom:11px}
            .tor-detail-card .tor-evidence {font-size:13px;line-height:1.55;color:#2c455d}
            .tor-detail-card .tor-reason {font-size:12px;line-height:1.55;color:#64758a;margin-top:7px}
            .tor-status {display:inline-block;padding:4px 10px;border-radius:999px;
                font-size:11px;font-weight:750;margin-bottom:9px}
            .tor-status-supported {background:#e1f6ec;color:#087c55}
            .tor-status-partial {background:#fff3d7;color:#936100}
            .tor-status-gap {background:#fde8e9;color:#b53541}
            .tor-status-unverified {background:#eaf0f7;color:#47617c}
            </style>""", unsafe_allow_html=True)
            from html import escape as _tor_escape
            for idx, item in enumerate(tor_rows, start=1):
                requirement = _tor_escape(str(item.get("TOR requirement") or "Not specified"))
                status = str(item.get("Automatic assessment") or "Not verified")
                evidence = _tor_escape(str(item.get("Evidence") or "None identified"))
                explanation = _tor_escape(str(item.get("Explanation") or ""))
                status_style = ("supported" if status.startswith("Evidence found") else
                                "partial" if status.startswith("Partial") else
                                "gap" if status.startswith("Potential") else "unverified")
                st.markdown(f"""<div class="tor-detail-card">
                    <div class="tor-label">Requirement {idx:02d}</div>
                    <div class="tor-requirement">{requirement}</div>
                    <span class="tor-status tor-status-{status_style}">{_tor_escape(status)}</span>
                    <div class="tor-evidence"><strong>CV evidence:</strong> {evidence}</div>
                    <div class="tor-reason"><strong>Assessment:</strong> {explanation}</div>
                    </div>""", unsafe_allow_html=True)
            st.caption("Automated TOR screening is provisional. Supporting CV statements and credential validity are not independently verified.")
        else:
            st.info("No TOR-to-CV qualification assessment was saved for this candidate. Re-evaluate the candidate with both a TOR and CV uploaded to generate this preview.")
        st.markdown('<div class="cv-modal-section-title">Qualification score breakdown</div>', unsafe_allow_html=True)
        table = [{"Criteria": item.get("criterion"), "Weight": f"{float(item.get('weight') or 0):.0%}",
                  "Selected level": item.get("selected"), "Rating": f"{float(item.get('rating') or 0):.0%}",
                  "Points": f"{float(item.get('points') or 0):.2f}"} for item in data.get("criteria", [])]
        if table:
            st.dataframe(table, use_container_width=True, hide_index=True)
        else:
            st.info("No qualification criteria saved for this evaluation.")
    with notes:
        st.markdown('<div class="cv-modal-section-title">Skills, certifications & remarks</div>', unsafe_allow_html=True)
        detected_profile = extract_skills_licenses(data.get("extracted_cv_text") or "")
        detail_grid([("Technical skills", data.get("skills") or detected_profile["skills"]),
                     ("Licenses / certifications", data.get("licenses") or detected_profile["licenses"]),
                     ("Evaluator remarks", data.get("remarks"))])
    st.caption("Evaluation results should be reviewed by an authorized evaluator before use in hiring decisions.")
    edit_button, close_button = st.columns(2)
    with edit_button:
        if st.button("✎ Re-evaluate this candidate", key=f"detail_edit_{evaluation_id}",
                     type="primary", use_container_width=True):
            st.session_state["reevaluate_id"] = evaluation_id
            st.session_state["main_navigation"] = "new"
            st.rerun()
    with close_button:
        if st.button("Close", key=f"close_details_{evaluation_id}", use_container_width=True):
            st.rerun()

def decision_of(record):
    return str(record.get("decision") or ("PASS" if record.get("result") == "QUALIFIED" else "FAIL")).upper()

def candidate_listing(records, prefix="list"):
    """Responsive candidate cards with the existing details, Excel, CV and delete actions."""
    from html import escape
    if not records:
        st.info("No candidates match the selected filters.")
        return
    for record in records:
        evaluation_id = record["id"]
        name = str(record.get("candidate_name") or "Unnamed candidate")
        initials = "".join(word[0] for word in name.split()[:2]).upper()
        decision = decision_of(record)
        passed = decision == "PASS"
        with st.container(border=True):
            name_col, result_col, view_col, edit_col, more_col = st.columns(
                [3.25, 1.05, 1.25, 1.45, .55], gap="small", vertical_alignment="center"
            )
            with name_col:
                st.markdown(
                    f'<div class="candidate-row-name"><span class="candidate-avatar">{escape(initials)}</span>'
                    f'<span><strong>{escape(name)}</strong><small>{escape(str(record.get("applied_position") or "Position not specified"))}'
                    f' · {escape(str(record.get("pos_level") or ""))} · {escape(str(record.get("key_classification") or "Non-Key"))}</small></span></div>',
                    unsafe_allow_html=True
                )
            with result_col:
                st.markdown(
                    f'<div class="candidate-row-result"><strong>{float(record.get("total_score") or 0):.1f}%</strong>'
                    f'<span class="status-pill {"pass" if passed else "fail"}">{"Qualified" if passed else "Not qualified"}</span></div>',
                    unsafe_allow_html=True
                )
            with view_col:
                if st.button("View details", key=f"{prefix}_view_{evaluation_id}", use_container_width=True):
                    evaluation_details(evaluation_id)
            with edit_col:
                if st.button("✎ Re-evaluate", key=f"{prefix}_reevaluate_{evaluation_id}",
                             type="primary", use_container_width=True):
                    st.session_state["reevaluate_id"] = evaluation_id
                    st.session_state["main_navigation"] = "new"
                    st.rerun()
            with more_col:
                with st.popover("⋯", use_container_width=True):
                    st.caption("Candidate actions")
                    data = get_evaluation(evaluation_id)
                    if data:
                        evaluation_date = str(record.get("evaluation_date") or "no_date").replace("/", "-")
                        filename = f"{name.replace(' ', '_')}_{evaluation_date}.xlsx"
                        st.download_button("Download Excel", create_excel(data), filename,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"{prefix}_excel_{evaluation_id}", use_container_width=True)
                    original_name, original_file = get_attachment(evaluation_id)
                    if original_file:
                        st.download_button("Download CV", original_file, original_name or "candidate_cv",
                            key=f"{prefix}_cv_{evaluation_id}", use_container_width=True)
                    else:
                        st.caption("No original CV attached")
                    st.divider()
                    if st.button("Delete evaluation", key=f"{prefix}_delete_{evaluation_id}", use_container_width=True):
                        confirm_delete(evaluation_id, name)

def dashboard(records):
    page_header("Personnel evaluation / Overview", "CV Evaluations",
                "Review candidate assessments and manage qualified personnel.")
    total = len(records)
    passed = sum(decision_of(r) == "PASS" for r in records)
    failed = total - passed
    key_count = sum((r.get("key_classification") or "Non-Key") == "Key" for r in records)
    average = sum(float(r.get("total_score") or 0) for r in records) / total if total else 0
    metric_grid([
        ("Total candidates", total),
        ("Qualified", f"{passed} · {passed / total:.0%}" if total else "0"),
        ("Not qualified", f"{failed} · {failed / total:.0%}" if total else "0"),
        ("Average score", f"{average:.1f}%")
    ])
    if not records:
        st.info("No evaluations yet. Choose New Evaluation to upload and assess your first CV.")
        if st.button("＋ New evaluation", type="primary"):
            st.session_state.main_navigation = "new"
            st.rerun()
        return
    st.markdown('<div class="section-heading">Candidate directory <span>Filter and open saved assessments</span></div>', unsafe_allow_html=True)
    search_col, level_col, result_col = st.columns([2.3, 1.2, 1.2])
    with search_col:
        query = st.text_input("Search candidates", placeholder="Search name or position…", key="dash_search")
    with level_col:
        level = st.selectbox("Professional level", ["All levels", "Pro A", "Pro B", "Pro C"], key="dash_level")
    with result_col:
        result = st.selectbox("Overall result", ["All results", "PASS", "FAIL"], key="dash_result")
    filtered = [r for r in records
        if (not query or query.lower() in str(r.get("candidate_name") or "").lower()
            or query.lower() in str(r.get("applied_position") or "").lower())
        and (level == "All levels" or str(r.get("pos_level") or "") == level)
        and (result == "All results" or decision_of(r) == result)
    ]
    st.caption(f"Showing {len(filtered)} of {total} candidates · {key_count} Key personnel")
    candidate_listing(filtered, "dash")

st.set_page_config(page_title="CV Checker Admin",page_icon="📄",layout="wide",initial_sidebar_state="expanded")
inject_styles(); require_login()
try:
    initialize_database()
except RuntimeError as exc:
    st.error(str(exc))
    st.info("Local setup: use .streamlit/secrets.toml. Streamlit Cloud: paste the same TOML under App settings → Secrets, save it, then reboot the app.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="brand-mark">◉</span><span>Oriental Consultant<br>Philippines Inc.<small>CV Checker Portal</small></span></div>', unsafe_allow_html=True)

    st.divider()
    # Button-based navigation: no radio circles or duplicate CSS-generated icons.
    navigation=[
        ("dashboard","CV Evaluations",":material/assignment_ind:"),
        ("new","New Evaluation",":material/note_add:"),
    ]
    for nav_id,nav_label,nav_icon in navigation:
        active=st.session_state.get("main_navigation","dashboard")==nav_id
        with st.container(key=f"nav_{nav_id}_{'active' if active else 'idle'}"):
            if st.button(nav_label,icon=nav_icon,key=f"nav_button_{nav_id}",use_container_width=True):
                st.session_state.main_navigation=nav_id
                if nav_id=="new":
                    st.session_state.pop("reevaluate_id",None)
                st.rerun()
    st.caption("Build: CV-PREVIEW-REVIEW-20261019-B")
    page=st.session_state.get("main_navigation","dashboard")
    st.divider()
    st.caption("Signed in as Administrator")
    if st.button("↪ Log out",use_container_width=True): logout()

if page=="dashboard":
    dashboard(list_evaluations())
elif page=="new":
    reevaluate_id=st.session_state.get("reevaluate_id")
    if reevaluate_id is not None:
        existing=get_evaluation(reevaluate_id)
        if existing:
            page_header("Evaluation workspace","Re-evaluate Candidate",
                        "Review and edit the saved evaluation. Updating will replace the previous scores.")
            if st.button("← Cancel re-evaluation",key="cancel_reevaluation"):
                st.session_state.pop("reevaluate_id",None)
                st.session_state.main_navigation="dashboard"
                st.rerun()
            evaluation_form(show_title=False,existing=existing,evaluation_id=reevaluate_id)
        else:
            st.error("The selected evaluation could not be found.")
            if st.button("Return to CV Evaluations"):
                st.session_state.pop("reevaluate_id",None)
                st.session_state.main_navigation="dashboard"
                st.rerun()
    else:
        page_header("Evaluation workspace","New CV Evaluation",
                    "Upload a CV, review the qualifications, and save the completed assessment.")
        evaluation_form(show_title=False)
else:
    page_header("Personnel evaluation / Records", "Saved CV Evaluations",
                "Search existing assessments, review candidate details, and download evaluation reports.")
    records = list_evaluations()
    if records:
        export_col, count_col = st.columns([1.25, 3], vertical_alignment="center")
        with export_col:
            if st.button("↓ Prepare all records (Excel)", key="prepare_all_excel", use_container_width=True):
                try:
                    with st.spinner("Collecting all saved evaluations..."):
                        all_records = list_all_evaluations_for_export()
                        st.session_state["all_evaluations_export"] = create_all_evaluations_excel(all_records)
                        st.session_state["all_evaluations_count"] = len(all_records)
                except Exception as exc:
                    st.error(f"Could not prepare Excel export: {exc}")
        with count_col:
            st.caption("Exports every saved evaluation, regardless of the filters below.")
        if st.session_state.get("all_evaluations_export"):
            st.download_button("Download All Records (.xlsx)", st.session_state["all_evaluations_export"],
                file_name="CV_Checker_All_Evaluations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all_excel")
            st.caption(f"Prepared {st.session_state.get('all_evaluations_count', 0)} candidate records.")
    if not records:
        st.info("No saved evaluations yet. Open New Evaluation to create your first record.")
    else:
        search_col, level_col, result_col = st.columns([2.5, 1.1, 1.1])
        with search_col:
            search = st.text_input("Search candidates", placeholder="Search name or applied position…", key="saved_search")
        with level_col:
            pos_filter = st.selectbox("Professional Level", ["All levels", "Pro A", "Pro B", "Pro C"], key="saved_professional_level")
        with result_col:
            status_filter = st.selectbox("Overall result", ["All results", "Qualified", "Not qualified"], key="saved_result")
        records = [r for r in records
            if (not search or search.lower() in str(r.get("candidate_name") or "").lower()
                or search.lower() in str(r.get("applied_position") or "").lower())
            and (pos_filter == "All levels" or str(r.get("pos_level") or "").strip().lower() == pos_filter.lower())
            and (status_filter == "All results" or (decision_of(r) == "PASS") == (status_filter == "Qualified"))]
        st.caption(f"Showing {len(records)} saved evaluations")
        candidate_listing(records, "saved")
