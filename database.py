import json
import mimetypes
import re
from datetime import datetime, timezone
from uuid import uuid4
import streamlit as st
from supabase import Client, create_client

BUCKET="File_Checker"
TABLE="cv_evaluations"

@st.cache_resource
def client()->Client:
    try:
        url=st.secrets["supabase"]["url"]
        key=st.secrets["supabase"]["secret_key"]
    except Exception as exc:
        raise RuntimeError("Supabase secrets are missing. Add [supabase] url and secret_key in Streamlit secrets.") from exc
    return create_client(url,key)

def initialize_database():
    supabase=client()
    try:
        supabase.table(TABLE).select("id,project_name,tor_name,client_name,key_classification,decision").limit(1).execute()
    except Exception as exc:
        message=str(exc)
        if "PGRST205" in message or "Could not find the table" in message or "does not exist" in message:
            raise RuntimeError("Supabase is connected, but the cv_evaluations table does not exist. Run supabase_schema.sql in the Supabase SQL Editor.") from exc
        if "PGRST204" in message or "project_name" in message or "key_classification" in message:
            raise RuntimeError("The cv_evaluations table needs the dashboard columns. Run enhance_cv_dashboard.sql once in the Supabase SQL Editor.") from exc
        if "401" in message or "Invalid API key" in message or "JWT" in message:
            raise RuntimeError("Supabase rejected the key. Check that url and secret_key come from the same project and that you used the secret/service_role key.") from exc
        raise RuntimeError(f"Supabase connection failed: {message}") from exc

def _safe_filename(name):
    clean=re.sub(r"[^A-Za-z0-9._-]+","_",name or "cv_file").strip("._")
    return clean or "cv_file"

def save_evaluation(data):
    supabase=client(); storage_path=None
    if data.get("source_file"):
        stamp=datetime.now(timezone.utc).strftime("%Y/%m/%d")
        storage_path=f"evaluations/{stamp}/{uuid4().hex}_{_safe_filename(data.get('source_filename'))}"
        mime=mimetypes.guess_type(data.get("source_filename",""))[0] or "application/octet-stream"
        supabase.storage.from_(BUCKET).upload(storage_path,data["source_file"],{"content-type":mime,"upsert":"false"})
    json_data={key:value for key,value in data.items() if key!="source_file"}
    payload={"candidate_name":data["candidate_name"],"pos_level":data["pos_level"],"applied_position":data["applied_position"],"project_name":data.get("project_name",""),"tor_name":data.get("tor_name",""),"client_name":data.get("client_name",""),"age":data.get("age"),"candidate_number":data.get("candidate_number",""),"key_classification":data.get("key_classification","Non-Key"),"key_scope":data.get("key_scope"),"decision":data.get("decision",data["result"]),"email":data.get("email",""),"mobile":data.get("mobile",""),"sex":data.get("sex",""),"evaluation_date":data["evaluation_date"],"total_score":data["total_score"],"overall_percentage":data["overall_percentage"],"result":data["result"],"details_json":json_data,"source_filename":data.get("source_filename",""),"storage_path":storage_path}
    try:
        response=supabase.table(TABLE).insert(payload).execute()
        return response.data[0]["id"]
    except Exception:
        if storage_path:
            try: supabase.storage.from_(BUCKET).remove([storage_path])
            except Exception: pass
        raise

