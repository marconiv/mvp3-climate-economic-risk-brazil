# theme.py
import streamlit as st

def inject_custom_css():
    st.markdown(
        """
        <style>

        /* ======== FUNDO GERAL ======== */
        .stApp {
            background: radial-gradient(circle at top left, #3b3c89, #161733);
            color: #ffffff;
        }

        /* ======== SIDEBAR ======== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1f2141, #121326);
            border-right: 1px solid rgba(255,255,255,0.12);
        }

        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] p {
            color: rgba(255,255,255,0.95) !important;
            font-size: 0.9rem;
        }

        /* LABELS DOS WIDGETS */
        label[data-testid="stWidgetLabel"] {
            color: #ffffff !important;
        }

        /* SELECTBOX: mantém dropdown padrão, só ajusta texto interno */
        div[data-baseweb="select"] * {
            color: #000000 !important;  /* texto preto no box branco */
        }

        /* ======== BOTÕES PILL (PT/EN + Analisar) ======== */
        .stButton > button {
            border-radius: 999px;
            padding: 6px 18px;
            border: 1px solid rgba(255,255,255,0.45);
            background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.02));
            color: #ffffff;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.15s ease-in-out;
        }

        .stButton > button:hover {
            border-color: rgba(255,255,255,0.8);
            background: linear-gradient(135deg, rgba(255,255,255,0.20), rgba(255,255,255,0.06));
        }

        /* Botão em foco */
        .stButton > button:focus:not(:active) {
            outline: none;
            box-shadow: 0 0 0 2px rgba(255,255,255,0.45);
        }

        /* ======== TÍTULOS ======== */
        h1, h2, h3, h4 {
            color: #ffffff !important;
        }

        /* ======== CARDS ======== */
        .card {
            background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: 0 18px 30px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255,255,255,0.12);
        }

        .card-header {
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: rgba(255,255,255,0.95);
        }

        .card-subtitle {
            font-size: 0.92rem;
            color: rgba(255,255,255,0.92);
            margin-bottom: 8px;
        }

        /* ======== MÉTRICAS GRANDES ======== */
        .big-metric {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 4px;
            color: #ffffff;
        }

        .big-metric-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.9;
        }

        /* ======== MINI MÉTRICAS (PIB, População etc.) ======== */
        .mini-metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 26px;
            margin-top: 12px;
        }

        .mini-metric {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .mini-metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: rgba(255,255,255,0.95);
        }

        .mini-metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff;
        }

        @media (max-width: 900px) {
            .mini-metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        /* ======== ALERTAS & INFOS ======== */
        .stAlert, .stInfo, .stWarning, .stError {
            color: #ffffff !important;
        }

        .stInfo > div {
            background: rgba(255,255,255,0.12) !important;
            border-radius: 14px;
            padding: 14px;
        }

        /* ======== BADGES DE RISCO ======== */
        .risk-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-left: 10px;
        }

        .risk-low       { background: rgba(46,204,113,0.16);  color:#2ecc71;  border:1px solid rgba(46,204,113,0.5); }
        .risk-med       { background: rgba(241,196,15,0.16);  color:#f1c40f;  border:1px solid rgba(241,196,15,0.5); }
        .risk-high      { background: rgba(230,126,34,0.16);  color:#e67e22;  border:1px solid rgba(230,126,34,0.5); }
        .risk-critical  { background: rgba(231,76,60,0.16);   color:#e74c3c;  border:1px solid rgba(231,76,60,0.5); }

        /* ======== PROGRESS BAR ======== */
        .stProgress > div > div {
            border-radius: 999px;
        }

        /* ======== TABELAS (st.dataframe) ======== */
        div[data-testid="stDataFrame"] table {
            color: #ffffff !important;
            font-size: 0.9rem;
            font-weight: 600;
        }

        div[data-testid="stDataFrame"] thead tr th {
            color: #ffffff !important;
            font-weight: 700 !important;
            background-color: rgba(0,0,0,0.25);
        }

        /* ======== TEXTO GERAL NOS CARDS (Rationale / Nota) ======== */
        .card-body-text {
            font-size: 0.92rem;
            line-height: 1.55;
            color: rgba(255,255,255,0.94);
        }

        .card-body-text ul {
            margin-top: 6px;
            margin-bottom: 0;
            padding-left: 20px;
        }

        .card-body-text li {
            margin-bottom: 4px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
