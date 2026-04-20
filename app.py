import streamlit as st
import random
from dataclasses import dataclass, field
from typing import List
import pandas as pd

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MediAlloc — Hospital Bed Allocation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .main-header h1 {
        color: white;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #93c5fd;
        margin: 4px 0 0;
        font-size: 14px;
    }
    .header-badge {
        background: rgba(255,255,255,0.15);
        color: #bfdbfe;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Stat cards */
    .stat-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .stat-label { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-value { font-size: 32px; font-weight: 700; margin-top: 4px; }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-critical { background: #ede9fe; color: #6d28d9; }
    .badge-high     { background: #fee2e2; color: #dc2626; }
    .badge-moderate { background: #fef3c7; color: #b45309; }
    .badge-low      { background: #dcfce7; color: #16a34a; }
    .badge-allocated { background: #dcfce7; color: #15803d; }
    .badge-rejected  { background: #fee2e2; color: #dc2626; }
    .badge-waiting   { background: #f1f5f9; color: #64748b; }

    /* Algorithm info banner */
    .algo-banner {
        background: #dbeafe;
        border: 1px solid #93c5fd;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 13px;
        color: #1e40af;
        margin-bottom: 16px;
        line-height: 1.6;
    }

    /* Section headers */
    .section-header {
        font-size: 13px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Result row styling */
    .result-allocated { border-left: 3px solid #16a34a; padding-left: 10px; }
    .result-rejected  { border-left: 3px solid #dc2626; padding-left: 10px; }

    /* Progress bar custom */
    .stProgress > div > div > div > div {
        background: #1d4ed8;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* Remove default streamlit padding */
    .block-container { padding-top: 1.5rem; }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    /* DataFrame */
    .dataframe { font-size: 13px !important; }

    /* Metric */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
CONDITIONS = {
    "Cardiac Arrest":       {"severity": 10, "days": 7},
    "Stroke":               {"severity": 9,  "days": 10},
    "Trauma / Accident":    {"severity": 9,  "days": 8},
    "Respiratory Failure":  {"severity": 8,  "days": 6},
    "Sepsis":               {"severity": 8,  "days": 9},
    "Appendicitis":         {"severity": 6,  "days": 3},
    "Fracture":             {"severity": 5,  "days": 5},
    "Pneumonia":            {"severity": 6,  "days": 7},
    "Diabetes Crisis":      {"severity": 7,  "days": 4},
    "Hypertension Crisis":  {"severity": 7,  "days": 3},
    "Minor Surgery":        {"severity": 3,  "days": 2},
    "Observation":          {"severity": 2,  "days": 1},
}

SAMPLE_PATIENTS = [
    ("Rahul Sharma",   45, "Cardiac Arrest"),
    ("Meera Iyer",     62, "Stroke"),
    ("Arjun Patel",    28, "Trauma / Accident"),
    ("Sunita Reddy",   55, "Respiratory Failure"),
    ("Dev Kumar",      70, "Sepsis"),
    ("Priya Nair",     38, "Diabetes Crisis"),
    ("Kiran Shah",     50, "Pneumonia"),
    ("Leela Singh",    33, "Hypertension Crisis"),
    ("Vikram Gupta",   40, "Appendicitis"),
    ("Nisha Joshi",    22, "Fracture"),
    ("Aarav Menon",    65, "Minor Surgery"),
    ("Deepa Verma",    29, "Observation"),
]

FIRST_NAMES = ["Arjun","Meera","Rajan","Priya","Sanjay","Kavya","Vikram","Deepa","Rahul","Sunita","Aarav","Leela","Kiran","Nisha","Dev"]
LAST_NAMES  = ["Sharma","Patel","Kumar","Singh","Reddy","Nair","Iyer","Shah"]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def severity_info(s):
    if s >= 9: return "Critical", "#6d28d9", "🔴"
    if s >= 7: return "High",     "#dc2626", "🟠"
    if s >= 4: return "Moderate", "#b45309", "🟡"
    return           "Low",      "#16a34a", "🟢"

def make_patient(name, age, condition, sev_override=0):
    d   = CONDITIONS[condition]
    sev = sev_override if sev_override > 0 else d["severity"]
    pid = f"P{st.session_state.pid_counter:03d}"
    st.session_state.pid_counter += 1
    benefit = round(sev * d["days"], 2)
    ratio   = round(sev / max(d["days"], 0.01), 3)
    return {
        "pid": pid, "name": name, "age": age,
        "condition": condition, "severity": sev,
        "days": d["days"], "benefit": benefit, "ratio": ratio,
        "alloc_days": 0.0, "status": "Waiting",
    }

# ─────────────────────────────────────────────
#  FRACTIONAL KNAPSACK
# ─────────────────────────────────────────────
def fractional_knapsack(patients, capacity):
    for p in patients:
        p["alloc_days"] = 0.0
        p["status"]     = "Waiting"

    ordered       = sorted(patients, key=lambda p: p["ratio"], reverse=True)
    remaining     = capacity
    total_benefit = 0.0
    steps         = []

    for i, p in enumerate(ordered):
        if remaining <= 0:
            p["status"] = "Rejected"
            steps.append({
                "Step": i+1, "Patient": p["name"], "Condition": p["condition"],
                "Severity": p["severity"], "Ratio": p["ratio"],
                "Requested (d)": p["days"], "Allocated (d)": 0,
                "Remaining After": round(remaining, 1), "Status": "Rejected",
            })
            continue

        if p["days"] <= remaining:
            p["status"]     = "Allocated"
            p["alloc_days"] = p["days"]
            remaining      -= p["days"]
            total_benefit  += p["benefit"]
        else:
            p["status"]     = "Rejected"
            p["alloc_days"] = 0.0

        steps.append({
            "Step": i+1, "Patient": p["name"], "Condition": p["condition"],
            "Severity": p["severity"], "Ratio": p["ratio"],
            "Requested (d)": p["days"], "Allocated (d)": round(p["alloc_days"], 1),
            "Remaining After": round(remaining, 1), "Status": p["status"],
        })

    return ordered, round(total_benefit, 2), steps

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "patients"    not in st.session_state: st.session_state.patients    = []
if "pid_counter" not in st.session_state: st.session_state.pid_counter = 1
if "results"     not in st.session_state: st.session_state.results     = None
if "steps"       not in st.session_state: st.session_state.steps       = None
if "ran"         not in st.session_state: st.session_state.ran         = False

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <h1>🏥 MediAlloc</h1>
    <p>Smart Hospital Bed Allocation System</p>
  </div>
  <div class="header-badge">Fractional Knapsack Algorithm</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Hospital Configuration")
    total_beds = st.number_input("Total Beds Available", min_value=1, max_value=500, value=20)
    avg_stay   = st.number_input("Avg. Stay per Patient (days)", min_value=1.0, max_value=30.0, value=5.0, step=0.5)
    capacity   = total_beds * avg_stay
    st.info(f"**Total capacity:** {capacity:.1f} bed-days")

    st.markdown("---")
    st.markdown("### ➕ Add Patient")

    p_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
    p_age  = st.number_input("Age", min_value=1, max_value=120, value=35)
    p_cond = st.selectbox("Medical Condition", list(CONDITIONS.keys()))

    # Live severity preview
    d = CONDITIONS[p_cond]
    label, color, dot = severity_info(d["severity"])
    st.markdown(
        f"<div style='background:#f1f5f9;border-radius:8px;padding:8px 12px;font-size:13px;margin:4px 0 8px'>"
        f"{dot} <b>Severity {d['severity']}/10</b> · {label} · ~{d['days']} days</div>",
        unsafe_allow_html=True
    )

    p_sev_override = st.slider("Severity Override (0 = auto)", 0.0, 10.0, 0.0, step=0.5)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Patient", type="primary", use_container_width=True):
            if not p_name.strip():
                st.error("Please enter a name.")
            else:
                st.session_state.patients.append(
                    make_patient(p_name.strip(), p_age, p_cond, p_sev_override)
                )
                st.success(f"Added {p_name}")
                st.rerun()
    with col2:
        if st.button("Random", use_container_width=True):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            age  = random.randint(18, 82)
            cond = random.choice(list(CONDITIONS.keys()))
            st.session_state.patients.append(make_patient(name, age, cond))
            st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 Actions")

    if st.button("⚡ Run Allocation Algorithm", type="primary", use_container_width=True):
        if not st.session_state.patients:
            st.error("Add patients first.")
        else:
            ordered, benefit, steps = fractional_knapsack(st.session_state.patients, capacity)
            st.session_state.results  = ordered
            st.session_state.steps    = steps
            st.session_state.benefit  = benefit
            st.session_state.capacity = capacity
            st.session_state.ran      = True
            st.rerun()

    if st.button("📋 Load Sample Patients", use_container_width=True):
        st.session_state.patients    = []
        st.session_state.pid_counter = 1
        st.session_state.ran         = False
        for name, age, cond in SAMPLE_PATIENTS:
            st.session_state.patients.append(make_patient(name, age, cond))
        st.rerun()

    if st.button("🗑 Clear All Patients", use_container_width=True):
        st.session_state.patients    = []
        st.session_state.pid_counter = 1
        st.session_state.results     = None
        st.session_state.steps       = None
        st.session_state.ran         = False
        st.rerun()

# ─────────────────────────────────────────────
#  STAT CARDS
# ─────────────────────────────────────────────
patients = st.session_state.patients
alloc_count  = sum(1 for p in patients if p["status"] == "Allocated")
reject_count = sum(1 for p in patients if p["status"] == "Rejected")
used_days    = sum(p["alloc_days"] for p in patients)
util_pct     = round(used_days / capacity * 100, 1) if (capacity > 0 and st.session_state.ran) else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("👥 Total Patients", len(patients))
with c2:
    st.metric("✅ Allocated", alloc_count)
with c3:
    st.metric("❌ Rejected", reject_count)
with c4:
    st.metric("📊 Utilisation", f"{util_pct}%")
with c5:
    benefit_val = st.session_state.get("benefit", 0)
    st.metric("💎 Total Benefit", f"{benefit_val:.0f}")

st.markdown("---")

# ─────────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Patient Queue", "✅ Allocation Results", "🔬 Algorithm Steps"])

# ── TAB 1: PATIENT QUEUE ─────────────────────
with tab1:
    if not patients:
        st.info("No patients in queue. Use the sidebar to add patients or load sample data.")
    else:
        st.markdown(f"**{len(patients)} patient(s) in queue**")

        # Remove patient
        remove_options = {f"{p['pid']} — {p['name']}": i for i, p in enumerate(patients)}
        selected_remove = st.selectbox("Select patient to remove:", ["— select —"] + list(remove_options.keys()))
        if st.button("✕ Remove Selected Patient", type="secondary"):
            if selected_remove == "— select —":
                st.warning("Please select a patient to remove.")
            else:
                idx = remove_options[selected_remove]
                removed = patients.pop(idx)
                st.success(f"Removed {removed['name']}")
                st.rerun()

        st.markdown("---")

        # Patient table
        rows = []
        for p in patients:
            label, _, dot = severity_info(p["severity"])
            rows.append({
                "PID":       p["pid"],
                "Name":      p["name"],
                "Age":       p["age"],
                "Condition": p["condition"],
                "Severity":  f"{p['severity']:.1f}",
                "Level":     f"{dot} {label}",
                "Days":      f"{p['days']}d",
                "Benefit":   f"{p['benefit']:.1f}",
                "Ratio":     f"{p['ratio']:.3f}",
                "Status":    p["status"],
            })

        df = pd.DataFrame(rows)

        def color_status(val):
            if val == "Allocated": return "color: #16a34a; font-weight: 600"
            if val == "Rejected":  return "color: #dc2626; font-weight: 600"
            return "color: #64748b"

        def color_level(val):
            if "Critical" in val: return "color: #6d28d9; font-weight: 600"
            if "High"     in val: return "color: #dc2626"
            if "Moderate" in val: return "color: #b45309"
            return "color: #16a34a"

        styled = df.style.applymap(color_status, subset=["Status"]) \
                         .applymap(color_level,  subset=["Level"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ── TAB 2: ALLOCATION RESULTS ────────────────
with tab2:
    if not st.session_state.ran:
        st.info("Run the allocation algorithm from the sidebar to see results here.")
    else:
        ordered  = st.session_state.results
        capacity = st.session_state.capacity

        # Summary metrics
        alloc_days  = sum(p["alloc_days"] for p in ordered if p["status"] == "Allocated")
        reject_days = sum(p["days"]       for p in ordered if p["status"] == "Rejected")

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.metric("Bed-Days Allocated", f"{alloc_days:.1f}d")
        with mc2:
            st.metric("Bed-Days Freed", f"{capacity - alloc_days:.1f}d")
        with mc3:
            st.metric("Total Benefit Score", f"{st.session_state.benefit:.1f}")

        # Progress bar
        util = alloc_days / max(capacity, 0.01)
        st.markdown(f"**Capacity Utilisation: {util*100:.1f}%**")
        st.progress(min(util, 1.0))

        st.markdown("---")
        st.markdown("**Patients sorted by greedy ratio (Severity ÷ Days)**")

        rows = []
        for i, p in enumerate(ordered, 1):
            label, _, dot = severity_info(p["severity"])
            rows.append({
                "Rank":         i,
                "Name":         p["name"],
                "Condition":    p["condition"],
                "Severity":     f"{p['severity']:.1f}",
                "Ratio":        f"{p['ratio']:.3f}",
                "Requested":    f"{p['days']}d",
                "Allocated":    f"{p['alloc_days']:.1f}d",
                "Status":       p["status"],
            })

        df2 = pd.DataFrame(rows)

        def color_status2(val):
            if val == "Allocated": return "color: #16a34a; font-weight: 700; background-color: #f0fdf4"
            if val == "Rejected":  return "color: #dc2626; font-weight: 700; background-color: #fef2f2"
            return ""

        styled2 = df2.style.applymap(color_status2, subset=["Status"])
        st.dataframe(styled2, use_container_width=True, hide_index=True)

# ── TAB 3: ALGORITHM STEPS ───────────────────
with tab3:
    st.markdown("""
    <div class="algo-banner">
    <b>Fractional Knapsack — How it works:</b><br>
    1. Compute <b>Ratio = Severity ÷ Treatment Days</b> for every patient (value density).<br>
    2. <b>Sort descending</b> by ratio — highest priority gets beds first (greedy choice).<br>
    3. Iterate: if patient fits in remaining capacity → <b>Allocate</b>, else → <b>Reject</b>.<br>
    4. Time complexity: <b>O(n log n)</b> for sorting + O(n) for the loop.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.ran:
        st.info("Run the algorithm to see step-by-step execution.")
    else:
        steps = st.session_state.steps

        rows = []
        for s in steps:
            rows.append({
                "Step":           s["Step"],
                "Patient":        s["Patient"],
                "Condition":      s["Condition"],
                "Severity":       s["Severity"],
                "Ratio":          s["Ratio"],
                "Requested":      f"{s['Requested (d)']}d",
                "Allocated":      f"{s['Allocated (d)']}d",
                "Remaining Cap.": f"{s['Remaining After']}d",
                "Decision":       s["Status"],
            })

        df3 = pd.DataFrame(rows)

        def color_decision(val):
            if val == "Allocated": return "color: #16a34a; font-weight: 700"
            if val == "Rejected":  return "color: #dc2626; font-weight: 700"
            return ""

        styled3 = df3.style.applymap(color_decision, subset=["Decision"])
        st.dataframe(styled3, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#94a3b8;padding:8px'>"
    "MediAlloc · Analysis of Algorithms Project · Fractional Knapsack Algorithm"
    "</div>",
    unsafe_allow_html=True
)
