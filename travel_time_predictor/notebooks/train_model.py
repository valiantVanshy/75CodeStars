import os
import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

# 📥 Load dataset
data_path = "data/simulated_travel_data.csv"
df = pd.read_csv(data_path)

print("🧾 Columns in dataset:", list(df.columns))

# 🧼 Clean and prepare data
df = df.rename(columns={
    "start_lon": "start_lng",
    "end_lon": "end_lng",
    "hour": "hour_of_day"
})

# ✅ Convert day_of_week to integer if not already
if df["day_of_week"].dtype == object:
    day_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    df["day_of_week"] = df["day_of_week"].map(day_map)

# 🚫 Remove rows with missing or invalid target values
df = df[pd.notnull(df["duration_mins"])]
df = df[np.isfinite(df["duration_mins"])]
df = df[df["duration_mins"] < 1e5]

# 🧾 Print column types
print("📊 Column types after cleaning:\n", df.dtypes)
print("✅ Final row count after cleaning:", len(df))

# 🎯 Features and target
X = df[["start_lat", "start_lng", "end_lat", "end_lng", "day_of_week", "hour_of_day"]]
y = df["duration_mins"]

# 🧪 Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🤖 Train model
model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# 🧮 Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"✅ Training complete. MAE = {round(mae, 2)} minutes")

# 💾 Save the model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/xgb_model.joblib")
print("💾 Model saved to models/xgb_model.joblib")
