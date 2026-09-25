"""Professional Streamlit interface for the local Flask loan-default API."""
from __future__ import annotations

import os
import sys
import subprocess
import time
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
API_URL = "https://risklens-ml-project-1.onrender.com"
TARGET_VARIABLE = "default"
FEATURE_ORDER = [
    "Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed", "NumCreditLines",
    "InterestRate", "LoanTerm", "DTIRatio", "HasMortgage", "HasDependents", "HasCoSigner",
    "Education", "EmploymentType", "MaritalStatus", "LoanPurpose",
]
CATEGORICAL_DEFAULTS = {
    "Education": ["Bachelor's", "High School", "Master's", "PhD"],
    "EmploymentType": ["Full-time", "Part-time", "Self-employed", "Unemployed"],
    "MaritalStatus": ["Single", "Married", "Divorced"],
    "HasMortgage": ["No", "Yes"], "HasDependents": ["No", "Yes"],
    "LoanPurpose": ["Other", "Auto", "Business", "Education", "Home"], "HasCoSigner": ["No", "Yes"],
}
def start_flask_backend() -> None:
    """Start the Flask API locally for Streamlit Cloud."""
    backend_file = PROJECT_ROOT / "backend" / "app.py"

    if not backend_file.exists():
        st.error(f"Backend file not found: {backend_file}")
        return

    try:
        response = requests.get(
            "http://127.0.0.1:5000/health",
            timeout=1
        )
        if response.ok:
            return
    except requests.RequestException:
        pass

    subprocess.Popen(
        [sys.executable, str(backend_file)],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    for _ in range(20):
        time.sleep(0.5)

        try:
            response = requests.get(
                "http://127.0.0.1:5000/health",
                timeout=1
            )

            if response.ok:
                return

        except requests.RequestException:
            pass

    st.error("Flask backend failed to start.")
st.set_page_config(page_title="RiskLens | Loan Default Intelligence", page_icon="RL", layout="wide", initial_sidebar_state="collapsed")


def toggle_theme() -> None:
    """Switch the UI theme while preserving the choice for this Streamlit session."""
    st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"


def apply_theme() -> None:
    """Apply the selected palette once per rerun using theme-scoped CSS variables."""
    theme = st.session_state.setdefault("theme", "light")
    is_dark = theme == "dark"
    st.markdown(f'''<div class="theme-anchor theme-{'dark' if is_dark else 'light'}"></div>
    <style>
      :root{{--rl-bg:#f6f8fc;--rl-surface:#ffffff;--rl-surface-alt:#f8fafc;--rl-text:#182230;--rl-heading:#102a43;--rl-muted:#64748b;--rl-border:#e5eaf2;--rl-border-strong:#e7edf5;--rl-nav-bg:rgba(255,255,255,.94);--rl-nav-text:#475569;--rl-nav-hover:#eff6ff;--rl-nav-active:#e8f0ff;--rl-input-bg:#ffffff;--rl-table-bg:#ffffff;--rl-table-header:#eff6ff;--rl-table-text:#182230;--rl-table-muted:#64748b;--rl-table-hover:#e8f1ff;--rl-shadow:rgba(15,23,42,.045);}}
      .stApp:has(.theme-dark){{--rl-bg:#07111f;--rl-surface:#0f1f33;--rl-surface-alt:#132e4f;--rl-text:#eaf2ff;--rl-heading:#f7faff;--rl-muted:#a9bdd6;--rl-border:#294563;--rl-border-strong:#345675;--rl-nav-bg:rgba(7,17,31,.9);--rl-nav-text:#bdcce0;--rl-nav-hover:#173b66;--rl-nav-active:#164d8a;--rl-input-bg:#0f1f33;--rl-table-bg:#0f1f33;--rl-table-header:#132e4f;--rl-table-text:#eaf2ff;--rl-table-muted:#a9bdd6;--rl-table-hover:#173b66;--rl-shadow:rgba(0,0,0,.3);}}
      .stApp:has(.theme-dark),.stApp:has(.theme-dark) [data-testid="stAppViewContainer"]{{background:var(--rl-bg)!important;color:var(--rl-text)}}
      .stApp:has(.theme-dark) div[data-testid="stHorizontalBlock"]:has(.brand){{background:var(--rl-nav-bg);border-color:var(--rl-border);box-shadow:0 8px 28px rgba(0,0,0,.28)}}
      .stApp:has(.theme-dark) .brand,.stApp:has(.theme-dark) .dashboard-title,.stApp:has(.theme-dark) .stat-value,.stApp:has(.theme-dark) .detail-card h3,.stApp:has(.theme-dark) .detail-card strong,.stApp:has(.theme-dark) .cta-panel h2,.stApp:has(.theme-dark) .section-title{{color:var(--rl-heading)}}
      .stApp:has(.theme-dark) .dashboard-intro,.stApp:has(.theme-dark) .stat-label,.stApp:has(.theme-dark) .stat-subtitle,.stApp:has(.theme-dark) .detail-card p,.stApp:has(.theme-dark) .muted,.stApp:has(.theme-dark) p{{color:var(--rl-muted)}}
      .stApp:has(.theme-dark) .stat-card,.stApp:has(.theme-dark) .detail-card,.stApp:has(.theme-dark) .dataset-card,.stApp:has(.theme-dark) .card{{background:var(--rl-surface);border-color:var(--rl-border-strong);box-shadow:0 12px 30px var(--rl-shadow),inset 0 1px 0 rgba(147,197,253,.04)}}
      .stApp:has(.theme-dark) .cta-panel{{background:linear-gradient(120deg,#152b4a,#121c2d);border-color:var(--rl-border-strong)}}
      .stApp:has(.theme-dark) .dashboard-hero p,.stApp:has(.theme-dark) .hero p{{color:#dbeafe}}
      .stApp:has(.theme-dark) .result-good{{background:#102b23}} .stApp:has(.theme-dark) .result-risk{{background:#351923}}
      .stApp:has(.theme-dark) [data-testid="stWidgetLabel"] p,.stApp:has(.theme-dark) [data-testid="stWidgetLabel"]{{color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) [data-baseweb="input"]>div,.stApp:has(.theme-dark) [data-baseweb="select"]>div,.stApp:has(.theme-dark) [data-baseweb="textarea"]>div{{background:var(--rl-input-bg)!important;border-color:var(--rl-border-strong)!important;color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) [data-baseweb="input"] input,.stApp:has(.theme-dark) [data-baseweb="select"] span,.stApp:has(.theme-dark) textarea{{color:var(--rl-text)!important;-webkit-text-fill-color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) [data-baseweb="popover"],.stApp:has(.theme-dark) [role="listbox"]{{background:var(--rl-surface)!important;color:var(--rl-text)!important}}
      /* Glide Data Grid paints its own canvas, so set its native colour tokens as well as its shell. */
      [data-testid="stDataFrame"]{{--gdg-bg-cell:var(--rl-table-bg);--gdg-bg-cell-medium:var(--rl-table-bg);--gdg-bg-header:var(--rl-table-header);--gdg-bg-header-has-focus:var(--rl-table-header);--gdg-bg-header-hovered:var(--rl-table-hover);--gdg-text-dark:var(--rl-table-text);--gdg-text-medium:var(--rl-table-muted);--gdg-text-light:var(--rl-table-muted);--gdg-border-color:var(--rl-border);--gdg-horizontal-border-color:var(--rl-border);--gdg-accent-color:#2563eb;--gdg-accent-light:var(--rl-table-hover);background:var(--rl-table-bg)!important;border:1px solid var(--rl-border)!important;border-radius:12px;overflow:auto}}
      [data-testid="stDataFrame"] [role="grid"],[data-testid="stDataFrame"] .dvn-scroller,[data-testid="stDataFrame"] canvas{{background:var(--rl-table-bg)!important}}
      .stApp:has(.theme-dark) [data-testid="stDataFrame"],.stApp:has(.theme-dark) [data-testid="stDataFrame"] *{{color:var(--rl-table-text)!important}}
      .stApp:has(.theme-dark) [data-testid="stDataFrame"] button{{background:#132e4f!important;border-color:var(--rl-border)!important;color:var(--rl-table-text)!important}}
      .stApp:has(.theme-dark) [data-testid="stMetric"]{{background:var(--rl-surface-alt);border:1px solid var(--rl-border);border-radius:12px;padding:.7rem}}
      .stApp:has(.theme-dark) [data-testid="stMetric"] *,.stApp:has(.theme-dark) .stSubheader{{color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) [data-testid="stAlert"],.stApp:has(.theme-dark) [data-testid="stAlert"]>div{{background:#102a47!important;border-color:#294f78!important;color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) [data-testid="stExpander"],.stApp:has(.theme-dark) [data-testid="stExpander"] details{{background:var(--rl-surface)!important;border-color:var(--rl-border)!important;color:var(--rl-text)!important}}
      .stApp:has(.theme-dark) code,.stApp:has(.theme-dark) [data-testid="stCode"]{{background:#0b192b!important;color:#dbeafe!important;border-color:var(--rl-border)!important}}
      div[data-testid="stHorizontalBlock"]:has(.brand) div[data-testid="stButton"] button{{min-width:42px;width:42px;height:38px;padding:0;border:1px solid #bfdbfe;background:#eff6ff;color:#1d4ed8;font-size:1.05rem;box-shadow:none}}
      div[data-testid="stHorizontalBlock"]:has(.brand) div[data-testid="stButton"] button:hover{{background:#dbeafe;color:#1d4ed8;transform:translateY(-1px)}}
      .stApp:has(.theme-dark) div[data-testid="stHorizontalBlock"]:has(.brand) div[data-testid="stButton"] button{{background:#1b2d47;border-color:#36506f;color:#fde68a}}
      @media (max-width:850px){{div[data-testid="stHorizontalBlock"]:has(.brand)>div:last-child{{flex:0 0 46px!important;width:46px!important}}}}
    </style>''', unsafe_allow_html=True)

st.markdown("""
<style>
  #MainMenu, footer, header {visibility:hidden}
  .block-container{max-width:1240px;padding-top:6.65rem;padding-bottom:3rem}
  .stApp{background:#f6f8fc;color:#182230;font-family:Inter,Segoe UI,sans-serif}
  /* Fixed custom navigation shell. The :has selector targets only the header row. */
  div[data-testid="stHorizontalBlock"]:has(.brand){position:fixed;top:0;left:0;right:0;z-index:1000;min-height:76px;padding:0.8rem max(2rem,calc((100vw - 1180px)/2));margin:0;background:rgba(255,255,255,.94);border-bottom:1px solid rgba(226,232,240,.9);box-shadow:0 8px 28px rgba(15,23,42,.08);backdrop-filter:blur(14px);align-items:center;transition:box-shadow .2s ease,background .2s ease}
  div[data-testid="stHorizontalBlock"]:has(.brand)>div{display:flex;align-items:center}
  .brand{display:flex;align-items:center;gap:.7rem;font-size:1.3rem;font-weight:850;letter-spacing:-.045em;color:#102a43;white-space:nowrap}.brand::before{content:"";display:inline-block;width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,#2563eb,#0f3a90);box-shadow:0 5px 12px rgba(37,99,235,.25)}.brand span{color:#2563eb}
  
  @keyframes nav-in{from{transform:scaleX(.35);opacity:.35}to{transform:scaleX(1);opacity:1}}
  @media (max-width: 850px){.block-container{padding-top:7.5rem}div[data-testid="stHorizontalBlock"]:has(.brand){padding:.7rem 1rem;min-height:86px}div[data-testid="stHorizontalBlock"]:has(.brand)>div:first-child{flex:0 0 auto!important;width:auto!important}div[data-testid="stHorizontalBlock"]:has(.brand)>div:last-child{min-width:0!important}div[data-testid="stHorizontalBlock"]:has(.brand) div[role="radiogroup"]{gap:0;overflow-x:auto;justify-content:flex-start;scrollbar-width:none}div[data-testid="stHorizontalBlock"]:has(.brand) div[role="radiogroup"] label{font-size:.78rem;padding:.42rem .56rem!important;white-space:nowrap}.brand{font-size:1.08rem}.brand::before{width:26px;height:26px}}
  .dashboard-hero{position:relative;overflow:hidden;min-height:345px;padding:3.1rem;border-radius:24px;background:linear-gradient(115deg,#102a43 0%,#173c68 52%,#1d4ed8 100%);box-shadow:0 20px 44px rgba(15,42,67,.19);animation:fade-up .45s ease-out both}.dashboard-hero::after{content:"";position:absolute;width:410px;height:410px;right:-150px;top:-245px;border:50px solid rgba(147,197,253,.14);border-radius:50%}.dashboard-hero h1{position:relative;z-index:1;max-width:690px;margin:.65rem 0 .9rem;color:#fff;font-size:clamp(2.3rem,4vw,3.7rem);line-height:1.04;letter-spacing:-.055em}.dashboard-hero p{position:relative;z-index:1;max-width:610px;margin:0;color:#dbeafe;font-size:1.05rem;line-height:1.65}.dashboard-eyebrow{position:relative;z-index:1;display:inline-flex;padding:.38rem .7rem;border:1px solid rgba(191,219,254,.25);border-radius:999px;background:rgba(15,42,67,.25);color:#bfdbfe;font-size:.73rem;font-weight:750;letter-spacing:.11em}.hero-facts{position:relative;z-index:1;display:flex;gap:.65rem;flex-wrap:wrap;margin-top:1.7rem}.hero-fact{padding:.6rem .75rem;border-radius:10px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.13);color:#e0efff;font-size:.84rem}.hero-fact b{color:#fff}.dashboard-title{margin:2.4rem 0 .25rem;font-size:1.55rem;font-weight:820;letter-spacing:-.035em;color:#102a43}.dashboard-intro{margin:0 0 1.15rem;color:#64748b}.stat-card,.detail-card,.cta-panel{background:#fff;border:1px solid #e7edf5;border-radius:17px;box-shadow:0 5px 18px rgba(15,23,42,.045);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}.stat-card{height:100%;padding:1.25rem}.stat-card:hover,.detail-card:hover{transform:translateY(-4px);border-color:#bfdbfe;box-shadow:0 14px 28px rgba(30,64,175,.11)}.stat-label{font-size:.73rem;font-weight:760;letter-spacing:.095em;text-transform:uppercase;color:#64748b}.stat-value{margin-top:.45rem;color:#102a43;font-size:1.5rem;font-weight:830;letter-spacing:-.035em}.stat-subtitle{margin-top:.2rem;color:#94a3b8;font-size:.84rem}.detail-card{height:100%;padding:1.25rem}.detail-card h3{margin:0 0 .55rem;color:#102a43;font-size:1rem}.detail-card p{margin:.28rem 0;color:#64748b;font-size:.92rem}.detail-card strong{color:#334155}.dataset-card{padding:1rem 1.1rem;background:#fff;border:1px solid #e7edf5;border-radius:17px;box-shadow:0 5px 18px rgba(15,23,42,.035)}.cta-panel{margin-top:2.3rem;padding:2rem 2.1rem;background:linear-gradient(120deg,#eff6ff,#fff)}.cta-panel h2{margin:0;color:#102a43;font-size:1.55rem;letter-spacing:-.035em}.cta-panel p{margin:.45rem 0 1.1rem;color:#64748b}.dashboard-action div[data-testid="stButton"] button{padding:.7rem 1.1rem;box-shadow:0 9px 20px rgba(37,99,235,.2);transition:transform .18s ease,box-shadow .18s ease,background .18s ease}.dashboard-action div[data-testid="stButton"] button:hover{transform:translateY(-2px);box-shadow:0 13px 25px rgba(37,99,235,.28)}@keyframes fade-up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
  .hero{background:linear-gradient(120deg,#102a43,#1d4ed8);border-radius:22px;padding:2.4rem;color:white;margin:1rem 0 1.7rem}.eyebrow{font-size:.75rem;letter-spacing:.12em;font-weight:700;color:#bfdbfe;text-transform:uppercase}.hero h1{font-size:2.5rem;line-height:1.08;margin:.55rem 0}.hero p{color:#dbeafe;max-width:680px;font-size:1.05rem}
  .card{background:#fff;border:1px solid #e5eaf2;border-radius:16px;padding:1.2rem;box-shadow:0 4px 18px rgba(15,23,42,.04);height:100%}.card-title{color:#64748b;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}.card-value{font-size:1.5rem;font-weight:800;margin-top:.35rem}.section-title{font-weight:800;font-size:1.55rem;letter-spacing:-.025em;margin-top:.6rem}.muted{color:#64748b}.result-good{border-left:5px solid #16a34a;background:#f0fdf4}.result-risk{border-left:5px solid #e11d48;background:#fff1f2}
  div[data-testid="stButton"] button{background:#2563eb;color:#fff;border:0;border-radius:9px;font-weight:700;padding:.55rem 1rem} div[data-testid="stButton"] button:hover{background:#1d4ed8;color:#fff}
  /* Premium visual layer: reusable surfaces, restrained blue accents, and responsive layout. */
  .block-container{padding-left:max(1.1rem,calc((100vw - 1180px)/2));padding-right:max(1.1rem,calc((100vw - 1180px)/2))}
  .dashboard-hero{min-height:370px;padding:3.35rem;background:radial-gradient(circle at 86% 22%,rgba(96,165,250,.3),transparent 26%),linear-gradient(120deg,#0b2744 0%,#123b73 52%,#2563eb 100%);box-shadow:0 24px 56px rgba(16,66,142,.26),0 0 0 1px rgba(191,219,254,.16) inset}
  .dashboard-hero::before{content:"";position:absolute;inset:0;opacity:.42;background-image:linear-gradient(rgba(191,219,254,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(191,219,254,.07) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(90deg,#000 0%,transparent 75%)}
  .dashboard-hero::after{width:470px;height:470px;right:-155px;top:-255px;border-width:54px;border-color:rgba(147,197,253,.16)}
  .dashboard-hero h1{max-width:650px;margin-top:.8rem;text-shadow:0 2px 18px rgba(1,17,43,.2)}.dashboard-hero p{max-width:570px}.dashboard-eyebrow{box-shadow:0 6px 18px rgba(5,28,70,.14);backdrop-filter:blur(6px)}
  .hero-facts{max-width:630px;gap:.7rem}.hero-fact{display:inline-flex;align-items:center;gap:.42rem;padding:.65rem .82rem;background:rgba(255,255,255,.12);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 7px 16px rgba(5,28,70,.1);backdrop-filter:blur(7px)}.hero-fact i{display:inline-grid;place-items:center;width:17px;height:17px;border-radius:5px;background:rgba(147,197,253,.28);color:#dbeafe;font-size:.72rem;font-style:normal}
  .hero-visual{position:absolute;right:3.1rem;bottom:2.35rem;width:min(30%,275px);z-index:1;opacity:.96}.hero-visual svg{display:block;width:100%;height:auto;filter:drop-shadow(0 18px 18px rgba(4,22,55,.24))}.hero-visual .chart-panel{fill:rgba(8,37,80,.34);stroke:rgba(191,219,254,.28);stroke-width:1}.hero-visual .chart-grid{stroke:rgba(191,219,254,.17);stroke-width:1}.hero-visual .chart-line{fill:none;stroke:#93c5fd;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}.hero-visual .chart-dot{fill:#fff;stroke:#60a5fa;stroke-width:4}.hero-visual .node{fill:#bfdbfe;filter:drop-shadow(0 0 8px #60a5fa)}.hero-visual .node-line{stroke:#93c5fd;stroke-width:1.5;opacity:.7}
  .dashboard-title{margin-top:2.7rem}.stat-card,.detail-card,.dataset-card,.card{position:relative;overflow:hidden;border-radius:18px}.stat-card{padding:1.35rem;border-color:#e4ebf6;box-shadow:0 10px 26px rgba(15,46,92,.06)}.stat-card::before{content:"";position:absolute;left:0;top:1.25rem;bottom:1.25rem;width:3px;border-radius:0 4px 4px 0;background:linear-gradient(#60a5fa,#2563eb);box-shadow:0 0 13px rgba(37,99,235,.35)}.stat-card:hover,.detail-card:hover{transform:translateY(-5px);border-color:#93c5fd;box-shadow:0 18px 35px rgba(30,64,175,.14),0 0 0 1px rgba(96,165,250,.1)}.detail-card{padding:1.4rem}.detail-card h3{font-size:1.04rem}.dataset-card{border-color:#e4ebf6;box-shadow:0 12px 28px rgba(15,46,92,.055)}
  .cta-panel{position:relative;overflow:hidden;border:1px solid #dbeafe;border-radius:20px;background:linear-gradient(112deg,#eef6ff,#fff 58%,#eef4ff);box-shadow:0 14px 32px rgba(30,64,175,.08)}.cta-panel::after{content:"";position:absolute;width:230px;height:230px;right:-90px;bottom:-145px;border:34px solid rgba(37,99,235,.08);border-radius:50%}
  .dashboard-action div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button{min-height:44px;border-radius:11px;background:linear-gradient(135deg,#2563eb,#1d4ed8);box-shadow:0 10px 21px rgba(37,99,235,.23);letter-spacing:.005em}.dashboard-action div[data-testid="stButton"] button:hover,div[data-testid="stFormSubmitButton"] button:hover{background:linear-gradient(135deg,#3b82f6,#1d4ed8);box-shadow:0 14px 28px rgba(37,99,235,.33)}
  .section-title{color:var(--rl-heading,#102a43);font-size:clamp(1.7rem,3vw,2.15rem);margin-top:.35rem}.card{padding:1.45rem;border-radius:18px}.card::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#2563eb,#60a5fa,transparent)}
  [data-testid="stMetric"]{padding:.9rem 1rem;border:1px solid var(--rl-border,#e5eaf2);border-radius:14px;background:var(--rl-surface,#fff);box-shadow:0 7px 18px rgba(15,46,92,.04)}
  [data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;border:1px solid var(--rl-border,#e5eaf2)}[data-testid="stExpander"]{border-radius:13px;border-color:var(--rl-border,#e5eaf2)}
  form[data-testid="stForm"]{padding:1.3rem;border:1px solid var(--rl-border,#e5eaf2);border-radius:18px;background:var(--rl-surface,#fff);box-shadow:0 12px 28px rgba(15,46,92,.045)}
  @media (max-width:850px){.block-container{padding-top:7rem;padding-bottom:2rem}.dashboard-hero{min-height:unset;padding:2.35rem 1.65rem;border-radius:20px}.hero-visual{right:1.4rem;bottom:1.3rem;width:25%;min-width:135px}.dashboard-hero h1{max-width:72%;font-size:clamp(2rem,7vw,3.1rem)}.dashboard-hero p{max-width:68%}.dashboard-title{margin-top:2.15rem}.stat-card,.detail-card{margin-bottom:.25rem}}
  @media (max-width:640px){.block-container{padding-top:6.75rem;padding-left:1rem;padding-right:1rem}.dashboard-hero{padding:2rem 1.35rem}.dashboard-hero h1,.dashboard-hero p{max-width:100%}.dashboard-hero h1{font-size:clamp(2rem,10vw,2.65rem)}.dashboard-hero p{font-size:.96rem}.hero-visual{display:none}.hero-facts{margin-top:1.35rem;gap:.45rem}.hero-fact{font-size:.76rem;padding:.52rem .62rem}.dashboard-title{font-size:1.38rem}.cta-panel{padding:1.55rem}.cta-panel h2{font-size:1.35rem}form[data-testid="stForm"]{padding:1rem;border-radius:14px}div[data-testid="stHorizontalBlock"]:has(.brand){min-height:66px!important;padding:.55rem .75rem!important}.brand{font-size:1rem}.brand::before{width:24px;height:24px}div[data-testid="stHorizontalBlock"]:has(.brand) div[role="radiogroup"] label{font-size:.72rem;padding:.35rem .46rem!important}}
  @media (max-width:430px){div[data-testid="stHorizontalBlock"]:has(.brand)>div:first-child{max-width:92px!important;overflow:hidden}.brand span{display:none}.dashboard-hero{border-radius:17px}.stat-card{padding:1.15rem}.hero-fact:last-child{display:none}}
  /* Modern RiskLens navigation buttons */
div[data-testid="stHorizontalBlock"]:has(.brand)
div[data-testid="stButton"] button {
    background: transparent !important;
    color: #475569 !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    font-weight: 650 !important;
    min-height: 40px !important;
    padding: 0.45rem 0.55rem !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"]:has(.brand)
div[data-testid="stButton"] button:hover {
    background: #eff6ff !important;
    color: #2563eb !important;
    transform: translateY(-1px);
}

/* Theme button */
div[data-testid="stHorizontalBlock"]:has(.brand)
div[data-testid="stButton"]:last-child button {
    background: #eff6ff !important;
    color: #2563eb !important;
    border: 1px solid #bfdbfe !important;
    min-width: 42px !important;
}
</style>
""", unsafe_allow_html=True)

apply_theme()


@st.cache_data(show_spinner=False)
def load_dataset() -> pd.DataFrame:
    dataset_path = PROJECT_ROOT / "Loan_default.csv"

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Loan_default.csv not found at: {dataset_path}"
        )

    df = pd.read_csv(dataset_path)

    if df.empty:
        raise ValueError("Loan_default.csv is empty.")

    return df


