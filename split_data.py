import pandas as pd
from sklearn.model_selection import StratifiedKFold

data = pd.read_csv("data/healthcare-dataset-stroke-data.csv")

X = data.drop("stroke", axis=1)
y = data["stroke"]

skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

splits = list(skf.split(X, y))

for i, (_, idx) in enumerate(splits):
    data.iloc[idx].to_csv(f"data/hospital_{i+1}.csv", index=False)

print("Stratified split done: each hospital has both classes")
