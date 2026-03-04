# 🧠 Privacy-Preserving Stroke Prediction using Federated Learning with Blockchain Logging

 

---

## 📌 Project Overview

This project implements a privacy-preserving stroke prediction system using **Federated Learning (FL)**.

Multiple hospitals collaboratively train a global machine learning model without sharing raw patient data. Instead of centralizing sensitive medical records, each hospital trains locally and shares only model updates.

To enhance trust and transparency, the system integrates a **blockchain-inspired logging mechanism** that records hospital participation in a tamper-resistant manner.

The project demonstrates a real-world simulation of distributed healthcare machine learning while maintaining strict data privacy.

---

## 🏥 Problem Statement

Modern healthcare AI systems face critical challenges:

- Patient data is highly sensitive and cannot be centralized.
- Stroke datasets are severely imbalanced.
- Distributed training systems require synchronization.
- Trust and transparency are essential in medical collaborations.

This project addresses these challenges using Federated Learning and blockchain-inspired logging.

---

## ⚖️ Core Challenges Addressed

### 1️⃣ Data Privacy Challenge

Healthcare data contains sensitive personal information.

Traditional centralized machine learning requires pooling data from multiple hospitals, which may violate privacy regulations and ethical standards.

**Approach Used:**  
Federated Learning ensures raw data never leaves the hospital. Only model parameters are shared with the central server.

---

### 2️⃣ Dataset Imbalance Problem

The stroke dataset contains significantly more non-stroke cases than stroke cases.

#### Impact:
- High overall accuracy but poor stroke detection
- Increased false negatives
- Reduced recall and F1-score for stroke class
- Misleading performance if only accuracy is considered

#### Strategy Used:
- Class-weight balancing
- Stratified data distribution
- Threshold tuning for minority class detection

---

### 3️⃣ Distributed Client Synchronization

In federated systems, all hospitals must participate in training rounds.

#### Problem:
A hospital may fail to participate if the server begins training before all clients are ready.

#### Impact:
- Incomplete model aggregation
- Reduced global model quality
- Training instability

#### Strategy Used:
Minimum client participation requirement ensures all hospitals contribute before aggregation.

---

### 4️⃣ Audit Transparency & Trust

Medical collaborations require accountability and transparency.

#### Problem:
- How do we verify which hospital participated?
- How do we ensure logs are not tampered with?

#### Solution:
A blockchain-inspired logging system records:
- Training start events
- Evaluation completion
- Participation history

This creates a tamper-resistant audit trail.

---

## 🏗️ System Architecture

The system consists of:

- 🌐 Global Federated Server  
- 🏥 Multiple Hospital Clients  
- 🔗 Blockchain Logging Layer  

### Workflow Summary

1. Server initializes global model  
2. Hospitals receive model parameters  
3. Hospitals train locally on private data  
4. Model updates are sent back to the server  
5. Server aggregates updates using FedAvg  
6. Blockchain logs participation events  

---

## 📊 Evaluation Metrics

Each hospital evaluates the model locally using:

- Confusion Matrix  
- Precision  
- Recall  
- F1 Score  

### Key Insight

In healthcare applications, **accuracy alone is insufficient**.  

Recall and F1-score for stroke detection are more critical because missing a stroke case can have severe consequences.

---

## 📈 Results Interpretation

- The model performs well on non-stroke prediction.
- Stroke detection remains challenging due to dataset imbalance.
- Recall improves when balancing strategies are applied.
- Federated Learning successfully preserves privacy while maintaining collaborative learning.

---

## ✅ Advantages of the Proposed System

- Preserves patient privacy  
- Enables secure multi-hospital collaboration  
- Avoids centralized medical data storage  
- Provides audit transparency through blockchain logging  
- Demonstrates real-world distributed healthcare AI  

---

## ⚠️ Limitations

- Dataset imbalance affects stroke detection performance  
- Blockchain logging introduces computational overhead  
- Synchronization constraints may delay training rounds  

---

## 🚀 Future Improvements

- Apply SMOTE or advanced resampling techniques  
- Implement secure aggregation encryption  
- Integrate smart-contract-based blockchain  
- Deploy real-time streaming hospital data  
- Replace classical ML with deep learning models  

---

## 🎓 Conclusion

This project demonstrates a federated learning-based stroke prediction system enhanced with blockchain-inspired logging.

While stroke prediction performance is limited by dataset imbalance, the system successfully:

- Preserves patient privacy  
- Enables distributed hospital collaboration  
- Ensures transparent participation tracking  

The architecture reflects real-world healthcare AI challenges and provides a strong foundation for secure medical machine learning systems.

---

## 🎯 Project Outcomes

- Implemented a working federated learning pipeline  
- Demonstrated multi-hospital collaboration  
- Addressed healthcare dataset imbalance challenges  
- Integrated transparent blockchain-based logging  

---

## 👩‍💻 Author

**Vishakha Singh**  
B.Tech Computer Science  
Federated Learning & AI Enthusiast  
