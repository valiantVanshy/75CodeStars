import pandas as pd
import numpy as np
from joblib import load
from sklearn.preprocessing import StandardScaler
import os

# ✅ Load trained model
model_path = "model/travel_time_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError("Model not found. Please run train_model.py first.")
model = load(model_path)

# ✅ Sample new data for prediction
new_data = pd.DataFrame([{
    'Distance_KM': 12.3,
    'Time_Of_Day': '08:45',
    'Day_Of_Week': 'Tuesday',
    'Trip_Type': 'Home_to_Office',
    'Start_Lat': 12.9716,
    'Start_Lon': 77.5946,
    'End_Lat': 12.9352,
    'End_Lon': 77.6145,
}])

# ✅ Convert time to minutes
def convert_time_to_minutes(time_str):
    hour, minute = map(int, time_str.split(":"))
    return hour * 60 + minute

new_data['Time_Minutes'] = new_data['Time_Of_Day'].apply(convert_time_to_minutes)

# ✅ Encode Day and Trip Type
new_data['Day_Index'] = pd.Categorical(new_data['Day_Of_Week'],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True).codes

new_data['Trip_Type_Code'] = new_data['Trip_Type'].map({'Home_to_Office': 0, 'Office_to_Home': 1})

# ✅ Add dummy speed to categorize (simulate live traffic approximation)
# We assume average urban speed based on time and day logic
approx_speed = 30  # can be dynamic later
new_data['Speed_KMPH'] = approx_speed
new_data['Speed_Category'] = pd.cut(new_data['Speed_KMPH'], bins=[0, 20, 40, 60, 120], labels=[0, 1, 2, 3])

# ✅ Features expected by model
features = [
    'Distance_KM', 'Time_Minutes', 'Day_Index',
    'Trip_Type_Code', 'Start_Lat', 'Start_Lon',
    'End_Lat', 'End_Lon', 'Speed_Category'
]

X_new = new_data[features].copy()
X_new['Speed_Category'] = X_new['Speed_Category'].astype(int)  # required for model

# ✅ StandardScaler should be re-fit (simple scaling here — match train pipeline)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_new)

# ✅ Predict travel time
predicted_time = model.predict(X_scaled)[0]
print(f"🕒 Predicted Travel Time: {predicted_time:.2f} minutes")