def styled_dataframe(data: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Return a theme-aware cell style for Streamlit's native dataframe grid."""
    if st.session_state["theme"] == "dark":
        colors = {"background": "#0F1F33", "header": "#132E4F", "text": "#EAF2FF", "border": "#294563"}
    else:
        colors = {"background": "#FFFFFF", "header": "#EFF6FF", "text": "#182230", "border": "#DCE6F2"}
    return (
        data.style
        .set_properties(**{
            "background-color": colors["background"],
            "color": colors["text"],
            "border-color": colors["border"],
        })
        .set_table_styles([
            {"selector": "th", "props": [("background-color", colors["header"]), ("color", colors["text"]), ("border-color", colors["border"])]},
            {"selector": "td:hover", "props": [("background-color", "#173B66" if st.session_state["theme"] == "dark" else "#E8F1FF")]},
        ])
    )


def render_dataframe(data: pd.DataFrame, **kwargs: object) -> None:
    """Render the unchanged native dataframe behavior with theme-aware grid cells."""
    st.dataframe(styled_dataframe(data), **kwargs)


def api_metadata() -> dict:
    try:
        response = requests.get(f"{API_URL}/metadata", timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"categorical_options": CATEGORICAL_DEFAULTS}

def render_header() -> str:
    left, navigation, theme_control = st.columns([1.5, 4, 0.5])

    with left:
        st.markdown(
            '''
            <div class="brand">
                 <div class="brand-logo">RL</div>
                <div class="brand-text">Risk<span>Lens</span></div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with navigation:
        pages = [
            ("🏠", "Dashboard"),
            ("🎯", "Prediction"),
            ("📊", "Dataset"),
            ("🤖", "Model"),
            ("ℹ️", "About"),
        ]

        current_page = st.session_state.get("nav_page", "Dashboard")

        nav_cols = st.columns(5)

        for col, (icon, name) in zip(nav_cols, pages):
            with col:
                # active = current_page == name

                if st.button(
                    f"{icon}  {name}",
                    key=f"nav_{name}",
                    use_container_width=True
                ):
                    st.session_state["nav_page"] = name
                    st.rerun()

    with theme_control:
        is_dark = st.session_state["theme"] == "dark"

        st.button(
            "☀️" if is_dark else "🌙",
            key="theme_toggle",
            on_click=toggle_theme,
            help="Switch to Light Mode" if is_dark else "Switch to Dark Mode"
        )

    return st.session_state.get("nav_page", "Dashboard")



def go_to_prediction() -> None:
    st.session_state["nav_page"] = "Prediction"


def dashboard(df: pd.DataFrame) -> None:
    metadata = api_metadata()
    model_name = metadata.get("model_name", "LogisticRegression")
    target = metadata.get("target_variable", TARGET_VARIABLE)
    dataset_target = metadata.get("dataset_target_column", "Default")
    st.markdown(f'''<section class="dashboard-hero"><div class="dashboard-eyebrow">Machine learning prediction platform</div><h1>Intelligent loan-risk predictions, powered by machine learning.</h1><p>Explore the project context, review the data, and generate an applicant-specific default-risk assessment through a reliable local prediction workflow.</p><div class="hero-facts"><span class="hero-fact"><i>◈</i>Model: <b>{model_name}</b></span><span class="hero-fact"><i>◎</i>Target: <b>{target}</b></span><span class="hero-fact"><i>✓</i>Local Flask API</span></div><div class="hero-visual" aria-hidden="true"><svg viewBox="0 0 280 205" role="img"><rect class="chart-panel" x="14" y="34" width="252" height="151" rx="18"/><path class="chart-grid" d="M34 74H246M34 112H246M34 150H246M68 55V165M120 55V165M172 55V165M224 55V165"/><path class="chart-line" d="M34 148 C55 134 61 141 80 121 S109 126 126 99 S154 114 174 79 S205 99 224 63 S238 77 246 53"/><circle class="chart-dot" cx="246" cy="53" r="5"/><path class="node-line" d="M44 22L81 42M81 42L124 20M124 20L160 45M160 45L205 19M205 19L242 39"/><circle class="node" cx="44" cy="22" r="5"/><circle class="node" cx="81" cy="42" r="5"/><circle class="node" cx="124" cy="20" r="5"/><circle class="node" cx="160" cy="45" r="5"/><circle class="node" cx="205" cy="19" r="5"/><circle class="node" cx="242" cy="39" r="5"/></svg></div></section>''', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-action">', unsafe_allow_html=True)
    st.button("Start prediction", type="primary", on_click=go_to_prediction)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Project at a glance</div><p class="dashboard-intro">Live facts from the copied project dataset and trained model contract.</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    facts = [("Dataset rows", f"{len(df):,}", "Loan applications"), ("Features", "16", "Model input columns"), ("Model", model_name, "Classification algorithm"), ("Target", target, "Dataset column: " + dataset_target)]
    for col, (title, value, subtitle) in zip(cols, facts):
        with col: st.markdown(f'<div class="stat-card"><div class="stat-label">{title}</div><div class="stat-value">{value}</div><div class="stat-subtitle">{subtitle}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Model overview</div><p class="dashboard-intro">Inference uses the preserved preprocessing and feature order from the original model artifacts.</p>', unsafe_allow_html=True)
    model_col, process_col, data_col = st.columns(3)
    with model_col: st.markdown(f'<div class="detail-card"><h3>Model contract</h3><p><strong>Algorithm:</strong> {model_name}</p><p><strong>Target:</strong> {target}</p><p><strong>Feature count:</strong> 16</p></div>', unsafe_allow_html=True)
    with process_col: st.markdown('<div class="detail-card"><h3>Preprocessing</h3><p><strong>Categorical:</strong> 7 fitted LabelEncoders</p><p><strong>Numerical vector:</strong> StandardScaler</p><p><strong>Inference:</strong> Flask REST API</p></div>', unsafe_allow_html=True)
    with data_col: st.markdown(f'<div class="detail-card"><h3>Dataset context</h3><p><strong>Rows:</strong> {len(df):,}</p><p><strong>Columns:</strong> {len(df.columns)}</p><p><strong>Dataset target:</strong> {dataset_target}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Dataset overview</div><p class="dashboard-intro">A small local preview of the copied source dataset.</p>', unsafe_allow_html=True)
    st.markdown('<div class="dataset-card">', unsafe_allow_html=True)
    render_dataframe(df.head(6), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-panel"><h2>Ready to make a prediction?</h2><p>Submit applicant details to the validated Flask API and receive a model-backed default-risk assessment.</p><div class="dashboard-action">', unsafe_allow_html=True)
    st.button("Make prediction →", type="primary", key="bottom_prediction", on_click=go_to_prediction)
    st.markdown('</div></div>', unsafe_allow_html=True)


def prediction_page() -> None:
    st.markdown('<div class="section-title">Loan default prediction</div><p class="muted">Target Variable: <b>default</b> (0 = No Default, 1 = Default). Fields match the original model’s trained feature order.</p>', unsafe_allow_html=True)
    metadata = api_metadata()
    options = metadata.get("categorical_options", CATEGORICAL_DEFAULTS)
    with st.form("prediction_form"):
        demographic, financial, loan = st.columns(3)
        with demographic:
            st.subheader("Applicant profile")
            age = st.number_input("Age", min_value=18, max_value=100, value=35)
            education = st.selectbox("Education", options["Education"])
            employment = st.selectbox("Employment type", options["EmploymentType"])
            marital = st.selectbox("Marital status", options["MaritalStatus"])
            dependents = st.selectbox("Has dependents", options["HasDependents"])
        with financial:
            st.subheader("Financial profile")
            income = st.number_input("Annual income", min_value=0, value=65000, step=1000)
            credit_score = st.number_input("Credit score", min_value=300, max_value=850, value=680)
            employed_months = st.number_input("Months employed", min_value=0, value=36)
            credit_lines = st.number_input("Credit lines", min_value=0, value=3)
            dti = st.number_input("Debt-to-income ratio", min_value=0.0, max_value=1.0, value=0.35, step=0.01, format="%.2f")
        with loan:
            st.subheader("Loan request")
            loan_amount = st.number_input("Loan amount", min_value=0, value=50000, step=1000)
            interest = st.number_input("Interest rate (%)", min_value=0.0, max_value=100.0, value=11.5, step=0.1)
            term = st.number_input("Loan term (months)", min_value=1, value=36)
            purpose = st.selectbox("Loan purpose", options["LoanPurpose"])
            mortgage = st.selectbox("Has mortgage", options["HasMortgage"])
            cosigner = st.selectbox("Has co-signer", options["HasCoSigner"])
        submitted = st.form_submit_button("Generate risk assessment", use_container_width=True)
    if not submitted:
        return
    payload = {"Age": age, "Income": income, "LoanAmount": loan_amount, "CreditScore": credit_score, "MonthsEmployed": employed_months, "NumCreditLines": credit_lines, "InterestRate": interest, "LoanTerm": term, "DTIRatio": dti, "HasMortgage": mortgage, "HasDependents": dependents, "HasCoSigner": cosigner, "Education": education, "EmploymentType": employment, "MaritalStatus": marital, "LoanPurpose": purpose}
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        data = response.json()
        if not response.ok or not data.get("success"):
            st.error(data.get("error", "The API could not process this request.")); return
    except requests.RequestException:
        st.error(f"Unable to reach the Flask API at {API_URL}. Start the backend and try again."); return
    risk = data["default_probability"] * 100
    css = "result-risk" if data["prediction"] == 1 else "result-good"
    assessment = "Higher default risk" if data["prediction"] == 1 else "Lower default risk"
    st.markdown(f'<div class="card {css}"><div class="card-title">Assessment for target: default</div><div class="card-value">{assessment}</div><p>Prediction: <b>{data["label"]}</b> &nbsp; | &nbsp; Estimated default probability: <b>{risk:.2f}%</b></p></div>', unsafe_allow_html=True)
    with st.expander("Submitted feature values"):
        summary = pd.DataFrame({"Feature": payload.keys(), "Value": [str(value) for value in payload.values()]})
        render_dataframe(summary, use_container_width=True, hide_index=True)


def dataset_page(df: pd.DataFrame) -> None:

    st.markdown(
        '<div class="section-title">Dataset overview</div>'
        '<p class="muted">Local copy of the source dataset used for this application.</p>',
        unsafe_allow_html=True
    )

    # Dataset check
    if df is None or df.empty:
        st.warning("Dataset is empty or could not be loaded.")
        return

    # Dataset information
    a, b, c = st.columns(3)

    a.metric("Rows", f"{len(df):,}")
    b.metric("Columns", len(df.columns))
    c.metric("Dataset target column", "Default")

    # -------------------------
    # Preview
    # -------------------------
    st.subheader("Preview")

    preview_df = df.head(20)

    if preview_df.empty:
        st.info("No preview data available.")
    else:
        st.dataframe(
            preview_df,
            use_container_width=True,
            hide_index=True
        )

    # -------------------------
    # Numeric Summary
    # -------------------------
    st.subheader("Numeric summary")

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        st.info("No numeric columns available for summary.")
    else:
        summary_df = numeric_df.describe().T

        st.dataframe(
            summary_df,
            use_container_width=True
        )

    # -------------------------
    # Dataset Information
    # -------------------------
    st.subheader("Dataset information")

    info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Unique Values": df.nunique().values
    })

    st.dataframe(
        info_df,
        use_container_width=True,
        hide_index=True
    )


def model_page() -> None:
    st.markdown('<div class="section-title">Model information</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Algorithm</div><div class="card-value">Logistic Regression Classifier</div><p class="muted">The copied original artifacts apply fitted LabelEncoders to categorical fields, then StandardScaler to the complete 16-feature vector before inference.</p></div>', unsafe_allow_html=True)
    st.subheader("Target variable"); st.code("default  (0 = No Default, 1 = Default)")
    st.subheader("Feature order used during inference"); render_dataframe(pd.DataFrame({"Position": range(1, 17), "Feature": FEATURE_ORDER}), hide_index=True, use_container_width=True)


def about_page() -> None:
    st.markdown('<div class="section-title">About RiskLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><p>RiskLens is a local decision-support interface for the existing loan-default model. Streamlit collects and presents inputs; Flask validates requests and runs the copied original encoders, scaler, and classifier. This separation keeps the browser UI independent from model execution while preserving the original feature order and preprocessing.</p></div>', unsafe_allow_html=True)


page = render_header()

try:
    dataset = load_dataset()
except Exception as exc:
    st.error(f"Unable to read the copied dataset: {exc}")
    st.stop()

if page == "Dashboard":
    dashboard(dataset)

elif page == "Prediction":
    prediction_page()

elif page == "Dataset":
    dataset_page(dataset)

elif page == "Model":
    model_page()

elif page == "About":
    about_page()
