# Reusable TOR Library

1. Execute `tor_library_schema.sql` in the same Supabase project as `cv_evaluations`.
2. Restart/redeploy Streamlit.
3. In New Evaluation, select **Upload new TOR**, enter a name, upload PDF/DOCX/TXT, and click **Save TOR to library**.
4. For future candidates, select the stored TOR from **Select project TOR** and upload only their CV.
5. The selected TOR's extracted requirements are used for automated provisional CV matching and saved with the evaluation.

Existing evaluations and scoring are unchanged. A TOR can be reused across sessions and app restarts. No automatic authentication of qualifications is performed.
