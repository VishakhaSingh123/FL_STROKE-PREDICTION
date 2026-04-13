"""
FL Stroke Prediction Dashboard
Run: streamlit run dashboard.py
Place this file in your FL_STROKE-PREDICTION/ root directory.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import hashlib
import time
import subprocess
import sys
from datetime import datetime

# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FL Stroke Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark medical theme */
.stApp {
    background: #0a0d12;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1520 !important;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * {
    color: #94a3b8 !important;
}
[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0f1e2e 0%, #0d1821 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,120,255,0.06);
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: #2563eb; }
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 6px;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #38bdf8;
    font-family: 'Space Mono', monospace;
    line-height: 1;
}
.metric-sub {
    font-size: 12px;
    color: #475569;
    margin-top: 4px;
}

/* Block header */
.block-header {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #2563eb;
    margin-bottom: 4px;
}
.block-hash {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #64748b;
    word-break: break-all;
}
.block-event {
    font-size: 14px;
    font-weight: 600;
    color: #e2e8f0;
}

/* Chain block container */
.chain-block {
    background: #0f1a26;
    border: 1px solid #1e3a5f;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    position: relative;
}
.chain-block.genesis { border-left-color: #16a34a; }
.chain-block.end     { border-left-color: #dc2626; }
.chain-block.fit     { border-left-color: #7c3aed; }
.chain-block.eval    { border-left-color: #0ea5e9; }

/* Risk badge */
.risk-high   { color: #ef4444; font-weight: 700; font-size: 28px; }
.risk-medium { color: #f97316; font-weight: 700; font-size: 28px; }
.risk-low    { color: #22c55e; font-weight: 700; font-size: 28px; }

/* Terminal box for logs */
.terminal {
    background: #020408;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #4ade80;
    max-height: 340px;
    overflow-y: auto;
}

/* Section title */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 16px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: 1px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2d45;
}

/* status pill */
.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
}
.pill-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.pill-blue   { background: #0c1a35; color: #60a5fa; border: 1px solid #1d4ed8; }
.pill-red    { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }

/* plotly chart background override */
.js-plotly-plot .plotly .svg-container { background: transparent !important; }

/* streamlit overrides */
div[data-testid="stMarkdownContainer"] p { color: #94a3b8; }
.stButton>button {
    background: #1d4ed8;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    padding: 10px 24px;
    transition: background 0.2s;
}
.stButton>button:hover { background: #2563eb; }
.stSlider [data-testid="stTickBar"] { color: #64748b; }
label[data-testid="stWidgetLabel"] { color: #94a3b8 !important; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ── helper: load audit log ───────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_audit_log(path="audit_log.json"):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

# ── helper: load hospital CSVs ──────────────────────────────────────────────
@st.cache_data
def load_hospital_data():
    dfs = {}
    for i in range(1, 4):
        p = f"data/hospital_{i}.csv"
        if os.path.exists(p):
            dfs[f"Hospital {i}"] = pd.read_csv(p)
    return dfs

# ── helper: verify blockchain ───────────────────────────────────────────────
def verify_blockchain(chain):
    for i in range(1, len(chain)):
        cur = chain[i]
        prev = chain[i - 1]
        # recompute hash
        block_str = json.dumps({
            "index": cur["index"],
            "timestamp": cur["timestamp"],
            "event": cur["event"],
            "data": cur["data"],
            "previous_hash": cur["previous_hash"],
        }, sort_keys=True)
        expected = hashlib.sha256(block_str.encode()).hexdigest()
        if cur["hash"] != expected:
            return False, i
        if cur["previous_hash"] != prev["hash"]:
            return False, i
    return True, -1

# ── sidebar nav ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 FL Stroke")
    st.markdown("### Dashboard")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Overview", "⛓️ Blockchain Audit", "📊 Training Metrics", "🔍 Stroke Risk Predictor"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<div class="block-hash">Privacy-Preserving Stroke Prediction<br/>via Federated Learning</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    if st.button("🔄  Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE: OVERVIEW                                          ║
# ╚══════════════════════════════════════════════════════════╝
if page == "🏠 Overview":
    st.markdown('<div class="section-title">SYSTEM OVERVIEW</div>', unsafe_allow_html=True)

    chain = load_audit_log()
    dfs = load_hospital_data()

    # ── top metrics row ──────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    rounds = [b for b in chain if b["event"] == "ROUND_FIT_COMPLETE"]
    evals = [b for b in chain if b["event"] == "ROUND_EVALUATE_COMPLETE"]

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Hospitals</div>
            <div class="metric-value">{len(dfs)}</div>
            <div class="metric-sub">Federated clients</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">FL Rounds</div>
            <div class="metric-value">{len(rounds)}</div>
            <div class="metric-sub">Completed rounds</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        # latest avg recall across clients
        if evals:
            last = evals[-1]["data"]["client_metrics"]
            avg_recall = np.mean([m["recall"] for m in last])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Recall</div>
                <div class="metric-value">{avg_recall:.2%}</div>
                <div class="metric-sub">Latest round</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="metric-card">
                <div class="metric-label">Avg Recall</div>
                <div class="metric-value">—</div>
                <div class="metric-sub">No data yet</div>
            </div>""", unsafe_allow_html=True)

    with c4:
        total = sum(len(df) for df in dfs.values())
        stroke = sum(df["stroke"].sum() for df in dfs.values())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total:,}</div>
            <div class="metric-sub">{int(stroke)} stroke cases ({stroke/total:.1%})</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── data distribution ────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">DATA DISTRIBUTION</div>', unsafe_allow_html=True)
        if dfs:
            import plotly.graph_objects as go

            hosp_names = list(dfs.keys())
            stroke_counts = [int(dfs[h]["stroke"].sum()) for h in hosp_names]
            no_stroke = [len(dfs[h]) - s for h, s in zip(hosp_names, stroke_counts)]

            fig = go.Figure()
            fig.add_bar(name="No Stroke", x=hosp_names, y=no_stroke,
                        marker_color="#1d4ed8", marker_opacity=0.85)
            fig.add_bar(name="Stroke", x=hosp_names, y=stroke_counts,
                        marker_color="#ef4444", marker_opacity=0.9)
            fig.update_layout(
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=20, b=0),
                height=280,
            )
            fig.update_xaxes(showgrid=False, color="#475569")
            fig.update_yaxes(showgrid=True, gridcolor="#1e2d45", color="#475569")
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">AGE DISTRIBUTION BY STROKE</div>', unsafe_allow_html=True)
        if dfs:
            import plotly.graph_objects as go
            all_df = pd.concat(dfs.values())
            fig2 = go.Figure()
            fig2.add_histogram(
                x=all_df[all_df["stroke"] == 0]["age"].dropna(),
                name="No Stroke", nbinsx=30,
                marker_color="#1d4ed8", opacity=0.7,
            )
            fig2.add_histogram(
                x=all_df[all_df["stroke"] == 1]["age"].dropna(),
                name="Stroke", nbinsx=30,
                marker_color="#ef4444", opacity=0.85,
            )
            fig2.update_layout(
                barmode="overlay",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=20, b=0),
                height=280,
            )
            fig2.update_xaxes(showgrid=False, color="#475569", title="Age")
            fig2.update_yaxes(showgrid=True, gridcolor="#1e2d45", color="#475569")
            st.plotly_chart(fig2, use_container_width=True)

    # ── architecture diagram ─────────────────────────────────
    st.markdown('<div class="section-title">FEDERATED ARCHITECTURE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1422;border:1px solid #1e3a5f;border-radius:12px;padding:24px;font-family:'Space Mono',monospace;font-size:12px;color:#64748b;text-align:center;line-height:2;">
        <span style="color:#38bdf8;font-size:14px;font-weight:700;">FEDERATED SERVER</span><br/>
        FedAvg Aggregation · Blockchain Audit Logger<br/>
        <span style="color:#334155;">↕ Model Weights Only (No Raw Data)</span><br/>
        <br/>
        <span style="color:#7c3aed;">Hospital 1</span> &nbsp;|&nbsp; 
        <span style="color:#2563eb;">Hospital 2</span> &nbsp;|&nbsp; 
        <span style="color:#0ea5e9;">Hospital 3</span><br/>
        Local Training · Privacy Preserved<br/>
        <br/>
        <span style="color:#16a34a;font-size:11px;">⛓ Each round logged to tamper-resistant blockchain audit trail</span>
    </div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE: BLOCKCHAIN AUDIT                                  ║
# ╚══════════════════════════════════════════════════════════╝
elif page == "⛓️ Blockchain Audit":
    st.markdown('<div class="section-title">BLOCKCHAIN AUDIT LOG</div>', unsafe_allow_html=True)

    chain = load_audit_log()

    if not chain:
        st.warning("audit_log.json not found. Run the federated learning server first.")
        st.stop()

    # ── integrity check ──────────────────────────────────────
    valid, bad_idx = verify_blockchain(chain)
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        if valid:
            st.markdown('<span class="pill pill-green">✓ CHAIN VALID</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="pill pill-red">✗ INVALID at block {bad_idx}</span>', unsafe_allow_html=True)
    with col_v2:
        st.markdown(f'<span class="pill pill-blue">{len(chain)} BLOCKS</span>', unsafe_allow_html=True)
    with col_v3:
        if chain:
            ts = chain[-1]["timestamp"]
            st.markdown(f'<span class="pill pill-blue">LAST: {ts}</span>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── block timeline ───────────────────────────────────────
    EVENT_CLASS = {
        "GENESIS": "genesis",
        "SERVER_START": "fit",
        "ROUND_FIT_COMPLETE": "fit",
        "ROUND_EVALUATE_COMPLETE": "eval",
        "SERVER_END": "end",
    }

    for block in chain:
        ev = block["event"]
        cls = EVENT_CLASS.get(ev, "")
        data_str = ""

        if ev == "ROUND_EVALUATE_COMPLETE":
            metrics = block["data"].get("client_metrics", [])
            data_str = " &nbsp;·&nbsp; ".join(
                f"<span style='color:#60a5fa'>H{m['client']}</span> recall={m['recall']:.3f} f1={m['f1']:.3f}"
                for m in metrics
            )
        elif ev == "ROUND_FIT_COMPLETE":
            d = block["data"]
            data_str = f"clients={d['num_clients']} · failures={d['num_failures']}"
        else:
            data_str = " &nbsp;·&nbsp; ".join(f"{k}={v}" for k, v in block["data"].items())

        st.markdown(f"""
        <div class="chain-block {cls}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="block-header">Block #{block['index']} · {block['timestamp']}</div>
                    <div class="block-event">{ev}</div>
                    <div style="color:#64748b;font-size:12px;margin-top:4px;">{data_str}</div>
                </div>
            </div>
            <div style="margin-top:8px;">
                <span style="color:#475569;font-size:10px;font-family:'Space Mono',monospace;">
                HASH: {block['hash'][:32]}...
                &nbsp;|&nbsp;
                PREV: {block['previous_hash'][:32] if block['previous_hash'] != '0' else 'GENESIS'}...
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # raw JSON expander
    with st.expander("View raw JSON"):
        st.json(chain)


# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE: TRAINING METRICS                                  ║
# ╚══════════════════════════════════════════════════════════╝
elif page == "📊 Training Metrics":
    import plotly.graph_objects as go

    st.markdown('<div class="section-title">FEDERATED TRAINING METRICS</div>', unsafe_allow_html=True)

    chain = load_audit_log()
    evals = [b for b in chain if b["event"] == "ROUND_EVALUATE_COMPLETE"]

    if not evals:
        st.warning("No evaluation data found. Run the FL training first.")
        st.stop()

    # ── reshape data ──────────────────────────────────────────
    rows = []
    for block in evals:
        rnd = block["data"]["round"]
        for cm in block["data"]["client_metrics"]:
            rows.append({
                "round": rnd,
                "hospital": f"Hospital {cm['client']}",
                "recall": cm["recall"],
                "precision": cm["precision"],
                "f1": cm["f1"],
            })
    df_metrics = pd.DataFrame(rows)

    hospitals = df_metrics["hospital"].unique()
    colors = {"Hospital 1": "#7c3aed", "Hospital 2": "#2563eb", "Hospital 3": "#0ea5e9"}

    # ── summary cards ─────────────────────────────────────────
    latest = df_metrics[df_metrics["round"] == df_metrics["round"].max()]
    c1, c2, c3 = st.columns(3)
    for col, metric, label in zip([c1, c2, c3], ["recall", "precision", "f1"], ["Avg Recall", "Avg Precision", "Avg F1"]):
        val = latest[metric].mean()
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val:.3f}</div>
                <div class="metric-sub">Round {df_metrics['round'].max()} avg</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── line charts ───────────────────────────────────────────
    for metric, title in [("recall", "RECALL"), ("precision", "PRECISION"), ("f1", "F1 SCORE")]:
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:12px;letter-spacing:2px;color:#475569;margin-bottom:8px;">{title} PER ROUND</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for h in hospitals:
            sub = df_metrics[df_metrics["hospital"] == h].sort_values("round")
            fig.add_scatter(
                x=sub["round"], y=sub[metric],
                name=h,
                mode="lines+markers",
                line=dict(color=colors.get(h, "#94a3b8"), width=2),
                marker=dict(size=8),
            )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=10, b=0),
            height=220,
            xaxis=dict(tickmode="linear", tick0=1, dtick=1, showgrid=False, title="Round", color="#475569"),
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", color="#475569", range=[0, 1.05]),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── per-hospital table ────────────────────────────────────
    st.markdown('<div class="section-title">DETAILED METRICS TABLE</div>', unsafe_allow_html=True)
    styled = df_metrics.rename(columns={"round": "Round", "hospital": "Hospital",
                                         "recall": "Recall", "precision": "Precision", "f1": "F1"})
    st.dataframe(
        styled.style.format({"Recall": "{:.4f}", "Precision": "{:.4f}", "F1": "{:.4f}"}),
        use_container_width=True,
    )

    # ── radar chart ───────────────────────────────────────────
    st.markdown('<div class="section-title">PERFORMANCE RADAR (LATEST ROUND)</div>', unsafe_allow_html=True)
    categories = ["Recall", "Precision", "F1"]
    fig_r = go.Figure()
    for h in hospitals:
        sub = latest[latest["hospital"] == h]
        if not sub.empty:
            vals = [sub["recall"].values[0], sub["precision"].values[0], sub["f1"].values[0]]
            vals_closed = vals + [vals[0]]
            fig_r.add_trace(go.Scatterpolar(
                r=vals_closed,
                theta=categories + [categories[0]],
                fill="toself",
                name=h,
                line_color=colors.get(h, "#94a3b8"),
                fillcolor=colors.get(h, "#94a3b8").replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in colors.get(h, "") else colors.get(h, "#94a3b8") + "26",
            ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], color="#475569", gridcolor="#1e2d45"),
            angularaxis=dict(color="#94a3b8"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=360,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_r, use_container_width=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE: STROKE RISK PREDICTOR                             ║
# ╚══════════════════════════════════════════════════════════╝
elif page == "🔍 Stroke Risk Predictor":
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    st.markdown('<div class="section-title">STROKE RISK PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748b;font-size:13px;">Uses a model trained on all hospital data combined. '
        'Enter patient details to estimate stroke risk.</p>',
        unsafe_allow_html=True,
    )

    # ── load & train ──────────────────────────────────────────
    @st.cache_resource
    def get_trained_model():
        dfs = []
        for i in range(1, 4):
            p = f"data/hospital_{i}.csv"
            if os.path.exists(p):
                dfs.append(pd.read_csv(p))
        if not dfs:
            return None, None, None, None
        df = pd.concat(dfs, ignore_index=True)
        df["bmi"].fillna(df["bmi"].mean(), inplace=True)
        cat_cols = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
        encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        X = df.drop(["stroke", "id"], axis=1, errors="ignore")
        y = df["stroke"]
        scaler = StandardScaler()
        X_s = scaler.fit_transform(X)
        model = LogisticRegression(max_iter=1000, class_weight="balanced")
        model.fit(X_s, y)
        return model, scaler, encoders, list(X.columns)

    model, scaler, encoders, feature_cols = get_trained_model()

    if model is None:
        st.error("Hospital CSV files not found. Run split_data.py first.")
        st.stop()

    # ── input form ────────────────────────────────────────────
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("**Patient Information**")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.slider("Age", 0.1, 82.0, 55.0, 0.5)
        ever_married = st.selectbox("Ever Married", ["Yes", "No"])
        work_type = st.selectbox("Work Type", ["Private", "Self-employed", "Govt_job", "children", "Never_worked"])
        residence = st.selectbox("Residence Type", ["Urban", "Rural"])
        smoking = st.selectbox("Smoking Status", ["never smoked", "formerly smoked", "smokes", "Unknown"])

    with col_r:
        st.markdown("**Clinical Data**")
        hypertension = st.radio("Hypertension", [0, 1], format_func=lambda x: "Yes" if x else "No", horizontal=True)
        heart_disease = st.radio("Heart Disease", [0, 1], format_func=lambda x: "Yes" if x else "No", horizontal=True)
        avg_glucose = st.slider("Avg Glucose Level (mg/dL)", 55.0, 272.0, 100.0, 0.5)
        bmi = st.slider("BMI", 10.0, 98.0, 28.0, 0.1)

    # ── predict ───────────────────────────────────────────────
    if st.button("CALCULATE STROKE RISK"):
        raw = {
            "gender": gender,
            "age": age,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "ever_married": ever_married,
            "work_type": work_type,
            "Residence_type": residence,
            "avg_glucose_level": avg_glucose,
            "bmi": bmi,
            "smoking_status": smoking,
        }

        inp = {}
        cat_cols_pred = ["gender", "ever_married", "work_type", "Residence_type", "smoking_status"]
        for k, v in raw.items():
            if k in cat_cols_pred:
                try:
                    inp[k] = encoders[k].transform([v])[0]
                except ValueError:
                    inp[k] = 0
            else:
                inp[k] = v

        row = pd.DataFrame([{col: inp.get(col, 0) for col in feature_cols}])
        row_s = scaler.transform(row)
        prob = model.predict_proba(row_s)[0][1]

        # risk level
        if prob >= 0.5:
            risk_class = "risk-high"
            risk_label = "HIGH RISK"
            risk_color = "#ef4444"
        elif prob >= 0.25:
            risk_class = "risk-medium"
            risk_label = "MODERATE RISK"
            risk_color = "#f97316"
        else:
            risk_class = "risk-low"
            risk_label = "LOW RISK"
            risk_color = "#22c55e"

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0f1a26;border:1px solid {risk_color}33;border-left:4px solid {risk_color};
                    border-radius:12px;padding:28px 32px;text-align:center;">
            <div style="font-family:'Space Mono',monospace;font-size:11px;letter-spacing:3px;color:#64748b;margin-bottom:8px;">STROKE RISK SCORE</div>
            <div class="{risk_class}">{prob:.1%}</div>
            <div style="font-family:'Space Mono',monospace;font-size:13px;letter-spacing:2px;color:{risk_color};margin-top:8px;">{risk_label}</div>
            <div style="color:#475569;font-size:12px;margin-top:12px;">Threshold: 0.25 (optimised for recall)</div>
        </div>
        """, unsafe_allow_html=True)

        # contributing factors gauge
        import plotly.graph_objects as go
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            number={"suffix": "%", "font": {"color": risk_color, "family": "Space Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569"},
                "bar": {"color": risk_color},
                "bgcolor": "#0f1a26",
                "steps": [
                    {"range": [0, 25], "color": "#052e16"},
                    {"range": [25, 50], "color": "#1c1003"},
                    {"range": [50, 100], "color": "#2d0a0a"},
                ],
                "threshold": {
                    "line": {"color": "#ffffff", "width": 2},
                    "thickness": 0.75,
                    "value": 25,
                },
            },
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=220,
            margin=dict(l=20, r=20, t=20, b=0),
        )
        st.plotly_chart(fig_g, use_container_width=True)

        # risk factors summary
        st.markdown('<div class="section-title">RISK FACTOR SUMMARY</div>', unsafe_allow_html=True)
        risk_factors = []
        if age > 65:          risk_factors.append(("Age > 65", "HIGH"))
        if hypertension:      risk_factors.append(("Hypertension", "HIGH"))
        if heart_disease:     risk_factors.append(("Heart Disease", "HIGH"))
        if avg_glucose > 140: risk_factors.append(("High Glucose", "MODERATE"))
        if bmi > 30:          risk_factors.append(("High BMI", "MODERATE"))
        if smoking == "smokes": risk_factors.append(("Smoker", "MODERATE"))
        if ever_married == "Yes" and age > 50: risk_factors.append(("Married + Age", "LOW"))

        if risk_factors:
            for factor, level in risk_factors:
                pill_cls = "pill-red" if level == "HIGH" else "pill-blue" if level == "MODERATE" else "pill-green"
                st.markdown(
                    f'<span class="pill {pill_cls}">{level}</span> &nbsp; {factor}<br/>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="pill pill-green">LOW RISK PROFILE</span>', unsafe_allow_html=True)

        st.markdown("""
        <br/><div style="background:#0f1a26;border:1px solid #1e2d45;border-radius:8px;padding:14px 18px;
                         font-size:12px;color:#475569;">
        ⚠️ This prediction is for research purposes only and should not replace professional medical advice.
        </div>
        """, unsafe_allow_html=True)