def update_evaluation(evaluation_id, data):
    """Update the original saved evaluation without creating a duplicate record.

    The original CV attachment and its storage path are retained unless a new
    CV is explicitly supplied. The new attachment is uploaded before the row
    update, and cleaned up if the database update fails.
    """
    supabase = client()
    existing_response = (supabase.table(TABLE)
                         .select("id,source_filename,storage_path")
                         .eq("id", evaluation_id).maybe_single().execute())
    existing = existing_response.data
    if not existing:
        raise ValueError("This saved evaluation no longer exists.")
    old_path = existing.get("storage_path")
    new_path = None
    source_filename = existing.get("source_filename") or ""
    if data.get("source_file"):
        stamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        source_filename = data.get("source_filename") or "candidate_cv"
        new_path = f"evaluations/{stamp}/{uuid4().hex}_{_safe_filename(source_filename)}"
        mime = mimetypes.guess_type(source_filename)[0] or "application/octet-stream"
        supabase.storage.from_(BUCKET).upload(
            new_path, data["source_file"], {"content-type": mime, "upsert": "false"})
    else:
        data["source_filename"] = source_filename
    json_data = {key: value for key, value in data.items() if key != "source_file"}
    payload = {
        "candidate_name": data["candidate_name"], "pos_level": data["pos_level"],
        "applied_position": data["applied_position"],
        "project_name": data.get("project_name", ""),
        "tor_name": data.get("tor_name", ""),
        "age": data.get("age"),
        "candidate_number": data.get("candidate_number", ""),
        "key_classification": data.get("key_classification", "Non-Key"),
        "key_scope": data.get("key_scope"), "decision": data["decision"],
        "email": data.get("email", ""), "mobile": data.get("mobile", ""),
        "sex": data.get("sex", ""), "evaluation_date": data["evaluation_date"],
        "total_score": data["total_score"],
        "overall_percentage": data["overall_percentage"], "result": data["result"],
        "details_json": json_data, "source_filename": source_filename,
        "storage_path": new_path or old_path,
    }
    try:
        supabase.table(TABLE).update(payload).eq("id", evaluation_id).execute()
    except Exception:
        if new_path:
            try: supabase.storage.from_(BUCKET).remove([new_path])
            except Exception: pass
        raise
    if new_path and old_path:
        try: supabase.storage.from_(BUCKET).remove([old_path])
        except Exception: pass
    return evaluation_id


def list_evaluations():
    response=client().table(TABLE).select("id,candidate_name,pos_level,applied_position,project_name,tor_name,client_name,age,candidate_number,key_classification,key_scope,decision,email,mobile,sex,evaluation_date,total_score,overall_percentage,result,source_filename,created_at").order("created_at",desc=True).execute()
    return response.data or []

def get_evaluation(evaluation_id):
    response=client().table(TABLE).select("details_json").eq("id",evaluation_id).maybe_single().execute()
    value=response.data.get("details_json") if response.data else None
    return json.loads(value) if isinstance(value,str) else value

def get_attachment(evaluation_id):
    response=client().table(TABLE).select("source_filename,storage_path").eq("id",evaluation_id).maybe_single().execute()
    if not response.data or not response.data.get("storage_path"): return None,None
    return response.data.get("source_filename"),client().storage.from_(BUCKET).download(response.data["storage_path"])

def delete_attachment(evaluation_id):
    supabase=client()
    response=supabase.table(TABLE).select("storage_path,details_json").eq("id",evaluation_id).maybe_single().execute()
    if not response.data or not response.data.get("storage_path"): return False
    supabase.storage.from_(BUCKET).remove([response.data["storage_path"]])
    details=response.data.get("details_json") or {}
    if isinstance(details,str): details=json.loads(details)
    details["source_filename"]=""
    supabase.table(TABLE).update({"source_filename":None,"storage_path":None,"details_json":details}).eq("id",evaluation_id).execute()
    return True

def delete_evaluation(evaluation_id):
    supabase=client()
    response=supabase.table(TABLE).select("storage_path").eq("id",evaluation_id).maybe_single().execute()
    if not response.data: return False
    storage_path=response.data.get("storage_path")
    supabase.table(TABLE).delete().eq("id",evaluation_id).execute()
    if storage_path:
        try: supabase.storage.from_(BUCKET).remove([storage_path])
        except Exception: pass
    return True


def list_all_evaluations_for_export(batch_size=500):
    """Fetch every saved evaluation, including full scoring details, without row limits."""
    supabase = client()
    results = []
    start = 0
    while True:
        response = (supabase.table(TABLE)
            .select("id,candidate_name,age,applied_position,email,mobile,candidate_number,pos_level,total_score,overall_percentage,details_json")
            .order("id").range(start, start + batch_size - 1).execute())
        batch = response.data or []
        results.extend(batch)
        if len(batch) < batch_size:
            break
        start += batch_size
    return results


# TOR library: saved independently from candidate evaluations.
TOR_TABLE = "cv_tor_library"

def list_saved_tors():
    response = client().table(TOR_TABLE).select("id,name,filename,requirements,created_at").order("name").execute()
    return response.data or []

def get_saved_tor(tor_id):
    response = client().table(TOR_TABLE).select("*").eq("id",tor_id).single().execute()
    return response.data

def save_tor(name, filename, text, requirements):
    name = name.strip()
    if not name or not text.strip() or not requirements:
        raise ValueError("A TOR name, readable document text, and extracted requirements are required.")
    result = client().table(TOR_TABLE).insert({
        "name": name, "filename": filename, "tor_text": text,
        "requirements": requirements,
    }).execute()
    return result.data[0]["id"]
