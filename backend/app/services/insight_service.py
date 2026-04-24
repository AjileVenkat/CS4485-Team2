"""Generates user-facing insights for dashboard display."""

from __future__ import annotations

from statistics import mean
from typing import Dict, List


def generate_insights(feature_values: Dict[str, float], probabilities: Dict[str, float], prediction: str, risk_score: float) -> List[Dict[str, str]]:
    """Create concise, deterministic insights based on model outputs and key features."""
    insights = []

    sorted_classes = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    if not sorted_classes:
        return insights

    top_label, top_prob = sorted_classes[0]
    confidence_level = "High" if top_prob >= 0.75 else "Moderate" if top_prob >= 0.55 else "Low"

    insights.append(
        {
            "feature": "Top Class Confidence",
            "detail": f"{top_label} is currently the top class at {top_prob * 100:.1f}% confidence.",
            "level": confidence_level,
        }
    )

    if len(sorted_classes) > 1:
        second_label, second_prob = sorted_classes[1]
        margin = (top_prob - second_prob) * 100.0
        separation_level = "High" if margin >= 20 else "Moderate" if margin >= 10 else "Low"
        insights.append(
            {
                "feature": "Class Separation",
                "detail": f"{top_label} leads {second_label} by {margin:.1f} percentage points.",
                "level": separation_level,
            }
        )

    risk_level = "High" if risk_score >= 70 else "Moderate" if risk_score >= 45 else "Low"
    insights.append(
        {
            "feature": "Risk Score",
            "detail": f"Risk score is {risk_score:.1f} out of 100 for this run.",
            "level": risk_level,
        }
    )

    theta_values = _collect_band_values(feature_values, "Theta_")
    alpha_values = _collect_band_values(feature_values, "Alpha_")
    if theta_values and alpha_values:
        theta_alpha_ratio = mean(theta_values) / max(mean(alpha_values), 1e-8)
        ratio_level = "High" if theta_alpha_ratio >= 1.2 else "Moderate" if theta_alpha_ratio >= 0.9 else "Info"
        insights.append(
            {
                "feature": "Theta/Alpha Balance",
                "detail": f"Average theta-to-alpha ratio is {theta_alpha_ratio:.2f} across selected channels.",
                "level": ratio_level,
            }
        )

    connectivity = {
        key: value for key, value in feature_values.items() if key.startswith("PHI_") and _is_finite_number(value)
    }
    if connectivity:
        top_pair = max(connectivity.items(), key=lambda item: abs(float(item[1])))
        insights.append(
            {
                "feature": "Top Connectivity Pair",
                "detail": f"{top_pair[0]} has the strongest mutual-information signal ({float(top_pair[1]):.3f}).",
                "level": "Info",
            }
        )

    if prediction != top_label:
        insights.append(
            {
                "feature": "Prediction Alignment",
                "detail": f"Predicted class was adjusted to {top_label} based on normalized probability output.",
                "level": "Info",
            }
        )

    return insights[:8]


def _collect_band_values(feature_values: Dict[str, float], prefix: str) -> List[float]:
    values = []
    for key, value in feature_values.items():
        if key.startswith(prefix) and _is_finite_number(value):
            values.append(float(value))
    return values


def _is_finite_number(value: object) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False

    return numeric == numeric and numeric not in (float("inf"), float("-inf"))
