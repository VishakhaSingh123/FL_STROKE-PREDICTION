import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flwr as fl
import pandas as pd
from sklearn.linear_model import LogisticRegression
from preprocess import preprocess

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score
)

class HospitalClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        df = pd.read_csv("data/hospital_3.csv")
        self.X, self.y = preprocess(df)

        # Initial training so coef_ exists
        self.model.fit(self.X, self.y)

    def get_parameters(self, config):
        return [self.model.coef_, self.model.intercept_]

    def fit(self, parameters, config):
        self.model.coef_ = parameters[0]
        self.model.intercept_ = parameters[1]
        self.model.fit(self.X, self.y)
        return [self.model.coef_, self.model.intercept_], len(self.X), {}

    def evaluate(self, parameters, config):
        # Load global model parameters
        self.model.coef_ = parameters[0]
        self.model.intercept_ = parameters[1]

        y_pred = self.model.predict(self.X)

        precision = precision_score(self.y, y_pred, zero_division=0)
        recall = recall_score(self.y, y_pred, zero_division=0)
        f1 = f1_score(self.y, y_pred, zero_division=0)

        print("\n--- Evaluation Results (Hospital 3) ---")
        print("Confusion Matrix:\n", confusion_matrix(self.y, y_pred))
        print("\nClassification Report:\n", classification_report(self.y, y_pred))
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1-score:", f1)

        # Sample predictions
        print("\nSample Predictions (first 10):")
        for i in range(min(10, len(self.y))):
            print(f"Actual: {self.y[i]}, Predicted: {y_pred[i]}")

        return 0.0, len(self.X), {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

fl.client.start_numpy_client(
    server_address="localhost:8080",
    client=HospitalClient()
)
