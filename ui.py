from html import escape
import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    :root{
        --navy:#0f2742;--blue:#1976d2;--blue-dark:#0b5cad;--blue-soft:#eaf4ff;
        --surface:#ffffff;--canvas:#f5f8fc;--line:#dbe5ef;--muted:#66788a;
        --shadow:0 12px 34px rgba(15,39,66,.08);--radius:18px
    }
    html{font-size:16px}
    .stApp{
        background:
            radial-gradient(circle at 92% 2%,rgba(25,118,210,.10),transparent 25rem),
            linear-gradient(180deg,#f9fbfe 0%,var(--canvas) 100%);
        color:var(--navy)
    }
    .block-container{max-width:1440px;padding:2rem clamp(1.25rem,3vw,3rem) 4rem}
    h1,h2,h3,h4{color:var(--navy);letter-spacing:-.025em}
    h2,h3{margin-top:1.2rem!important}
    hr{border-color:var(--line)!important}

    [data-testid="stSidebar"]{background:rgba(255,255,255,.97);border-right:1px solid var(--line);box-shadow:8px 0 28px rgba(15,39,66,.04)}
    [data-testid="stSidebar"]>div:first-child{width:18rem}
    [data-testid="stSidebar"] .block-container{padding:1.65rem 1.15rem}
    [data-testid="stSidebar"] [role="radiogroup"]{gap:.35rem}
    [data-testid="stSidebar"] [role="radiogroup"] label{
        background:transparent;border:1px solid transparent;border-radius:13px;
        padding:.72rem .85rem;margin:.08rem 0;transition:all .18s ease;color:var(--navy)
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#f1f7fd;border-color:#d9eafb;transform:translateX(2px)}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(135deg,#eaf4ff,#f5faff);border-color:#bcdcff;color:var(--blue-dark);font-weight:750}
    [data-testid="stSidebar"] [data-testid="stRadio"] input{display:none}

    .page-kicker{color:var(--blue);font-size:.76rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase}
    .page-title{font-size:clamp(1.8rem,3.2vw,2.65rem);font-weight:850;line-height:1.1;margin:.32rem 0;color:var(--navy);letter-spacing:-.035em}
    .page-subtitle{color:var(--muted);font-size:1rem;line-height:1.55;margin:0 0 1.6rem;max-width:52rem}

    .metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;margin:1rem 0 1.8rem}
    .metric-card{position:relative;overflow:hidden;background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:var(--radius);padding:1.15rem 1.25rem;box-shadow:var(--shadow);transition:transform .18s ease,box-shadow .18s ease}
    .metric-card:before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:linear-gradient(180deg,var(--blue),#62b5ff)}
    .metric-card:hover{transform:translateY(-2px);box-shadow:0 16px 38px rgba(15,39,66,.12)}
    .metric-label{font-size:.75rem;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.07em}
    .metric-value{font-size:clamp(1.35rem,2.5vw,2.1rem);font-weight:850;margin-top:.4rem;overflow-wrap:anywhere;color:var(--navy)}

    .detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem}
    .detail-item{background:linear-gradient(145deg,#fff,#f8fbfe);border:1px solid var(--line);border-radius:14px;padding:1rem 1.05rem;min-width:0}
    .detail-label{font-size:.72rem;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.055em}
    .detail-value{margin-top:.3rem;font-weight:700;overflow-wrap:anywhere;color:var(--navy)}
    .login-brand{text-align:center;margin:clamp(2rem,8vh,6rem) 0 1.4rem}
    .login-icon{width:68px;height:68px;margin:0 auto .95rem;border-radius:21px;background:linear-gradient(135deg,#0f4f8a,#2196f3);display:grid;place-items:center;color:#fff;font-size:1.9rem;box-shadow:0 16px 36px rgba(25,118,210,.28)}
    .section-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:1.2rem 1.3rem;box-shadow:var(--shadow)}
    .list-heading{font-size:.72rem;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.07em;padding:.4rem .2rem}

    div[data-testid="stForm"],div[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.96);border-color:var(--line)!important;border-radius:var(--radius)!important;box-shadow:var(--shadow)}
    div[data-testid="stForm"]{padding:1.35rem}
    div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;box-shadow:0 6px 20px rgba(15,39,66,.045)}
    [data-testid="stPlotlyChart"]{background:rgba(255,255,255,.96);border:1px solid var(--line);border-radius:var(--radius);padding:.35rem;box-shadow:var(--shadow);overflow:hidden}
    [data-testid="stTabs"] [data-baseweb="tab-list"]{gap:.35rem;border-bottom:1px solid var(--line)}
    [data-testid="stTabs"] button{border-radius:10px 10px 0 0;padding:.75rem 1rem}
    [data-testid="stDialog"]>div{border-radius:22px!important}

    .stButton>button,.stDownloadButton>button{border-radius:11px;min-height:2.7rem;font-weight:750;border-color:#cbd8e5;transition:all .18s ease}
    .stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--blue);color:var(--blue-dark);transform:translateY(-1px);box-shadow:0 8px 18px rgba(25,118,210,.12)}
    .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(135deg,var(--blue-dark),var(--blue));border:0;color:#fff;box-shadow:0 9px 22px rgba(25,118,210,.22)}
    .stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stSelectbox [data-baseweb="select"]{border-radius:11px;background:#fbfdff;border-color:#cfdae6;min-height:2.75rem}
    [data-testid="stFileUploaderDropzone"]{background:#f8fbff;border:1.5px dashed #b9d5ee;border-radius:16px;padding:1rem}
    [data-testid="stAlert"]{border-radius:14px}

    @media(max-width:1000px){
        .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
        .detail-grid{grid-template-columns:1fr}
        .block-container{padding-top:1.4rem}
    }
    @media(max-width:760px){
        html{font-size:15px}
        .block-container{padding:1.1rem .9rem 3rem}
        .page-title{font-size:1.9rem}.page-subtitle{margin-bottom:1.15rem}
        div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.75rem!important}
        div[data-testid="stHorizontalBlock"]>div[data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important;min-width:100%!important}
        [data-testid="stPlotlyChart"]{margin-top:.25rem}
        div[data-testid="stDialog"]{width:calc(100vw - 1rem)!important;max-width:calc(100vw - 1rem)!important}
    }
    @media(max-width:520px){
        .metric-grid{grid-template-columns:1fr;gap:.7rem}
        .metric-card{padding:1rem 1.1rem}
        .list-heading{display:none}
        .stButton>button,.stDownloadButton>button{width:100%}
        [data-testid="stSidebar"]>div:first-child{width:16.5rem}
    }
    .section-heading{font-size:1.22rem;font-weight:800;color:#122b48;margin:1.45rem 0 .7rem;display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap}
    .section-heading span{font-size:.82rem;font-weight:500;color:#7b8ca0}
    .status-pill{display:inline-block;border-radius:999px;padding:.32rem .7rem;font-size:.75rem;font-weight:800;letter-spacing:.04em}
    .status-pill.pass{background:#e3f7ef;color:#087c59}
    .status-pill.fail{background:#fff0f0;color:#c3414a}
    [data-testid="stVerticalBlockBorderWrapper"]{box-shadow:0 5px 22px rgba(20,50,90,.05)!important}
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h4{margin:.1rem 0 .65rem!important}
    [data-testid="stPlotlyChart"]{padding:.2rem!important}
    [data-testid="stSidebar"] [role="radiogroup"] label{padding:.6rem .75rem}
    .metric-grid{gap:.75rem;margin:.75rem 0 1.2rem}
    .metric-card{padding:1rem 1.1rem;border-radius:15px;box-shadow:0 4px 18px rgba(15,39,66,.05)}
    .page-subtitle{margin-bottom:1.1rem}

    /* Candidate details modal */
    [data-testid="stDialog"] [role="dialog"]{border-radius:22px!important;overflow:auto;max-height:90vh}
    [data-testid="stDialog"] .block-container{padding-top:.8rem!important}
    .cv-modal-top{background:linear-gradient(125deg,#f1f7ff,#ffffff 75%);border:1px solid #dce9f8;border-radius:17px;padding:1.15rem 1.25rem;margin:.1rem 0 1rem}
    .cv-modal-kicker{font-size:.69rem;letter-spacing:.1em;color:#4b78a8;font-weight:800;margin-bottom:.9rem}
    .cv-modal-kicker span,.cv-modal-meta span{padding:0 .4rem;color:#9eb1c4}
    .cv-modal-hero{display:flex;gap:1rem;align-items:center;min-width:0}
    .cv-modal-avatar{width:57px;height:57px;flex:none;display:grid;place-items:center;border-radius:16px;background:linear-gradient(145deg,#175caa,#40a1ef);color:white;font-size:1.2rem;font-weight:850;box-shadow:0 8px 18px #1976d230}
    .cv-modal-person{flex:1;min-width:0}
    .cv-modal-name{font-size:1.25rem;font-weight:850;color:#102b4a;line-height:1.2;overflow-wrap:anywhere}
    .cv-modal-meta,.cv-modal-project{font-size:.81rem;color:#647d96;margin-top:.2rem}
    .cv-modal-result{text-align:right;flex:none}
    .cv-modal-score{font-size:2rem;font-weight:900;letter-spacing:-.05em;color:#0d3158;line-height:1.1}
    .cv-modal-score span{font-size:1rem;color:#66809c;margin-left:2px}
    .cv-modal-status{display:inline-block;margin-top:.35rem;padding:.25rem .65rem;border-radius:99px;font-size:.68rem;font-weight:800;letter-spacing:.06em}
    .cv-modal-status.pass{background:#e0f7eb;color:#0a7e54}.cv-modal-status.fail{background:#ffeded;color:#b43d45}
    .cv-modal-section-title{font-size:.88rem;font-weight:800;color:#183655;margin:.8rem 0 .9rem}
    .cv-modal-info-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.3rem 1.5rem;margin-bottom:1rem}
    .cv-modal-info{padding:.65rem 0;border-bottom:1px solid #e9eef5;min-width:0}
    .cv-modal-label{font-size:.66rem;font-weight:800;letter-spacing:.075em;color:#71869d;text-transform:uppercase}
    .cv-modal-value{font-size:.88rem;font-weight:650;color:#17324f;margin-top:.22rem;overflow-wrap:anywhere}
    .cv-modal-document{padding:.8rem 1rem;background:#f5f9ff;border:1px solid #dce9f8;border-radius:12px;margin:.6rem 0}
    [data-testid="stDialog"] .detail-item{padding:.7rem .9rem}
    @media(max-width:640px){.cv-modal-hero{flex-wrap:wrap}.cv-modal-result{width:100%;text-align:left;padding-left:0}.cv-modal-info-grid{grid-template-columns:1fr}.cv-modal-top{padding:1rem}}

    /* Responsive mockup-inspired design layer */
    .stApp{background:#f3f7fc}
    .block-container{max-width:1530px;padding-top:1.3rem}
    [data-testid="stSidebar"]{background:#fff}
    .sidebar-brand{display:flex;align-items:center;gap:.65rem;font-size:.88rem;font-weight:800;color:#12325d;line-height:1.3;padding:.65rem .2rem 1rem}
    .sidebar-brand small{display:block;font-size:.69rem;font-weight:500;color:#8293aa;margin-top:.3rem}
    .brand-mark{display:grid;place-items:center;width:2.35rem;height:2.35rem;border-radius:50%;background:#e7f2ff;color:#1765ca;font-size:1.6rem}
    .page-title{font-size:clamp(1.7rem,2.7vw,2.45rem);letter-spacing:-.04em}
    .page-subtitle{font-size:.91rem;margin-bottom:1.25rem}
    .metric-grid{gap:.75rem;margin:.65rem 0 1.25rem}
    .metric-card{border-radius:15px;box-shadow:0 5px 22px #173b6410;padding:1rem 1.1rem}
    .metric-card:before{width:0}
    .metric-label{font-size:.75rem;text-transform:none;letter-spacing:0}
    .metric-value{font-size:1.65rem}
    .section-heading{margin:1.1rem 0 .65rem}
    [data-testid="stVerticalBlockBorderWrapper"]{box-shadow:0 4px 16px #173b640b!important}
    .candidate-row-name{display:flex;align-items:center;gap:.8rem;min-width:0}
    .candidate-row-name strong{display:block;font-size:.88rem;color:#142e51;overflow-wrap:anywhere}
    .candidate-row-name small{display:block;font-size:.72rem;color:#72859d;margin-top:.18rem;overflow-wrap:anywhere}
    .candidate-avatar{flex:none;display:grid;place-items:center;background:#e8f1ff;color:#145cbb;width:2.55rem;height:2.55rem;border-radius:12px;font-size:.82rem;font-weight:850}
    .candidate-row-result{text-align:center}
    .candidate-row-result strong{display:block;color:#17355c;font-size:1.08rem}
    .candidate-row-result .status-pill{font-size:.63rem;padding:.2rem .45rem;white-space:nowrap}
    .form-section-heading{display:flex;align-items:center;gap:.55rem;font-size:.75rem;font-weight:850;color:#2773cc;margin:1.2rem 0 .65rem}
    .form-section-heading span{font-size:1rem;color:#18365b}
    [data-testid="stFileUploaderDropzone"]{padding:1.35rem;border:1.5px dashed #95c2f7;background:#f7fbff}
    [data-testid="stSelectbox"] label,[data-testid="stTextInput"] label{font-size:.81rem;font-weight:650}
    [data-testid="stSelectbox"] [data-baseweb="select"]{min-height:2.35rem}
    [data-testid="stAlert"]{font-size:.85rem}
    @media(max-width:760px){
      .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
      .candidate-row-name{gap:.45rem}
      .candidate-avatar{width:2rem;height:2rem;font-size:.72rem}
      .candidate-row-result{text-align:left}
      .block-container{padding:1rem .75rem 3rem}
    }
    @media(max-width:420px){.metric-grid{grid-template-columns:1fr 1fr;gap:.45rem}.metric-card{padding:.8rem}.metric-value{font-size:1.3rem}}

    /* Reference-matched navigation: flat icon links, blue selected row */
    [data-testid="stSidebar"]{background:#f8fbff!important;border-right:1px solid #dce9f8!important}
    [data-testid="stSidebar"] .block-container{padding:1.15rem .8rem!important}
    [data-testid="stSidebar"] [role="radiogroup"]{gap:.18rem!important}
    [data-testid="stSidebar"] [role="radiogroup"] label{
      display:flex!important;align-items:center!important;gap:.5rem!important;
      width:100%!important;border-radius:9px!important;
      padding:.7rem .75rem!important;min-height:2.9rem!important;
      border:1px solid transparent!important;transform:none!important;
      background:transparent!important;font-size:.86rem!important;
      color:#204c85!important
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover{
      background:#eaf3ff!important;border-color:#eaf3ff!important
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
      background:#e5f0ff!important;border-color:#e5f0ff!important;
      color:#0759bf!important;font-weight:750!important
    }
    [data-testid="stSidebar"] [role="radiogroup"] label [data-baseweb="radio"] > div:first-child{
      display:none!important
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:before{
      display:inline-flex;align-items:center;justify-content:center;
      width:1.5rem;height:1.5rem;flex:none;
      font-size:1.05rem;font-weight:600;color:#245d9d
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1):before{content:"⌂"}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2):before{content:"▣"}
    [data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3):before{content:"▤"}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked):before{color:#0967d8}
    [data-testid="stSidebar"] hr{margin:1.1rem 0!important}
    [data-testid="stSidebar"] .stButton>button{
      background:transparent!important;color:#244b7b!important;
      border:1px solid #d5e5f5!important;box-shadow:none!important;
      font-size:.83rem!important;min-height:2.4rem!important
    }
    .sidebar-brand{padding:.65rem .2rem 1rem!important;font-size:.81rem!important}
    .brand-mark{background:#e7f1ff!important;color:#1464ca!important}
    @media(max-width:760px){
      [data-testid="stSidebar"] .block-container{padding:1rem .65rem!important}
      [data-testid="stSidebar"] [role="radiogroup"] label{min-height:2.8rem!important}
    }

    /* Sidebar navigation — matches reference: single small icon, no radio control */
    [data-testid="stSidebar"] .st-key-nav_dashboard_idle button,
    [data-testid="stSidebar"] .st-key-nav_dashboard_active button,
    [data-testid="stSidebar"] .st-key-nav_new_idle button,
    [data-testid="stSidebar"] .st-key-nav_new_active button,
    [data-testid="stSidebar"] .st-key-nav_saved_idle button,
    [data-testid="stSidebar"] .st-key-nav_saved_active button{
      width:100%!important;min-height:2.45rem!important;
      justify-content:flex-start!important;text-align:left!important;
      padding:.5rem .72rem!important;border:0!important;
      border-radius:7px!important;background:transparent!important;
      color:#1e4d86!important;box-shadow:none!important;
      font-size:.82rem!important;font-weight:500!important;
      gap:.55rem!important;transition:background .15s ease!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button:hover{
      background:#eaf3ff!important;color:#0860cf!important;
    }
    [data-testid="stSidebar"] .st-key-nav_dashboard_active button,
    [data-testid="stSidebar"] .st-key-nav_new_active button,
    [data-testid="stSidebar"] .st-key-nav_saved_active button{
      background:#e3efff!important;color:#0962d4!important;font-weight:650!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stIconMaterial"]{
      font-size:1.05rem!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button p{
      font-size:.82rem!important;
    }
    [data-testid="stSidebar"] .sidebar-brand{margin-bottom:.1rem!important}

    /* Alignment fix: Streamlit centers its INNER button content wrapper.
       Align both the button and its nested wrapper, not just the outer button. */
    [data-testid="stSidebar"] [class*="st-key-nav_"] .stButton,
    [data-testid="stSidebar"] [class*="st-key-nav_"] [data-testid="stButton"]{
      width:100%!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button{
      display:flex!important;
      flex-direction:row!important;
      align-items:center!important;
      justify-content:flex-start!important;
      text-align:left!important;
      padding-left:14px!important;
      padding-right:10px!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button > div,
    [data-testid="stSidebar"] [class*="st-key-nav_"] button > span,
    [data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stMarkdownContainer"]{
      margin-left:0!important;
      margin-right:auto!important;
      text-align:left!important;
      justify-content:flex-start!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stMarkdownContainer"]{
      display:flex!important;align-items:center!important;gap:9px!important;
    }
    [data-testid="stSidebar"] [class*="st-key-nav_"] button svg,
    [data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stIconMaterial"]{
      flex-shrink:0!important;
    }
    /* Transparent Streamlit top header and toolbar */
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    /* Transparent sidebar, including its internal background layers */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    </style>""",unsafe_allow_html=True)

def page_header(kicker,title,subtitle=""):
    st.markdown(f'<div class="page-kicker">{escape(kicker)}</div><div class="page-title">{escape(title)}</div><div class="page-subtitle">{escape(subtitle)}</div>',unsafe_allow_html=True)

def metric_grid(items):
    cards="".join(f'<div class="metric-card"><div class="metric-label">{escape(str(label))}</div><div class="metric-value">{escape(str(value))}</div></div>' for label,value in items)
    st.markdown(f'<div class="metric-grid">{cards}</div>',unsafe_allow_html=True)

def detail_grid(items):
    cards="".join(f'<div class="detail-item"><div class="detail-label">{escape(str(label))}</div><div class="detail-value">{escape(str(value or "Not provided"))}</div></div>' for label,value in items)
    st.markdown(f'<div class="detail-grid">{cards}</div>',unsafe_allow_html=True)
