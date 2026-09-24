"""Flask API for loan-default inference using the copied original artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_VARIABLE = "default"
DATASET_TARGET_COLUMN = "Default"
FEATURE_ORDER = [
    "Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed",
    "NumCreditLines", "InterestRate", "LoanTerm", "DTIRatio", "HasMortgage",
    "HasDependents", "HasCoSigner", "Education", "EmploymentType",
    "MaritalStatus", "LoanPurpose",
]
CATEGORICAL_FEATURES = [
    "HasMortgage", "HasDependents", "HasCoSigner", "Education",
    "EmploymentType", "MaritalStatus", "LoanPurpose",
]
NUMERIC_FEATURES = [feature for feature in FEATURE_ORDER if feature not in CATEGORICAL_FEATURES]

app = Flask(__name__)


def load_artifacts() -> tuple[Any, Any, dict[str, Any]]:
    """Load the exact artifacts copied from the original ML project."""
    try:
        model = joblib.load(PROJECT_ROOT / "model.pkl")
        scaler = joblib.load(PROJECT_ROOT / "scaler.pkl")
        encoders = joblib.load(PROJECT_ROOT / "encoders.pkl")
    except Exception as exc:  # pragma: no cover - startup failures are environmental
        raise RuntimeError("Unable to load the copied ML artifacts.") from exc
    return model, scaler, encoders


MODEL, SCALER, ENCODERS = load_artifacts()


def _error(message: str, status: int = 400, details: dict[str, str] | None = None):
    body: dict[str, Any] = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


def validate_and_prepare(payload: Any) -> pd.DataFrame:
    """Validate raw user data, encode categoricals, and preserve training order."""
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    missing = [feature for feature in FEATURE_ORDER if feature not in payload]
    if missing:
        raise ValueError(f"Missing required features: {', '.join(missing)}")

    row: dict[str, Any] = {}
    for feature in NUMERIC_FEATURES:
        try:
            value = float(payload[feature])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{feature} must be a valid number.") from exc
        if not np.isfinite(value):
            raise ValueError(f"{feature} must be finite.")
        row[feature] = value

    for feature in CATEGORICAL_FEATURES:
        value = str(payload[feature]).strip()
        if not value:
            raise ValueError(f"{feature} cannot be empty.")
        allowed = set(ENCODERS[feature].classes_)
        if value not in allowed:
            raise ValueError(f"Invalid {feature}. Allowed values: {', '.join(ENCODERS[feature].classes_)}")
        row[feature] = ENCODERS[feature].transform([value])[0]

    return pd.DataFrame([row], columns=FEATURE_ORDER)


@app.get("/health")
def health():
    return jsonify({"success": True, "status": "ready", "target_variable": TARGET_VARIABLE})


@app.get("/metadata")
def metadata():
    return jsonify({
        "success": True,
        "target_variable": TARGET_VARIABLE,
        "dataset_target_column": DATASET_TARGET_COLUMN,
        "model_name": type(MODEL).__name__,
        "features": FEATURE_ORDER,
        "categorical_options": {name: list(ENCODERS[name].classes_) for name in CATEGORICAL_FEATURES},
    })


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    try:
        frame = validate_and_prepare(payload)
        scaled = SCALER.transform(frame)
        prediction = int(MODEL.predict(scaled)[0])
        probabilities = MODEL.predict_proba(scaled)[0]
        default_index = list(MODEL.classes_).index(1)
        default_probability = float(probabilities[default_index])
    except ValueError as exc:
        return _error(str(exc))
    except Exception:
        app.logger.exception("Prediction failed")
        return _error("The model could not process this request.", 500)

    return jsonify({
        "success": True,
        "target_variable": TARGET_VARIABLE,
        "prediction": prediction,
        "label": "Default" if prediction == 1 else "No Default",
        "default_probability": round(default_probability, 6),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
