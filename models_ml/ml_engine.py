# ============================================================
# ml_engine.py
# ============================================================
# Carrega o modelo socioeconômico treinado e disponibiliza
# funções para uso no MVP3.
#
# - load_model(): carrega o modelo joblib
# - predict_vulnerability(): calcula vulnerabilidade 0–100
# - load_shap_artifacts(): carrega PNG & HTML
#
# ============================================================

import os
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
SHAP_PNG = os.path.join(MODEL_DIR, "shap_summary.png")
SHAP_HTML = os.path.join(MODEL_DIR, "shap_summary.html")


# ------------------------------------------------------------
# 1) Carregar modelo ML
# ------------------------------------------------------------

_model = None   # cache global


def load_model():
    global _model

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Modelo ML não encontrado em: {MODEL_PATH}"
            )
        _model = joblib.load(MODEL_PATH)

    return _model


# ------------------------------------------------------------
# 2) Prever vulnerabilidade socioeconômica
# ------------------------------------------------------------

def predict_vulnerability(indicators: dict) -> float:
    """
    Recebe os indicadores socioeconômicos:
        - PIB_per_capita
        - Densidade_hab_km2
        - Populacao
        - PIB_mil_reais

    Retorna score de vulnerabilidade (0–100).

    """
    model = load_model()

    X = pd.DataFrame([{
        "PIB_per_capita": indicators["PIB_per_capita"],
        "Densidade_hab_km2": indicators["Densidade_hab_km2"],
        "Populacao": indicators["Populacao"],
        "PIB_mil_reais": indicators["PIB_mil_reais"],
    }])

    pred = model.predict(X)[0]

    # Garantir limites 0–100
    pred = float(np.clip(pred, 0, 100))

    return pred


# ------------------------------------------------------------
# 3) Carregar artefatos SHAP
# ------------------------------------------------------------

def load_shap_artifacts():
    """
    Retorna caminhos de arquivos SHAP:
      - PNG estático
      - HTML interativo
    """
    if not os.path.exists(SHAP_PNG):
        raise FileNotFoundError(f"Arquivo não encontrado: {SHAP_PNG}")

    if not os.path.exists(SHAP_HTML):
        raise FileNotFoundError(f"Arquivo não encontrado: {SHAP_HTML}")

    return SHAP_PNG, SHAP_HTML


# ------------------------------------------------------------
# 4) Helper de saída para Streamlit
# ------------------------------------------------------------

def compute_ml_block(indicators: dict) -> dict:
    """
    Faz:
      - previsões ML
      - agrega indicadores
      - prepara painel para a UI

    Retorna:
      {
          "score": float,
          "category": str,
          "shap_png": "...",
          "shap_html": "..."
      }
    """

    score = predict_vulnerability(indicators)

    if score < 25:
        cat = "Baixa vulnerabilidade"
    elif score < 50:
        cat = "Moderada"
    elif score < 75:
        cat = "Alta"
    else:
        cat = "Crítica"

    shap_png, shap_html = load_shap_artifacts()

    return {
        "score": round(score, 1),
        "category": cat,
        "shap_png": shap_png,
        "shap_html": shap_html
    }
