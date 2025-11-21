# combined_risk_engine.py
# ============================================================
# Combina risco climático com risco socioeconômico (ML).
# Pesos padrão: 60% clima + 40% socioeconômico ML.
# ============================================================

from typing import Dict, Optional


def _categorize(score: float) -> str:
    """Categorias padrão."""
    if score < 25:
        return "Baixo"
    if score < 50:
        return "Moderado"
    if score < 75:
        return "Alto"
    return "Crítico"


def combine_risks(
    climate_risk: Dict,
    socio_like_risk: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Combinação linear de riscos com normalização de pesos.
    """

    # -----------------------
    # 1) Pesos padrão (OPÇÃO A)
    # -----------------------
    if weights is None:
        weights = {"climate": 0.6, "socioecon": 0.4}

    # Normalização robusta
    w_climate = float(weights.get("climate", 0.6))
    w_socio = float(weights.get("socioecon", 0.4))

    total = w_climate + w_socio
    if total <= 0:
        w_climate, w_socio = 0.6, 0.4
        total = 1.0

    w_climate /= total
    w_socio /= total

    # -----------------------
    # 2) Scores individuais
    # -----------------------
    climate_score = float(climate_risk.get("score", 0.0))
    socio_score = float(socio_like_risk.get("score", 0.0))

    # -----------------------
    # 3) Combinação
    # -----------------------
    combined = w_climate * climate_score + w_socio * socio_score
    combined = max(0.0, min(100.0, combined))
    combined_rounded = round(combined, 1)

    category = _categorize(combined_rounded)

    # -----------------------
    # 4) Pacote unificado
    # -----------------------
    return {
        "score": combined_rounded,
        "category": category,
        "weights": {
            "climate": round(w_climate, 2),
            "socioecon": round(w_socio, 2),
        },
        "components": {
            "climate_score": round(climate_score, 1),
            "socioecon_score": round(socio_score, 1),
        },
    }
