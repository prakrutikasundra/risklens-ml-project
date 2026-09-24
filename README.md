# RiskLens - Loan Default Intelligence

A local professional Streamlit and Flask application built from copied artifacts of the original ML project. The original `D:\ML PROJECT` directory is never written to.

## Detected model contract

- Target variable: `default` (`0` = No Default, `1` = Default)
- Dataset source column: `Default`
- Algorithm: `LogisticRegression`
- Preprocessing: fitted `LabelEncoder` instances for seven categorical features, followed by the copied `StandardScaler`
- Feature order: `Age`, `Income`, `LoanAmount`, `CreditScore`, `MonthsEmployed`, `NumCreditLines`, `InterestRate`, `LoanTerm`, `DTIRatio`, `HasMortgage`, `HasDependents`, `HasCoSigner`, `Education`, `EmploymentType`, `MaritalStatus`, `LoanPurpose`

## Install

```powershell
cd D:\Project
python -m pip install -r requirements.txt
```

## Run

Start the API in the first terminal:

```powershell
cd D:\Project
python backend\app.py
```

Start the UI in a second terminal:

```powershell
cd D:\Project
streamlit run frontend\streamlit_app.py
```

The Flask API runs at `http://127.0.0.1:5000`; the Streamlit UI runs at `http://localhost:8501`.

## API

`POST /predict` expects JSON with all 16 displayed fields. `GET /health` confirms service readiness and `GET /metadata` exposes feature and categorical metadata for the UI.

## Test request

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/predict -ContentType 'application/json' -Body '{"Age":35,"Income":65000,"LoanAmount":50000,"CreditScore":680,"MonthsEmployed":36,"NumCreditLines":3,"InterestRate":11.5,"LoanTerm":36,"DTIRatio":0.35,"HasMortgage":"No","HasDependents":"No","HasCoSigner":"No","Education":"Bachelor''s","EmploymentType":"Full-time","MaritalStatus":"Single","LoanPurpose":"Other"}'
```

## SOP-compliant implementation

### Problem statement and objective

Predict whether a loan applicant will default (`Default`: 0 = no default, 1 = default) from demographic, financial, and loan attributes. The objective is to provide a transparent probability estimate for decision support, not an automatic lending decision.

### Dataset and features

The supplied `Loan_default.csv` has 255,347 rows and 18 columns. `LoanID` is a unique identifier and is excluded from modelling to prevent memorisation. The 16 features are age, income, loan amount, credit score, employment months, credit lines, interest rate, loan term, debt-to-income ratio, education, employment type, marital status, mortgage, dependents, loan purpose, and co-signer. The dataset has no missing values; the pipeline nevertheless includes median/mode imputation for robust deployment input handling.

### Preprocessing, EDA, and algorithms

Numerical features are median-imputed and standard-scaled. Categorical features are mode-imputed and one-hot encoded. Generated EDA covers target distribution, correlations, and loan amount distribution. `src/scratch_logistic_regression.py` contains a NumPy-only logistic-regression implementation. It is compared with scikit-learn's tuned logistic regression. Cross-validation, tuning results, test metrics, ROC curve, confusion matrix, feature importance, and scratch loss are saved under `reports/`.

The evaluation JSON also records the validation-versus-test ROC-AUC gap as an overfitting check. The tuned model is intentionally class-balanced because the supplied target distribution is imbalanced.

### Reproduce training and run the Flask web app

```powershell
cd D:\Project
python -m pip install -r requirements.txt
python -m src.train
python backend\server.py
```

Open `http://127.0.0.1:5000`. The Flask app serves Home, Prediction, Model Details, and EDA/Visualizations sections. API endpoint: `POST /predict`; health check: `GET /health`.

### Deployment

`render.yaml` provides a free Render Blueprint configuration. Push this directory (including `Loan_default.csv`) to a GitHub repository, create a Render Blueprint from that repository, and let Render run the declared build command. Set `CORS_ORIGIN` only if a separate frontend origin is used; no secrets are required for this project. Copy the resulting Render URL into the deployment placeholder below after your account deploys it.

**Deployed URL:** `YOUR_RENDER_URL_HERE`

### Future scope

Add bias/fairness analysis, prediction logging with consent, monitoring for data drift, and a model-review workflow before any real lending use.
