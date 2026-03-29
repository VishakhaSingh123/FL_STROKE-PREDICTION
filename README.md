# 🧠 Privacy-Preserving Stroke Prediction using Federated Learning

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![ML](https://img.shields.io/badge/ML-Federated%20Learning-green)
![Privacy](https://img.shields.io/badge/Privacy-Blockchain%20Logging-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

> A privacy-preserving stroke prediction system where multiple hospitals collaboratively train a global ML model — without ever sharing raw patient data.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Core Challenges & Solutions](#-core-challenges--solutions)
- [Evaluation Metrics](#-evaluation-metrics)
- [Results](#-results)
- [Advantages & Limitations](#-advantages--limitations)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## 📌 Overview

This project simulates a real-world **Federated Learning (FL)** system for stroke prediction across 3 hospitals. Instead of centralizing sensitive patient records, each hospital trains a local model and shares only model weights with a central server.

A **blockchain-inspired logging layer** records participation events in a tamper-resistant audit trail, ensuring transparency and accountability in the collaborative training process.

---

## 🏥 Problem Statement

Modern healthcare AI faces critical challenges:

- Patient data is highly sensitive and cannot be centralized
- Stroke datasets are severely imbalanced (far more non-stroke cases)
- Distributed systems need synchronization across all participants
- Medical collaborations require transparency and accountability

This project addresses all four using Federated Learning + blockchain logging.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────┐
│              FEDERATED SERVER               │
│  • Initializes global model                 │
│  • Aggregates updates via FedAvg            │
│  • Broadcasts updated weights               │
└────────────────┬────────────────────────────┘
                 │  model weights (up/down)
     ┌───────────┼───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Hospital1│ │Hospital2│ │Hospital3│
│  Local  │ │  Local  │ │  Local  │
│Training │ │Training │ │Training │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┴───────────┘
                 │
     ┌───────────▼───────────┐
     │   Blockchain Logger   │
     │  Tamper-resistant     │
     │  participation audit  │
     └───────────────────────┘
```

**Training Workflow:**
1. Server initializes the global model
2. All hospitals receive current model parameters
3. Each hospital trains locally on its private data
4. Model updates (weights only) are sent back to the server
5. Server aggregates using **FedAvg**
6. Blockchain logs each participation event
7. Repeat for N rounds

---

## 📁 Project Structure

```
FL_STROKE-PREDICTION/
│
├── data/                   # Raw stroke dataset (not shared between hospitals)
│
├── preprocess.py           # Data cleaning and feature engineering
├── split_data.py           # Splits dataset across 3 hospitals (stratified)
│
├── server/                 # Federated server logic
│   └── ...                 # Model initialization, FedAvg aggregation
│
├── hospital1/              # Hospital 1 client
│   └── ...                 # Local training, evaluation, weight sharing
├── hospital2/              # Hospital 2 client
│   └── ...
├── hospital3/              # Hospital 3 client
│   └── ...
│
├── __pycache__/
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/VishakhaSingh123/FL_STROKE-PREDICTION.git
cd FL_STROKE-PREDICTION

# 2. Install dependencies
pip install -r requirements.txt
```

> **Dataset:** This project uses the [Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset) from Kaggle. Download `healthcare-dataset-stroke-data.csv` and place it inside the `data/` folder.

---

## 🚀 How to Run

### Step 1 — Preprocess the Data

```bash
python preprocess.py
```

### Step 2 — Split Data Across Hospitals

```bash
python split_data.py
```

This distributes the preprocessed data into `hospital1/`, `hospital2/`, and `hospital3/` using stratified sampling to maintain stroke/non-stroke ratio.

### Step 3 — Start the Federated Server

```bash
python server/server.py
```

### Step 4 — Launch Hospital Clients

Open 3 separate terminals and run:

```bash
# Terminal 1
python hospital1/client.py

# Terminal 2
python hospital2/client.py

# Terminal 3
python hospital3/client.py
```

> The server waits for all 3 hospitals to connect before beginning federated training rounds.

---

## ⚖️ Core Challenges & Solutions

### 1. Data Privacy
Raw patient data never leaves the hospital. Only model parameters travel over the network — satisfying privacy regulations and ethical standards.

### 2. Dataset Imbalance
The stroke dataset is highly skewed (non-stroke >> stroke cases).

| Strategy | Purpose |
|---|---|
| Class-weight balancing | Penalizes incorrect stroke predictions more |
| Stratified splitting | Ensures each hospital sees proportional stroke cases |
| Threshold tuning | Improves recall for the minority (stroke) class |

### 3. Client Synchronization
A minimum client participation requirement ensures the server only begins aggregation once **all 3 hospitals are ready**, preventing partial or unstable updates.

### 4. Audit Transparency
A blockchain-inspired logging layer records:
- Training round start/end events
- Which hospitals participated
- Evaluation completion timestamps

This creates a **tamper-resistant** audit trail for medical accountability.

---

## 📊 Evaluation Metrics

Each hospital evaluates the global model locally after each round using:

| Metric | Why It Matters |
|---|---|
| **Recall** | Most critical — missing a stroke is dangerous |
| **F1 Score** | Balances precision and recall for imbalanced data |
| Precision | Avoids excessive false alarms |
| Confusion Matrix | Full breakdown of prediction outcomes |

> ⚠️ **Accuracy alone is misleading** in stroke prediction. A model predicting "no stroke" for all patients would achieve ~95% accuracy but 0% recall.

---

## 📈 Results

| Class | Performance |
|---|---|
| Non-Stroke | High precision and recall |
| Stroke | Successfully detected after addressing class imbalance challenges |

The dataset imbalance challenge was resolved through class-weight balancing, stratified data distribution, and threshold tuning — enabling the model to accurately predict both stroke and non-stroke cases.

Federated Learning successfully maintains collaborative learning quality comparable to centralized training — without any hospital sharing raw data.

---

## ✅ Advantages & ⚠️ Limitations

**Advantages:**
- Patient privacy is fully preserved
- Enables secure multi-hospital AI collaboration
- No centralized storage of sensitive records
- Transparent participation via blockchain logging

**Limitations:**
- Dataset imbalance limits stroke detection performance
- Blockchain logging adds some computational overhead
- Synchronization requirement may delay training if a hospital is slow

---

## 🚀 Future Improvements

- [ ] Apply **SMOTE** or advanced oversampling for better stroke recall
- [ ] Add **secure aggregation** (encrypted weight sharing)
- [ ] Replace blockchain-inspired logs with a real **smart contract**
- [ ] Integrate **deep learning** models (LSTM, MLP)
- [ ] Support **asynchronous** federated rounds
- [ ] Deploy on real hospital streaming data

---

## 👩‍💻 Author

**Vishakha Singh**
B.Tech Computer Science | Federated Learning & AI Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-VishakhaSingh123-black?logo=github)](https://github.com/VishakhaSingh123)

---

*Built as a demonstration of privacy-preserving healthcare AI using Federated Learning.*
