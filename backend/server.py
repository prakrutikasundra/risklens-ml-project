"""SOP-compliant Flask web application and JSON prediction API.

The original app.py remains untouched as a legacy Streamlit API.  This module
is the reproducible deployment entry point and uses the training pipeline.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory

from src.config import ARTIFACTS_DIR, CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, REPORTS_DIR, TARGET_COLUMN

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_PATH = ARTIFACTS_DIR / "loan_default_pipeline.joblib"
METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
CATEGORY_OPTIONS = {"Education":["Bachelor's","High School","Master's","PhD"],"EmploymentType":["Full-time","Part-time","Self-employed","Unemployed"],"MaritalStatus":["Divorced","Married","Single"],"HasMortgage":["No","Yes"],"HasDependents":["No","Yes"],"LoanPurpose":["Auto","Business","Education","Home","Other"],"HasCoSigner":["No","Yes"]}
app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"))

def _error(message: str, status: int = 400): return jsonify({"success":False,"error":message}), status
def _metadata() -> dict: return json.loads(METADATA_PATH.read_text(encoding="utf-8")) if METADATA_PATH.exists() else {}
def _model():
    if not PIPELINE_PATH.exists(): raise RuntimeError("Trained model is unavailable. Run `python -m src.train` first.")
    return joblib.load(PIPELINE_PATH)
def _validate(payload: Any) -> pd.DataFrame:
    if not isinstance(payload, dict): raise ValueError("Request body must be a JSON object.")
    missing=[feature for feature in FEATURES if feature not in payload]
    if missing: raise ValueError("Missing required fields: " + ", ".join(missing))
    cleaned={}
    for feature in NUMERIC_FEATURES:
        try: value=float(payload[feature])
        except (TypeError,ValueError) as exc: raise ValueError(f"{feature} must be a valid number.") from exc
        if not np.isfinite(value): raise ValueError(f"{feature} must be finite.")
        cleaned[feature]=value
    for feature in CATEGORICAL_FEATURES:
        value=str(payload[feature]).strip()
        if value not in CATEGORY_OPTIONS[feature]: raise ValueError(f"Invalid {feature}.")
        cleaned[feature]=value
    return pd.DataFrame([cleaned], columns=FEATURES)

@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"]=os.getenv("CORS_ORIGIN","*")
    response.headers["Access-Control-Allow-Headers"]="Content-Type"
    response.headers["Access-Control-Allow-Methods"]="GET, POST, OPTIONS"
    return response
@app.get("/")
def home(): return render_template("index.html")
@app.get("/health")
def health(): return jsonify({"success":True,"status":"ready" if PIPELINE_PATH.exists() else "model_not_trained","target_variable":TARGET_COLUMN})
@app.get("/metadata")
def metadata():
    saved=_metadata(); return jsonify({"success":True,"target_variable":TARGET_COLUMN,"features":FEATURES,"categorical_options":CATEGORY_OPTIONS,"model_name":saved.get("model_name","Run training to create model"),"best_parameters":saved.get("best_parameters",{}),"best_cv_roc_auc":saved.get("best_cv_roc_auc")})
@app.post("/predict")
def predict():
    try:
        probability=float(_model().predict_proba(_validate(request.get_json(silent=True)))[0,1]); prediction=int(probability >= .5)
    except ValueError as exc: return _error(str(exc))
    except RuntimeError as exc: return _error(str(exc),503)
    except Exception:
        app.logger.exception("Prediction failed"); return _error("The model could not process this request.",500)
    return jsonify({"success":True,"target_variable":TARGET_COLUMN,"prediction":prediction,"label":"Default" if prediction else "No Default","default_probability":round(probability,6)})
@app.route("/predict", methods=["OPTIONS"])
def options(): return ("",204)
@app.get("/reports/figures/<path:filename>")
def figures(filename: str): return send_from_directory(REPORTS_DIR / "figures",filename)
if __name__ == "__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=os.getenv("FLASK_DEBUG")=="1")
