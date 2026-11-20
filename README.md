# CV Checker Admin Portal

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Supabase setup

1. Open your Supabase project and run `supabase_schema.sql` in SQL Editor.
2. Confirm the existing Storage bucket is named exactly `File_Checker`.
3. Copy `secrets.toml.example` to `.streamlit/secrets.toml` when running locally.
4. Enter your project URL and Supabase secret key. Never commit or publish the
   real secret key.
5. On Streamlit Cloud, open **App settings → Secrets** and paste:

```toml
[supabase]
url = "https://YOUR_PROJECT_REF.supabase.co"
secret_key = "YOUR_SUPABASE_SECRET_KEY"
```

The secret key is used only by the Streamlit server. It bypasses Row Level
Security, so it must never be exposed in browser code or GitHub.

If your existing table contains `POS A`, `POS B`, or `POS C`, run
`migrate_pos_to_pro.sql` once to rename them to `Pro A`, `Pro B`, and `Pro C`.

For an existing `cv_evaluations` table, also run
`enhance_cv_dashboard.sql` once. It adds Project, TOR, Client, Age, Number,
Key/Non-Key, Key Category, and PASS/FAIL columns required by the dashboard.

## Classification rules

- International Key: PASS at 70 or higher. A score below 70 is automatically
  reclassified as Non-Key.
- Local Key: PASS at 50 or higher.
- Non-Key: PASS at 50 or higher.
- The dashboard summarizes average scores by TOR and client and shows Key-client,
  overall PASS/FAIL, and Non-Key PASS/FAIL pie charts.

## Admin login

Default login:

- Username: `admin`
- Password: `admin123`

Change these before deployment by setting `CV_ADMIN_USERNAME` and
`CV_ADMIN_PASSWORD` as environment variables. Evaluation records are stored in
the Supabase `cv_evaluations` table. Attached CV files are stored in the
`File_Checker` bucket.
