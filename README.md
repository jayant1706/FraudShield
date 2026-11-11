# FraudShield: Enterprise AI-Powered Financial Fraud Detection Platform

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Passing-emerald?style=flat-square&logo=githubactions)](https://github.com/jayant1706/FraudShield)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com)
[![PCI--DSS Ready](https://img.shields.io/badge/PCI--DSS-Zero%20PAN%20Storage-success?style=flat-square)](docs/aws_deployment_architecture.md)

**GitHub Repository:** [https://github.com/jayant1706/FraudShield](https://github.com/jayant1706/FraudShield)

### 🚀 Live Cloud Deployments

| Component | Production URL | Hosting | Status |
| :--- | :--- | :--- | :---: |
| **Investigator Dashboard** | [https://fraud-shield-one-khaki.vercel.app](https://fraud-shield-one-khaki.vercel.app) | **Vercel** | [![Vercel](https://img.shields.io/badge/Vercel-Live-success?style=flat-square&logo=vercel)](https://fraud-shield-one-khaki.vercel.app) |
| **FastAPI REST API Gateway** | [https://fraudshield-c5eh.onrender.com](https://fraudshield-c5eh.onrender.com) | **Render** | [![Render](https://img.shields.io/badge/Render-Online-46E3B7?style=flat-square&logo=render)](https://fraudshield-c5eh.onrender.com) |
| **Interactive OpenAPI Docs** | [https://fraudshield-c5eh.onrender.com/docs](https://fraudshield-c5eh.onrender.com/docs) | **Swagger UI** | `Active` |
| **Health Check Probe** | [https://fraudshield-c5eh.onrender.com/health](https://fraudshield-c5eh.onrender.com/health) | **Render** | `200 OK` |

**FraudShield** is an industry-grade, production-ready AI financial transaction fraud detection and risk decision platform. Built for banks, payment gateways, and fintech platforms, FraudShield combines machine learning ensembles (**XGBoost Champion**, **Random Forest**, **Isolation Forest**) with a **deterministic heuristic risk engine**, **sub-25ms TreeSHAP explainability**, an **audit-ready relational database**, and a **10-page enterprise investigator dashboard**.

> [!IMPORTANT]
> **Regulatory & Compliance Notice:** FraudShield is engineered as a **decision-support platform** for fraud risk teams. Prediction scores and risk classifications do not constitute automated banking decisions. Final transaction disposition (clearing, hold, or decline) adheres to financial institution policies and human investigator oversight.

---

## Table of Contents

- [Understanding FraudShield: What Does It Do?](#understanding-fraudshield-what-does-it-do)
  - [The Problem in Financial Fraud](#the-problem-in-financial-fraud)
  - [The FraudShield Solution](#the-fraudshield-solution)
  - [End-to-End Processing Lifecycle](#end-to-end-processing-lifecycle)
- [System Architecture](#system-architecture)
- [Dual-Layer Decision Engine](#dual-layer-decision-engine)
  - [Layer 1: Supervised ML Tournament (XGBoost Champion)](#layer-1-supervised-ml-tournament-xgboost-champion)
  - [Layer 2: Deterministic Heuristic Risk Engine](#layer-2-deterministic-heuristic-risk-engine)
  - [Why ML Probability is Separated from Risk Score](#why-ml-probability-is-separated-from-risk-score)
- [Real-Time Model Explainability (TreeSHAP)](#real-time-model-explainability-treeshap)
- [Machine Learning Pipeline & MLOps](#machine-learning-pipeline--mlops)
  - [Dataset Distribution & Severe Class Imbalance](#dataset-distribution--severe-class-imbalance)
  - [Leak-Free Preprocessing & Scaling](#leak-free-preprocessing--scaling)
  - [Evaluation Metrics & PR-AUC Optimization](#evaluation-metrics--pr-auc-optimization)
  - [Automated Feature Drift Monitoring (Kolmogorov-Smirnov)](#automated-feature-drift-monitoring-kolmogorov-smirnov)
- [Database Schema & Zero-PAN Compliance](#database-schema--zero-pan-compliance)
- [Enterprise Investigator Dashboard (10 Pages)](#enterprise-investigator-dashboard-10-pages)
- [Technology Stack](#technology-stack)
- [API Reference & Live Examples](#api-reference--live-examples)
- [Installation & Quick Start](#installation--quick-start)
  - [Local Setup (Virtualenv)](#1-local-development-setup-virtualenv)
  - [Single-Command Docker Stack](#2-single-command-docker-compose-stack)
  - [Running the 36-Test Suite](#3-running-automated-test-suite)
- [Security & PCI-DSS Compliance](#security--pci-dss-compliance)

---

## Understanding FraudShield: What Does It Do?

### The Problem in Financial Fraud

Global card payment fraud amounts to over **$30 billion annually**. Traditional fraud detection systems suffer from two major flaws:

1. **Rigid Rule-Only Engines:** Static `if-else` rules fail against sophisticated fraudsters. Setting low thresholds blocks legitimate cardholders (costly false declines), while setting high thresholds lets fraudulent bursts slip through.
2. **Opaque "Black-Box" ML Models:** Deep neural nets or uncalibrated models output probabilities without explanation. In regulated banking environments (FCRA, GDPR Article 22, OCC Bulletin), banks **cannot legally block or decline transactions without clear, auditable explanations**.

### The FraudShield Solution

FraudShield bridges statistical machine learning and financial regulatory compliance through a **Dual-Layer Decision Architecture**:

```
Transaction Request ──► [ Feature Engineering ] ──► [ ML Inference: XGBoost ] ──► Probability: 0.942
                                                  │
                                                  ├──► [ TreeSHAP Attribution ] ──► Top Drivers: V14, V12
                                                  │
                                                  └──► [ Heuristic Risk Rules ] ──► Triggers: Amount Spike, Off-Hours
                                                                   │
                                                                   ▼
                                                       Final Decision: HIGH RISK
                                                       Action: FLAG_FOR_REVIEW
                                                       Latency: 16.8 ms
```

### End-to-End Processing Lifecycle

1. **Ingest:** Transaction parameters (amount, timestamp, merchant category, location, device fingerprint, and latent vectors $V_1 - V_{28}$) arrive via authenticated REST API.
2. **Transform:** Raw numerical values are standardized using a leak-free `RobustScaler` (calibrated against median and IQR to resist extreme outlier spikes).
3. **Score:** The champion XGBoost model computes the exact fraud probability ($0.0000$ to $1.0000$).
4. **Attribute (SHAP):** TreeSHAP computes the marginal contribution of each feature to the prediction score in $<25\text{ms}$.
5. **Evaluate Rules:** Deterministic heuristic rules check for high-value spikes, velocity bursts, unusual UTC hours, and high-risk merchant categories.
6. **Assign Tier:** A definitive risk level (`LOW`, `MEDIUM`, `HIGH`) and recommended action (`ALLOW`, `FLAG_FOR_REVIEW`, `BLOCK`) are assigned.
7. **Persist & Stream:** Transaction data and prediction telemetry are indexed into PostgreSQL 16. Prometheus latency counters and drift monitors increment.
8. **Investigate:** The event appears instantly on the React dashboard for fraud analyst triage and audit extraction.

---

## System Architecture

FraudShield implements a clean **Modular Monolith** architecture with strict separation between API gateways, business service layers, ML inference, and asynchronous task execution:

```
                                [ Client / React 18 Dashboard ]
                                              │
                                       (HTTP / REST / JWT)
                                              ▼
                             [ FastAPI Security & Routing Gateway ]
                                       (Port 8000 / ASGI)
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
  [ Auth & RBAC ]                  [ Transaction Service ]               [ Analytics Service ]
(JWT / Bcrypt / Roles)                        │                                    │
                                              ▼                                    │
                                   [ Feature Preprocessor ]                        │
                                   (Leak-Free RobustScaler)                        │
                                              │                                    │
                                              ▼                                    │
                                   [ ML Prediction Engine ]                        │
                                  (XGBoost Champion + SHAP)                        │
                                              │                                    │
                                              ▼                                    │
                                   [ Heuristic Risk Engine ]                       │
                                  (Deterministic Rule Matrix)                      │
                                              │                                    │
                                              ▼                                    │
                                   [ Database Repositories ]                       │
                                 (SQLAlchemy 2.0 / PostgreSQL) ◄───────────────────┘
                                              │
                                              ▼
                                   [ Redis Message Broker ]
                                        (Port 6379)
                                              │
                                              ▼
                                   [ Celery Async Workers ]
                                (Batch Ingestion & Drift Checks)
                                              │
                                              ▼
                                    [ Observability Stack ]
                           (Prometheus :9090 / Grafana :3001)
```

---

## Dual-Layer Decision Engine

### Layer 1: Supervised ML Tournament (XGBoost Champion)

Four distinct model architectures were trained, cross-validated, and benchmarked on 100,000+ credit card transactions:

| Model Architecture | Role | PR-AUC | ROC-AUC | F1-Score | Recall | Precision | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **XGBoost Classifier (`scale_pos_weight`)** | Gradient Boosted Trees | **88.42%** | **98.24%** | **87.80%** | **87.80%** | **87.80%** | **ACTIVE CHAMPION** |
| **Random Forest Ensemble** | Balanced Bagging Trees | 85.20% | 97.10% | 84.10% | 82.50% | 85.80% | CANDIDATE |
| **Logistic Regression** | Calibrated Linear Model | 74.50% | 96.30% | 73.20% | 79.10% | 68.10% | BASELINE |
| **Isolation Forest** | Unsupervised Anomaly | 61.20% | 91.50% | 58.90% | 84.00% | 45.30% | COMPLEMENTARY |

- **Why XGBoost Won:** Gradient-boosted decision trees handle severe class imbalance via the `scale_pos_weight` parameter, naturally handle nonlinear feature interactions (e.g. amount spikes combined with negative $V_{14}$ deviations), and evaluate in sub-millisecond runtime.

### Layer 2: Deterministic Heuristic Risk Engine

Machine learning probabilities alone should not automatically decline customer payments. FraudShield incorporates a deterministic rule engine:

1. **`UNUSUALLY_HIGH_TRANSACTION_AMOUNT`:** Flags single transactions exceeding \$2,500 or $>3\times$ the account average.
2. **`VELOCITY_SPIKE`:** Flags accounts executing $\ge 5$ transactions within a rolling 5-minute window.
3. **`UNUSUAL_HOURS`:** Identifies high-value transfers initiated during off-hours (01:00 - 05:00 UTC) where account takeover fraud historically peaks.
4. **`HIGH_RISK_MERCHANT_CATEGORY`:** Scrutinizes high-risk verticals (cryptocurrency exchanges, peer-to-peer transfers, luxury retail).
5. **`SUSPICIOUS_DEVICE_OR_LOCATION`:** Evaluates device emulator fingerprints and cross-border IP discrepancies.

### Why ML Probability is Separated from Risk Score

- **ML Probability ($0.0 - 1.0$):** A statistical estimation of the likelihood that the transaction matches historical fraud signatures.
- **Risk Level (`LOW`, `MEDIUM`, `HIGH`):** The operational business decision. Even if an ML model outputs a borderline probability ($0.38$), a triggered rule (e.g., velocity spike across 3 countries in 10 minutes) elevates the transaction to **HIGH RISK** for human review.

```
Risk Classification Matrix:
├── LOW RISK    (Score < 0.30, 0 Rules)        ──► ALLOW
├── MEDIUM RISK (Score 0.30 - 0.70, or 1 Rule) ──► FLAG_FOR_REVIEW
└── HIGH RISK   (Score ≥ 0.70, or ≥ 2 Rules)   ──► BLOCK / STEP-UP AUTH
```

---

## Real-Time Model Explainability (TreeSHAP)

For every transaction scored, FraudShield computes **Shapley Additive Explanations (TreeSHAP)** in under **25 milliseconds**. Instead of guessing why a transaction was flagged, investigators see the exact marginal impact of each feature:

```json
"explanations": [
  { "feature": "V12", "impact": "high_risk", "value": -6.20, "shap_value": 6.9853 },
  { "feature": "V14", "impact": "high_risk", "value": -8.50, "shap_value": 5.0747 },
  { "feature": "V10", "impact": "high_risk", "value": -4.10, "shap_value": 4.1887 },
  { "feature": "V17", "impact": "high_risk", "value": -5.00, "shap_value": 3.0115 },
  { "feature": "Amount", "impact": "medium_risk", "value": 4500.0, "shap_value": 0.4812 }
]
```

- **Positive SHAP values** push the score towards fraud (e.g. $V_{14} < -7.0$ represents a high-probability account compromise signature).
- **Negative SHAP values** act as protective factors (e.g. recurring merchant, familiar device fingerprint).

---

## Machine Learning Pipeline & MLOps

### Dataset Distribution & Severe Class Imbalance

- **Benchmark Source:** Kaggle European Credit Card Fraud Detection benchmark (284,807 transactions).
- **Fraud Prevalence:** **~0.172%** (only 17 fraud cases per 10,000 legitimate transactions).
- **Input Features (30 dimensions):**
  - $V_1 - V_{28}$: Confidential PCA components extracted from cardholder behavioral streams.
  - $Time$: Elapsed seconds between transaction and the first transaction in the dataset.
  - $Amount$: Transaction currency gross value.

### Leak-Free Preprocessing & Scaling

To eliminate data leakage:
- Transformations are fitted **strictly on the 70% training split**.
- `RobustScaler` scales $Time$ and $Amount$ using median and Interquartile Range ($\text{IQR} = Q_3 - Q_1$), preventing billion-dollar outlier fraud transactions from corrupting normal variance.

### Evaluation Metrics & PR-AUC Optimization

Standard classification accuracy is misleading in fraud detection: a dummy model predicting 100% legitimate transactions achieves **99.83% accuracy** while missing every single fraud event.

FraudShield optimizes for **PR-AUC (Precision-Recall Area Under Curve)**:
- **Precision:** $\frac{TP}{TP + FP}$ — Minimizes false declines and prevents customer friction.
- **Recall:** $\frac{TP}{TP + FN}$ — Maximizes fraud capture rate and prevents financial losses.
- **Champion PR-AUC:** **88.42%** on unseen holdout test data.

### Automated Feature Drift Monitoring (Kolmogorov-Smirnov)

Live production features naturally drift over time due to economic inflation, changing consumer habits, or new cyberattack vectors. FraudShield runs background **two-sample Kolmogorov-Smirnov (KS) tests**:

$$\text{KS Statistic: } D = \sup_x |F_{\text{live}}(x) - F_{\text{baseline}}(x)|$$

If the $p$-value falls below $0.05$ across critical vectors ($V_{10}, V_{12}, V_{14}$ or $Amount$), a `DATA_DRIFT_DETECTED` warning is generated to schedule candidate model retraining via Celery.

---

## Database Schema & Zero-PAN Compliance

FraudShield enforces strict **Zero Primary Account Number (PAN) / Zero CVV storage**:

```
┌───────────────────────┐         ┌────────────────────────┐
│         users         │         │      transactions      │
├───────────────────────┤         ├────────────────────────┤
│ id (PK, String 36)    │         │ id (PK, String 36)     │
│ full_name             │◄────┐   │ external_transaction_id│ (Indexed)
│ email (UQ, Indexed)   │     │   │ amount (Float)         │
│ password_hash         │     │   │ transaction_time (DT)  │ (Indexed)
│ role (ADMIN/INV/USER) │     │   │ merchant_category      │
│ is_active (Bool)      │     │   │ device_id (String)     │
│ created_at / updated_at│    │   │ location (String)      │
└───────────────────────┘     │   │ user_id (FK)           ├───────┐
                              │   │ status (PENDING/FLAGGED│       │
                              │   │ created_at / updated_at│       │
                              │   └───────────┬────────────┘       │
                              │               │                    │
                              │               │ 1:1 Relationship   │
                              │               ▼                    │
                              │   ┌────────────────────────┐       │
                              │   │      predictions       │       │
                              │   ├────────────────────────┤       │
                              │   │ id (PK, String 36)     │       │
                              │   │ transaction_id (FK, UQ)│       │
                              │   │ fraud_probability      │       │
                              │   │ predicted_class        │       │
                              │   │ risk_level             │       │
                              │   │ recommended_action     │       │
                              │   │ model_version          │       │
                              │   │ inference_latency_ms   │       │
                              │   │ rule_triggers (JSON)   │       │
                              │   │ explanations (JSON)    │       │
                              │   │ created_at (DateTime)  │       │
                              │   └────────────────────────┘       │
                              │                                    │
┌───────────────────────┐     │   ┌────────────────────────┐       │
│     model_versions    │     │   │       audit_logs       │       │
├───────────────────────┤     │   ├────────────────────────┤       │
│ id (PK, String 36)    │     │   │ id (PK, String 36)     │       │
│ version (UQ, Indexed) │     └───┤ user_id (FK, Indexed)  │       │
│ model_name            │         │ action (String)        │       │
│ artifact_path         │         │ resource_type          │       │
│ metrics (JSON)        │         │ resource_id (Indexed)  │       │
│ status (ACTIVE/CAND)  │         │ ip_address (String)    │       │
│ created_at (DateTime) │         │ details (JSON)         │       │
└───────────────────────┘         │ timestamp (DT, Indexed)│       │
                                  └────────────────────────┘       │
                                                                   │
* Zero PAN, CVV, or cardholder magnetic stripe data persisted * ───┘
```

---

## Enterprise Investigator Dashboard (10 Pages)

Built in **React 18**, **TypeScript**, and **Tailwind CSS**, the frontend provides complete situational awareness for fraud analysts:

| Page | Key Operational Features |
| :--- | :--- |
| **1. Executive Dashboard** | Live SLA strip (99.98%), category risk heatmap, real-time flagged queue, diurnal hourly fraud distribution. |
| **2. Fraud Detection Simulator** | 4 synthetic attack presets (*Account Takeover*, *Velocity Burst*, *Tor Exit Cross-Border*, *Card Testing*), real-time latent feature sliders, and 1-click ledger injection. |
| **3. Transactions Ledger** | Searchable audit ledger, quick filter chips (*All*, *Critical High Risk*, *Approved*), real-time KPI overview bar, and native **client-side CSV audit export**. |
| **4. Transaction Detail & Triage** | 28 PCA latent vector table with standard z-scores, device/network fingerprint analysis, historical baseline comparison, and investigator disposition actions. |
| **5. Risk & Loss Analytics** | Diurnal 24-hour UTC fraud clock, temporal volume trends, and **Financial Loss Prevention ROI Calculator** (direct principal saved, chargeback dispute fees avoided). |
| **6. Model Performance & Simulator**| **Interactive Probability Threshold Slider (0.10 - 0.90)** with live confusion matrix updates, PR curve visualization, and top-8 SHAP feature business interpretations. |
| **7. Model Version Registry** | Active vs. Candidate model registry, Champion-Challenger tournament comparison, and 1-click model promotion. |
| **8. User & Team Management** | Team provisioning, RBAC role assignment (`ADMIN`, `INVESTIGATOR`, `USER`), and active status toggling. |
| **9. Risk Engine Settings** | Heuristic threshold tuning (velocity window, high-amount limits, rate limits, TreeSHAP toggles). |
| **10. Global System Status Modal**| Clickable header telemetry modal displaying live operational health across all 7 microservices. |

---

## Technology Stack

```
Backend:           Python 3.13, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0, Alembic
Security:          JWT (PyJWT), Bcrypt password hashing, SlowAPI rate limiting, Request IDs
Machine Learning:  XGBoost 2.1, Scikit-learn 1.9, TreeSHAP 0.54, SciPy, Pandas, NumPy, Joblib
Task Queue:        Redis 7, Celery 5.4
Database:          PostgreSQL 16 (production) / SQLite (development & testing)
Frontend:          React 18.3, TypeScript 5.7, Vite 6, Tailwind CSS, Recharts, Lucide Icons
Observability:     Prometheus Scraper, Grafana Dashboards, Structured JSON Logging
Containerization:  Docker Multi-Stage, Docker Compose, Nginx Reverse Proxy
CI/CD:             GitHub Actions Automated Test Pipeline
```

---

## API Reference & Live Examples

### 1. Authenticate (Obtain Bearer Token)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@fraudshield.io",
    "password": "AdminPassword123!"
  }'
```

### 2. Real-Time Fraud Scoring & Explainability
```bash
curl -X POST "http://localhost:8000/api/v1/predictions/predict" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN_LIVE_1001",
    "amount": 4500.00,
    "merchant_category": "luxury",
    "location": "Lagos, Nigeria",
    "device_id": "DEV_SUSP_991",
    "features": {
      "V14": -8.5,
      "V12": -6.2,
      "V10": -4.1,
      "V17": -5.0
    }
  }'
```

**Live Response (16.8 ms inference latency):**
```json
{
  "prediction_id": "378e1c47-577c-439b-addd-593347186b15",
  "transaction_id": "TXN_LIVE_1001",
  "fraud_probability": 0.9998,
  "prediction": "FRAUD",
  "risk_level": "HIGH",
  "recommended_action": "FLAG_FOR_REVIEW",
  "model_version": "v1.0.0",
  "inference_latency_ms": 16.84,
  "rule_triggers": [
    "UNUSUALLY_HIGH_TRANSACTION_AMOUNT"
  ],
  "explanations": [
    { "feature": "V12", "value": -6.2, "shap_value": 6.9853, "impact": "high_risk" },
    { "feature": "V14", "value": -8.5, "shap_value": 5.0747, "impact": "high_risk" },
    { "feature": "V10", "value": -4.1, "shap_value": 4.1887, "impact": "high_risk" },
    { "feature": "V17", "value": -5.0, "shap_value": 3.0115, "impact": "high_risk" }
  ],
  "created_at": "2026-11-10T13:29:21Z"
}
```

### 3. Update Transaction Investigation Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/transactions/TXN_LIVE_1001/status" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "REJECTED",
    "investigation_notes": "Cardholder confirmed unauthorized attempt. Device emulator flagged."
  }'
```

---

## Installation & Quick Start

### 1. Local Development Setup (Virtualenv)

#### Step 1: Clone Repository
```bash
git clone https://github.com/jayant1706/FraudShield.git
cd FraudShield
```

#### Step 2: Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
# If script execution is restricted on your system, enable it for this process:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate virtual environment:
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt `cmd`):**
```cmd
.\venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### Step 4: Initialize Database & Run Backend Server
```bash
# Seed initial tables and administrator user
python -m backend.app.db.init_db

# Start FastAPI ASGI server on port 8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 5: Start React Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
- **Web App:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Default Admin Login:** `admin@fraudshield.io` / `AdminPassword123!`

---

### 2. Single-Command Docker Compose Stack

To launch all 7 production microservices (FastAPI, React + Nginx, PostgreSQL, Redis, Celery, Prometheus, Grafana) with one command:

```bash
docker compose up --build -d
```

| Container | Internal Port | Host Port | Role |
| :--- | :---: | :---: | :--- |
| `fraudshield-frontend` | 80 | `http://localhost:80` | Nginx reverse proxy + React SPA |
| `fraudshield-backend` | 8000 | `http://localhost:8000` | FastAPI ASGI application & inference engine |
| `fraudshield-postgres` | 5432 | `localhost:5432` | PostgreSQL 16 relational database |
| `fraudshield-redis` | 6379 | `localhost:6379` | In-memory cache & task queue broker |
| `fraudshield-celery-worker`| — | — | Async batch scoring & statistical drift engine |
| `fraudshield-prometheus` | 9090 | `http://localhost:9090` | Telemetry & request latency metrics scraper |
| `fraudshield-grafana` | 3000 | `http://localhost:3001` | SRE performance & fraud analytics dashboards |

---

### 3. Running Automated Test Suite

FraudShield includes 36 comprehensive backend unit and integration tests:

```bash
pytest backend/tests -v
```

```
============================= test session starts =============================
backend/tests/api/test_analytics_and_models_api.py::test_health_probe PASSED [  2%]
backend/tests/api/test_analytics_and_models_api.py::test_ready_probe PASSED  [  5%]
backend/tests/api/test_analytics_and_models_api.py::test_prometheus_metrics_endpoint PASSED [  8%]
backend/tests/api/test_analytics_and_models_api.py::test_analytics_overview PASSED [ 11%]
backend/tests/api/test_analytics_and_models_api.py::test_analytics_fraud_trends PASSED [ 13%]
backend/tests/api/test_analytics_and_models_api.py::test_analytics_risk_distribution PASSED [ 16%]
backend/tests/api/test_analytics_and_models_api.py::test_model_info_endpoint PASSED [ 19%]
backend/tests/api/test_analytics_and_models_api.py::test_model_metrics_endpoint PASSED [ 22%]
backend/tests/api/test_analytics_and_models_api.py::test_list_model_versions PASSED [ 25%]
backend/tests/api/test_analytics_and_models_api.py::test_model_retrain_trigger PASSED [ 27%]
backend/tests/api/test_auth_api.py::test_register_new_user_success PASSED   [ 30%]
backend/tests/api/test_auth_api.py::test_register_duplicate_email_conflict PASSED [ 33%]
backend/tests/api/test_auth_api.py::test_login_success_returns_jwt PASSED    [ 36%]
backend/tests/api/test_auth_api.py::test_login_invalid_password_fails PASSED [ 38%]
backend/tests/api/test_auth_api.py::test_get_current_user_me PASSED         [ 41%]
backend/tests/api/test_auth_api.py::test_get_me_unauthorized_without_token PASSED [ 44%]
backend/tests/api/test_predictions_api.py::test_predict_legitimate_transaction PASSED [ 47%]
backend/tests/api/test_predictions_api.py::test_predict_fraudulent_transaction_signature PASSED [ 50%]
backend/tests/api/test_predictions_api.py::test_predict_invalid_input_negative_amount_fails PASSED [ 52%]
backend/tests/api/test_predictions_api.py::test_batch_prediction_endpoint PASSED [ 55%]
backend/tests/api/test_predictions_api.py::test_get_prediction_by_id PASSED [ 58%]
backend/tests/api/test_transactions_api.py::test_create_and_get_transaction PASSED [ 61%]
backend/tests/api/test_transactions_api.py::test_list_transactions_with_pagination_and_filters PASSED [ 63%]
backend/tests/api/test_transactions_api.py::test_update_transaction_status_and_rbac PASSED [ 66%]
backend/tests/unit/test_ml_pipeline.py::test_data_ingestion_and_validation PASSED [ 69%]
backend/tests/unit/test_ml_pipeline.py::test_data_quality_auditor PASSED    [ 72%]
backend/tests/unit/test_ml_pipeline.py::test_preprocessor_pipeline PASSED    [ 75%]
backend/tests/unit/test_ml_pipeline.py::test_model_evaluator_metrics PASSED [ 77%]
backend/tests/unit/test_ml_pipeline.py::test_model_comparator PASSED        [ 80%]
backend/tests/unit/test_ml_pipeline.py::test_shap_explainer PASSED          [ 83%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_low_risk_transaction PASSED [ 86%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_high_amount_rule PASSED [ 88%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_unusual_timing_rule PASSED [ 91%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_high_risk_merchant_rule PASSED [ 94%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_historical_amount_spike PASSED [ 97%]
backend/tests/unit/test_risk_engine.py::test_risk_engine_high_ml_probability_flags_for_review PASSED [100%]
============================= 36 passed in 32.26s =============================
```

---

## Security & PCI-DSS Compliance

1. **Cardholder Data Neutrality:** Primary Account Numbers (PAN), expiration dates, and CVVs are strictly prohibited from entering FraudShield databases. Transactions reference external tokenized IDs.
2. **Encrypted Identity & Token Security:** Passwords hashed using Bcrypt (cost factor 12). Authorization governed by signed HS256 JWT tokens with 60-minute expirations.
3. **Defense-in-Depth Rate Limiting:** Global rate limiting at 120 requests/minute per IP protects inference endpoints against credential stuffing and distributed denial-of-service (DDoS).
4. **Traceable Audit Logging:** Every disposition update, retraining execution, and schema alteration writes an immutable audit record with user ID, IP address, and microsecond timestamps.

---

## License

FraudShield is distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for details.
