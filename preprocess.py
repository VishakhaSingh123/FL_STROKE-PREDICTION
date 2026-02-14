from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess(df):
    df = df.copy()

    # Handle missing values
    df["bmi"].fillna(df["bmi"].mean(), inplace=True)

    # Encode categorical columns
    categorical_cols = [
        "gender",
        "ever_married",
        "work_type",
        "Residence_type",
        "smoking_status"
    ]

    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])

    # Split features and target
    X = df.drop("stroke", axis=1)
    y = df["stroke"]

    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    return X, y
