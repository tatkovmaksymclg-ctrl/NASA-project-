"""Демонстраційна модель оцінювання відхилень фізіологічних показників."""

def assess_measurement(row: dict) -> dict:
    """
    Повертає сумарний бал ризику, категорію та пояснення.
    Межі умовні: вони потрібні лише для демонстрації логіки програми.
    """
    score = 0
    reasons = []

    hr = float(row["heart_rate"])
    spo2 = float(row["spo2"])
    temp = float(row["temperature"])
    sys_bp = float(row["systolic"])
    dia_bp = float(row["diastolic"])
    resp = float(row["respiration"])

    if hr < 50 or hr > 110:
        score += 2
        reasons.append("значне відхилення частоти серцевих скорочень")
    elif hr < 55 or hr > 100:
        score += 1
        reasons.append("помірне відхилення частоти серцевих скорочень")

    if spo2 < 92:
        score += 3
        reasons.append("значне зниження SpO₂")
    elif spo2 < 95:
        score += 1
        reasons.append("зниження SpO₂")

    if temp < 35.5 or temp > 38.0:
        score += 3
        reasons.append("значне відхилення температури тіла")
    elif temp < 36.0 or temp > 37.5:
        score += 1
        reasons.append("помірне відхилення температури тіла")

    if sys_bp < 90 or sys_bp > 160 or dia_bp < 60 or dia_bp > 100:
        score += 2
        reasons.append("значне відхилення артеріального тиску")

    if resp < 8 or resp > 24:
        score += 2
        reasons.append("відхилення частоти дихання")

    if score >= 5:
        level = "Критичний"
    elif score >= 2:
        level = "Увага"
    else:
        level = "Норма"

    if not reasons:
        reasons.append("відхилень за правилами симуляції не виявлено")

    return {"risk_score": score, "risk_level": level, "reasons": "; ".join(reasons)}


def analyze_dataframe(frame):
    """Додає до таблиці бали ризику, категорію та пояснення."""
    import pandas as pd

    if frame.empty:
        return frame.copy()

    analyzed = frame.copy()
    results = [
        assess_measurement(row)
        for row in analyzed.to_dict(orient="records")
    ]
    analyzed["risk_score"] = [item["risk_score"] for item in results]
    analyzed["risk_level"] = [item["risk_level"] for item in results]
    analyzed["reasons"] = [item["reasons"] for item in results]
    return analyzed
