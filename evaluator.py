from datetime import date
import hashlib
import streamlit as st
from config import ACADEMIC, ELIGIBILITY, POSITIONS, TRAINING
from cv_extract import extract_text, extracted_identity
from auto_analyzer import analyze_cv
from database import save_evaluation, update_evaluation, list_saved_tors, get_saved_tor, save_tor
from tor_matcher import extract_requirements, compare_requirements, summarize_assessment

def classify_evaluation(declared_classification,key_scope,total_score):
    final_classification=declared_classification
    if declared_classification=="Key" and key_scope=="International" and total_score<70:
        final_classification="Non-Key"
    pass_mark=70 if final_classification=="Key" and key_scope=="International" else 50
    return final_classification,"PASS" if total_score>=pass_mark else "FAIL"

def evaluation_form(show_title=True, existing=None, evaluation_id=None):
    existing = existing or {}
    editing = evaluation_id is not None
    def prior(key, default=""):
        value = existing.get(key)
        return default if value is None else value
    prior_criteria = {str(item.get("criterion", "")).lower(): item.get("selected")
                      for item in existing.get("criteria", []) if isinstance(item, dict)}
    def prior_score(prefix):
        return next((value for key, value in prior_criteria.items()
                     if key.startswith(prefix.lower())), None)
    if editing:
        st.info(f"Re-evaluating: {prior('candidate_name', 'Candidate')} — changes will update the existing record.")

    if show_title: st.title("New CV Evaluation")
    position_options=list(POSITIONS)
    prior_position=prior("pos_level",position_options[0])
    pos=st.selectbox("Professional level",position_options,
        index=position_options.index(prior_position) if prior_position in position_options else 0)
    st.info(POSITIONS[pos]["description"])
    st.markdown("#### Project TOR requirements")
    st.caption("Select a previously saved TOR or upload a new one. Saved TORs are shared through Supabase and can be reused for future CV assessments.")
    try:
        saved_tors = list_saved_tors()
        library_ready = True
    except Exception as exc:
        saved_tors = []
        library_ready = False
        st.error("TOR library is unavailable. Run `tor_library_schema.sql` in the Supabase SQL Editor, then refresh. Details: " + str(exc))
    tor_choices = {f"{item['name']} ({item['filename']})": item['id'] for item in saved_tors}
    options = ["Upload new TOR"] + list(tor_choices)
    selected = st.selectbox("Select project TOR", options, key="selected_tor_library")
    tor_text = ""
    requirements = []
    tor_library_id = None
    tor_name = ""
    if selected != "Upload new TOR":
        tor_library_id = tor_choices[selected]
        try:
            selected_tor = get_saved_tor(tor_library_id)
            tor_text = selected_tor.get("tor_text") or ""
            requirements = selected_tor.get("requirements") or []
            tor_name = selected_tor.get("name") or ""
            st.success(f"Using saved TOR: {tor_name} — {len(requirements)} requirements loaded")
        except Exception as exc:
            st.error(f"Unable to load selected TOR: {exc}")
    else:
        tor_name = st.text_input("TOR / project name", value=prior("tor_name") if editing else "", placeholder="e.g. Project Engineer — Road Rehabilitation")
        tor_file = st.file_uploader("Upload TOR (once)", type=["pdf", "docx", "txt"], key="tor_requirements_upload")
        if tor_file is not None:
            try:
                tor_text = extract_text(tor_file)
                requirements = extract_requirements(tor_text) if tor_text.strip() else []
                if requirements:
                    st.success(f"Extracted {len(requirements)} requirements from {tor_file.name}")
                    if st.button("Save TOR to library", disabled=not library_ready, type="primary"):
                        new_id = save_tor(tor_name, tor_file.name, tor_text, requirements)
                        st.session_state["new_saved_tor_id"] = new_id
                        st.success("TOR saved. Select it from the saved TOR dropdown on future evaluations.")
                else:
                    st.warning("No qualification requirements extracted. Check that the TOR contains selectable text.")
            except Exception as exc:
                st.error(f"Could not process TOR: {exc}")
    if requirements:
        with st.expander(f"Extracted TOR requirements ({len(requirements)})"):
            for i, requirement in enumerate(requirements, 1):
                st.write(f"{i}. {requirement}")
    elif selected == "Upload new TOR":
        st.info("Upload and save a TOR once. Next time, select it from the library and upload only the candidate CV.")
    st.caption("Automatic assessment: Key International, Key National, "
               "Non-Key International and Non-Key National will all be checked. "
               "No manual classification selection is required.")
    st.markdown('<div class="form-section-heading">02 <span>Upload candidate CV</span></div>', unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload CV",type=["pdf","docx","txt"],help="Supported formats: PDF, DOCX, TXT")
    text=prior("extracted_cv_text") if editing else ""
    if uploaded:
        try:
            with st.spinner("Uploading and analyzing CV..."): text=extract_text(uploaded)
            st.success(f"Automatically uploaded and extracted: {uploaded.name}")
        except Exception as exc: st.error(str(exc))
    suggested_name,suggested_email,suggested_phone=extracted_identity(text)
    if editing:
        suggested_name=prior("candidate_name",suggested_name)
        suggested_email=prior("email",suggested_email)
        suggested_phone=prior("mobile",prior("candidate_number",suggested_phone))
    analysis=analyze_cv(text,pos) if text.strip() else None
    tor_rows = []
    tor_outcome = None
    tor_explanation = None
    if requirements and text.strip():
        st.markdown("#### Automatic TOR-to-CV assessment")
        tor_rows = compare_requirements(requirements, text)
        tor_outcome, tor_explanation = summarize_assessment(tor_rows)
        st.info(f"**{tor_outcome}** — {tor_explanation}")
        st.dataframe(tor_rows, hide_index=True, use_container_width=True)
        st.caption("Automatic provisional screening only. The tool cannot authenticate qualifications, infer missing experience, or certify compliance with the TOR.")
    elif requirements:
        st.info("Upload a CV to compare its extracted text against the TOR requirements.")
    # Each uploaded CV / professional level gets its own widget identity.
    # This prevents stale selections from a previous candidate from carrying over.
    signature=(f"edit_{evaluation_id}_{pos}" if editing else
               (hashlib.sha256((pos+"\n"+text).encode()).hexdigest()[:12]
                if text.strip() else "empty_"+pos))
    if analysis:
        st.info("CV extracted. Suggested selections below are preliminary; please review them before saving.")
        with st.expander("Detected qualifications and items to verify"):
            for field,value in analysis["suggestions"].items():
                st.write(f"**{field.title()}:** {value} — {analysis['evidence'].get(field,'')}")
            for warning in analysis["warnings"]:
                st.write("• " + warning)
    elif uploaded:
        st.warning("No readable CV text found. Please enter the qualifications manually.")

    def scoring_selectbox(label, mapping, field):
        options=list(mapping)
        if "None" not in options: options.append("None")
        suggested=(analysis or {}).get("suggestions",{}).get(field)
        previous=prior_score({"academic":"academic qualification","training":"number of relevant trainings",
            "professional":"total professional experience","relevant":"relevant experience for",
            "projects":"philippines/similar geographic experience",
            "eligibility":"eligibility"}[field]) if editing else None
        default=previous if previous in options else (suggested if suggested in options else "None")
        return st.selectbox(label, options, index=options.index(default),key=f"cv_{signature}_{field}")

    # Brief scoring explanation placed directly above the candidate information form.
    st.markdown('<div class="form-section-heading"><span>Evaluation criteria & computation</span></div>', unsafe_allow_html=True)
    st.caption(
        "Academic Qualification (15%) · Relevant Trainings (10%) · "
        "Professional Experience (20%) · Relevant Experience (40%) · "
        "Geographic Experience (10%) · Eligibility (5%)"
    )
    st.markdown("**Overall Score = Σ (Criterion Rating × Criterion Weight) × 100**")
    st.caption(
        "PASS: Key International ≥ 70%; Key National, Non-Key International "
        "and Non-Key National ≥ 50%. Below the applicable threshold = FAIL. "
        "All four categories use the same weighted score."
    )

    st.markdown('<div class="form-section-heading">03 <span>Candidate information & qualifications</span></div>', unsafe_allow_html=True)
    with st.form("evaluation_form"):
        c1,c2=st.columns(2)
        with c1:
            project_name=st.text_input("Project name",value=prior("project_name"))
            name=st.text_input("Candidate name",suggested_name)
            applied=st.text_input("Applied position",value=prior("applied_position"))
            email=st.text_input("Email",suggested_email)
            phone=st.text_input("Number",suggested_phone)
        with c2:
            age=st.number_input("Age",min_value=15,max_value=100,value=max(15,min(100,int(prior("age",25) or 25))),step=1)
            sex_options=["Not specified","Male","Female","Prefer not to say"]
            old_sex=prior("sex","Not specified")
            sex=st.selectbox("Sex",sex_options,index=sex_options.index(old_sex) if old_sex in sex_options else 0)
            saved_date=prior("evaluation_date")
            try: default_date=date.fromisoformat(str(saved_date)[:10]) if editing and saved_date else date.today()
            except (ValueError,TypeError): default_date=date.today()
            evaluation_date=st.date_input("Evaluation date",default_date)
            academic=scoring_selectbox("Academic qualification — 15%",ACADEMIC,"academic")
            training=scoring_selectbox("Relevant trainings — 10%",TRAINING,"training")
        professional=scoring_selectbox("Professional experience — 20%",POSITIONS[pos]["professional"],"professional")
        relevant=scoring_selectbox(f"Relevant experience for {pos} — 40%",POSITIONS[pos]["relevant"],"relevant")
        projects=scoring_selectbox("Philippines/similar geographic experience — 10%",POSITIONS[pos]["projects"],"projects")
        eligibility=scoring_selectbox("Eligibility — 5%",ELIGIBILITY,"eligibility")
        skills=st.text_area("Technical skills (maximum 3)",value=prior("skills"))
        licenses=st.text_area("Licenses / certifications / affiliations",value=prior("licenses"))
        remarks=st.text_area("Evaluation remarks",value=prior("remarks"))
        submitted=st.form_submit_button("Update Evaluation" if editing else "Save Evaluation",type="primary",use_container_width=True)
    if submitted:
        if not project_name.strip() or not name.strip() or not applied.strip() or not tor_name.strip(): st.error("Project name, TOR, candidate name, and applied position are required."); return
        items=[("Academic Qualification",.15,academic,ACADEMIC.get(academic,0)),("Number of Relevant Trainings",.10,training,TRAINING.get(training,0)),("Total Professional Experience",.20,professional,POSITIONS[pos]["professional"][professional]),(f"Relevant Experience for {pos}",.40,relevant,POSITIONS[pos]["relevant"][relevant]),("Philippines/Similar Geographic Experience",.10,projects,POSITIONS[pos]["projects"][projects]),("Eligibility",.05,eligibility,ELIGIBILITY.get(eligibility,0))]
        criteria=[{"criterion":a,"weight":b,"selected":c,"rating":d,"points":100*b*d} for a,b,c,d in items]
        total=sum(item["points"] for item in criteria)
        # Backward-compatible primary result for legacy database fields.
        # All four category results are derived from this same score in View Details.
        final_classification = "Key" if total >= 50 else "Non-Key"
        key_scope = "International" if total >= 70 else "Local"
        declared_classification = "Automatic"
        decision = "PASS" if total >= 50 else "FAIL"
        data={"project_name":project_name.strip(),"tor_name":tor_name.strip(),"candidate_name":name.strip(),"age":int(age),"candidate_number":phone,"pos_level":pos,"applied_position":applied.strip(),"declared_classification":declared_classification,"key_classification":final_classification,"key_scope":key_scope,"decision":decision,"email":email,"mobile":phone,"sex":sex,"evaluation_date":evaluation_date.isoformat(),"total_score":total,"overall_percentage":total,"result":"QUALIFIED" if decision=="PASS" else "NOT QUALIFIED","skills":skills,"licenses":licenses,"remarks":remarks,"criteria":criteria,"extracted_cv_text":text,"source_filename":uploaded.name if uploaded else prior("source_filename"),
              "source_file":uploaded.getvalue() if uploaded else None,
              "tor_requirements": requirements if requirements else prior("tor_requirements", []),
              "tor_library_id": tor_library_id,
              "tor_assessment": tor_rows if requirements and text.strip() else prior("tor_assessment", []),
              "tor_assessment_outcome": tor_outcome if tor_outcome else prior("tor_assessment_outcome", ""),
              "tor_assessment_explanation": tor_explanation if tor_explanation else prior("tor_assessment_explanation", "") }
        try:
            record_id=update_evaluation(evaluation_id,data) if editing else save_evaluation(data)
            st.success(f"Evaluation #{record_id} {'updated' if editing else 'saved'}: {final_classification} — {decision}.")
            if editing:
                st.session_state.pop("reevaluate_id",None)
                if st.button("Return to Saved Evaluations",key="back_after_update"):
                    st.session_state.main_navigation="saved"
                    st.rerun()
        except Exception as exc:
            st.error(f"Supabase save failed: {exc}")
