<img width="1366" height="768" alt="Screenshot (534)" src="https://github.com/user-attachments/assets/66b256be-faed-45f5-8bdd-c52f0ebf30cf" /># 🧠 Privacy-Preserving Stroke Prediction using Federated Learning & Blockchain Logging

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flower](https://img.shields.io/badge/Flower-flwr-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A privacy-preserving machine learning system where 3 simulated hospitals collaboratively train a stroke prediction model using **Federated Learning (Flower/flwr)** — without sharing raw patient data — enhanced with a **blockchain-inspired audit logging layer** for transparency and trust.

---

## 📌 Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technical Challenges & Solutions](#technical-challenges--solutions)
- [Results](#results)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Blockchain Audit Log](#blockchain-audit-log)
- [Limitations & Future Work](#limitations--future-work)
- [Conclusion](#conclusion)

---

## 🌐 Overview

Modern healthcare AI faces a fundamental conflict — building accurate models requires large datasets, but patient data is too sensitive to centralise.

This project resolves that conflict using **Federated Learning (FL)**:
- Each hospital trains a local model on its own private data
- Only model parameters (not raw data) are shared with a central server
- The server aggregates updates using the **FedAvg algorithm** via **Flower (flwr)**
- A **blockchain-inspired logging layer** records every participation event in a tamper-resistant hash chain

---

## 🏥 Problem Statement

| Challenge | Impact |
|---|---|
| Patient data cannot be centralised | Traditional ML is impossible across hospitals |
| Stroke datasets are severely imbalanced (95:5 ratio) | Model predicts "no stroke" for everything — 0% recall |
| Distributed clients need synchronisation | Incomplete rounds degrade model quality |
| Medical collaborations need audit trails | No way to verify hospital participation |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GLOBAL FL SERVER                     │
│          (FedAvg Aggregation via Flower/flwr)           │
│              + Blockchain Audit Logger                  │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
    ┌──────────▼──────────┐   ┌───────────▼─────────┐   ┌──────────────────────┐
    │     Hospital 1      │   │     Hospital 2      │   │     Hospital 3       │
    │   (Local Data)      │   │   (Local Data)      │   │   (Local Data)       │
    │  Local Training     │   │  Local Training     │   │  Local Training      │
    └──────────┬──────────┘   └───────────┬─────────┘   └──────────┬───────────┘
               │                          │                          │
               └──────────────────────────┴──────────────────────────┘
                                          │
                             ┌────────────▼────────────┐
                             │   BLOCKCHAIN LOGGER     │
                             │   Hash-Chain Ledger     │
                             │   audit_log.json        │
                             └─────────────────────────┘
```

**Workflow:**
1. Server initialises global model and logs `SERVER_START` to blockchain
2. Each hospital receives model parameters from server
3. Hospitals train locally — **raw data never leaves the hospital**
4. Local model updates sent back to server
5. Server aggregates using FedAvg and logs `ROUND_FIT_COMPLETE`
6. Server evaluates and logs `ROUND_EVALUATE_COMPLETE` with per-client metrics
7. Repeats for 3 rounds
8. Final chain verified and saved to `audit_log.json`

---

## ✨ Key Features

- **🔒 Privacy by Design** — raw patient data never transmitted or centralised
- **🏥 3 Hospital Simulation** — 3 clients training in parallel via Flower (flwr)
- **⚖️ Class Imbalance Handling** — class-weight balancing + threshold tuning
- **🔗 Blockchain Audit Log** — tamper-resistant hash chain logging every round
- **📊 Per-Client Evaluation** — precision, recall, F1-score logged per hospital
- **✅ Chain Verification** — integrity check after all rounds complete

---

## ⚙️ Technical Challenges & Solutions

### 1. Data Privacy
**Problem:** Centralising sensitive medical records violates privacy regulations

**Solution:** Federated Learning via Flower — only model gradients shared, never patient records

---

### 2. Dataset Imbalance (Most Critical)
**Problem:** Stroke cases represent only ~5% of the dataset

**Without fix:**
- 95% accuracy but **0% stroke recall**
- Model predicts "no stroke" for every patient
- Completely useless in a healthcare context

**Solution:**
- `class_weight='balanced'` in LogisticRegression
- Decision threshold lowered to 0.25 to favour recall

**Result after fix:** Stroke recall jumped from **0% → 93–98%** across all 3 hospitals

---

### 3. Client Synchronisation
**Problem:** Server must wait for all hospitals before aggregating

**Solution:** `min_fit_clients=3` and `min_available_clients=3` enforces all 3 hospitals contribute before any aggregation

---

### 4. Audit Transparency
**Problem:** Medical collaborations need verifiable participation records

**Solution:** Blockchain-inspired hash chain where each block contains:
- Event type and timestamp
- Per-client metrics
- SHA-256 hash of current block
- Hash of previous block (tamper-evident linkage)

---

## 📊 Results

### Per-Hospital Classification Report (After Class Balancing)

| Hospital | Accuracy | Stroke Precision | Stroke Recall | Stroke F1 |
|---|---|---|---|---|
| Hospital 1 | 54% | 0.09 | **0.93** | 0.17 |
| Hospital 2 | 56% | 0.10 | **0.95** | 0.17 |
| Hospital 3 | 55% | 0.10 | **0.98** | 0.17 |

### Before vs After Class Balancing

| Metric | Before Fix | After Fix |
|---|---|---|
| Stroke Recall | ~0% | **93–98%** |
| Sample Predictions | All wrong (Predicted: 0) | All correct (Predicted: 1) |
| Model Usefulness | ❌ None | ✅ High recall for healthcare |


### Federated Training Summary

| Metric | Value |
|---|---|
| Number of Rounds | 3 |
| Clients per Round | 3 |
| Total Training Time | ~33 seconds |
| Failures | 0 |

> **Key Insight:** In healthcare, **recall is the most critical metric** — missing a stroke is far more dangerous than a false alarm. The model achieves 93–98% stroke recall, correctly flagging the vast majority of actual stroke cases.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Federated Learning | Flower (flwr) |
| Aggregation | FedAvg (built into Flower) |
| ML Model | Scikit-learn — Logistic Regression |
| Data Processing | Pandas, NumPy |
| Blockchain Logging | Custom Python hash-chain (SHA-256) |
| Dataset | [Stroke Prediction Dataset — Kaggle](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset) |

---

## 📸 Screenshots

### 🔗 Blockchain Audit Log
![Blockchain Log](<img width="1366" height="768" alt="Screenshot (534)" src="https://github.com/user-attachments/assets/8f7d566b-445a-4691-ad05-f50a3661108e" />
)


### 📊 Classification Report (Hospital 1)
![Classification Report](<img width="1366" height="768" alt="Screenshot (535)" src="https://github.com/user-attachments/assets/b406012a-7bfa-41e9-9735-2816ecdb3e61" />
)

### 📄 Audit Log JSON
![Audit Log JSON](<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/43f818d3-2680-40a7-b073-8cd223cf6258" />
)


## 📁 Project Structure

```
FL_STROKE-PREDICTION/
│
├── blockchain.py          # Blockchain hash-chain logger
├── preprocess.py          # Data preprocessing pipeline
├── split_data.py          # Stratified data splitting across hospitals
├── audit_log.json         # Generated blockchain audit log
│
├── server/
│   └── server.py          # FL server — FedAvg + blockchain logging
│
├── hospital1/
│   └── client.py          # Hospital 1 — local training + evaluation
├── hospital2/
│   └── client.py          # Hospital 2 — local training + evaluation
├── hospital3/
│   └── client.py          # Hospital 3 — local training + evaluation
│
├── data/
│   ├── hospital_1.csv     # Stratified patient data — Hospital 1
│   ├── hospital_2.csv     # Stratified patient data — Hospital 2
│   └── hospital_3.csv     # Stratified patient data — Hospital 3
│
└── requirements.txt
```

---

## 🚀 How to Run

### Prerequisites
```bash
Python 3.8+
Anaconda (recommended)
```

### Setup
```bash
# Clone the repository
git clone https://github.com/VishakhaSingh123/FL_STROKE-PREDICTION
cd FL_STROKE-PREDICTION

# Create and activate environment
conda create -n fl_stroke python=3.8
conda activate fl_stroke

# Install dependencies
pip install -r requirements.txt
```

### Run (4 terminals needed)

**Terminal 1 — Start Server first:**
```bash
conda activate fl_stroke
python server/server.py
```
Wait for `Flower server running` before starting clients.

**Terminal 2 — Hospital 1:**
```bash
conda activate fl_stroke
python hospital1/client.py
```

**Terminal 3 — Hospital 2:**
```bash
conda activate fl_stroke
python hospital2/client.py
```

**Terminal 4 — Hospital 3:**
```bash
conda activate fl_stroke
python hospital3/client.py
```

Training completes in ~33 seconds. Results and blockchain audit log printed to server terminal and saved to `audit_log.json`.

---

## 🔗 Blockchain Audit Log

After training, `audit_log.json` is generated in the root folder. Each block contains:

```json
{
  "index": 1,
  "timestamp": "2026-03-04 12:30:00",
  "event": "ROUND_FIT_COMPLETE",
  "data": {
    "round": 1,
    "num_clients": 3,
    "num_failures": 0
  },
  "previous_hash": "a3f9b2c1d4e5f6a7...",
  "hash": "b4c8d2e1f3a59d76..."
}
```

The hash chain links every block to the previous one — any tampering with past records invalidates all subsequent hashes, making the log tamper-resistant.

---

## ⚠️ Limitations & Future Work

### Current Limitations
- High recall comes with low precision — acceptable in healthcare but worth noting
- Simulation runs on a single machine, not true distributed deployment
- Blockchain is hash-chain based, not a full distributed ledger

### Planned Improvements
- [ ] Apply SMOTE for advanced resampling to improve precision
- [ ] Implement secure aggregation with differential privacy
- [ ] Integrate smart-contract-based blockchain (Ethereum/Hyperledger)
- [ ] Deploy across actual distributed nodes using FastAPI
- [ ] Replace Logistic Regression with deep learning models

---

## 🎓 Conclusion

This project successfully implements a **working federated learning pipeline** using Flower (flwr) across 3 simulated hospital clients — achieving privacy-preserving collaborative stroke prediction without centralising any patient data.

Key outcomes:
- ✅ Raw patient data never leaves individual hospital clients
- ✅ Stroke detection recall improved from **0% → 93–98%** via class balancing
- ✅ 3 federated training rounds completed in ~33 seconds with 0 failures
- ✅ Blockchain audit log provides tamper-resistant participation tracking

The project reflects real challenges in healthcare AI — data privacy, class imbalance, distributed synchronisation, and audit transparency — making it a strong foundation for production-grade federated medical ML systems.

---

## 👩‍💻 Author

**Vishakha Singh**
B.Tech Computer Science, Manipal University Jaipur (2027)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/vishakha-singh-03309b24a)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/VishakhaSingh123)

---

*If you found this project useful, please consider giving it a ⭐*

