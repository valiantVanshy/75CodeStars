import random
import pandas as pd
import streamlit as st
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import math



# Define bounding box for a city (e.g., Bangalore)
lat_min, lat_max = 12.85, 13.10
lon_min, lon_max = 77.50, 77.70

def generate_coordinates():
    lat = random.uniform(lat_min, lat_max)
    lon = random.uniform(lon_min, lon_max)
    return lat, lon

# Generate 150 customers
customers = []
for cid in range(1, 151):
    home_lat, home_lon = generate_coordinates()
    office_lat, office_lon = generate_coordinates()
    customers.append({
        "Customer ID": cid,
        "Home Latitude": home_lat,
        "Home Longitude": home_lon,
        "Workplace Latitude": office_lat,
        "Workplace Longitude": office_lon,
    })

customer_df = pd.DataFrame(customers)
customer_df.to_csv("customers.csv", index=False)
print("✅ customers.csv updated with 150 customers.")

from datetime import datetime, timedelta

# Load updated customer data
customer_df = pd.read_csv("customers.csv")

start_date = datetime(2023, 1, 1)
days = 90
travel_logs = []

for _, row in customer_df.iterrows():
    for i in range(days):
        travel_date = start_date + timedelta(days=i)
        day_of_week = travel_date.strftime("%A")

        # Morning trip
        morning_time = random.choice(["08:00", "08:30", "09:00", "09:30"])
        travel_logs.append({
            "Customer ID": row["Customer ID"],
            "date": travel_date.date(),
            "day_of_week": day_of_week,
            "trip_type": "Home to Office",
            "time_of_day": morning_time,
            "from_lat": row["Home Latitude"],
            "from_lon": row["Home Longitude"],
            "to_lat": row["Workplace Latitude"],
            "to_lon": row["Workplace Longitude"],
        })

        # Evening trip
        evening_time = random.choice(["17:30", "18:00", "18:30", "19:00"])
        travel_logs.append({
            "Customer ID": row["Customer ID"],
            "date": travel_date.date(),
            "day_of_week": day_of_week,
            "trip_type": "Office to Home",
            "time_of_day": evening_time,
            "from_lat": row["Workplace Latitude"],
            "from_lon": row["Workplace Longitude"],
            "to_lat": row["Home Latitude"],
            "to_lon": row["Home Longitude"],
        })

travel_df = pd.DataFrame(travel_logs)
travel_df.to_csv("travel_logs.csv", index=False)
print("✅ travel_logs.csv created with data for 150 customers.")


# Load the travel log
df = pd.read_csv("travel_logs.csv")

# Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # km

# Function to simulate traffic speed based on time
def get_avg_speed(time_str):
    hour = int(time_str.split(":")[0])
    if 8 <= hour < 10 or 17 <= hour < 19:
        return random.uniform(18, 25)  # Peak hour
    elif 7 <= hour < 8 or 10 <= hour < 12 or 15 <= hour < 17:
        return random.uniform(25, 35)  # Medium traffic
    else:
        return random.uniform(35, 50)  # Light traffic

# Apply distance and ETA to the DataFrame
distances = []
etas = []

for _, row in df.iterrows():
    dist = haversine(row["from_lat"], row["from_lon"], row["to_lat"], row["to_lon"])
    road_dist = dist * 1.4  # simulating road network
    avg_speed = get_avg_speed(row["time_of_day"])
    eta = (road_dist / avg_speed) * 60  # in minutes

    distances.append(round(road_dist, 2))
    etas.append(round(eta, 2))

# Add columns
df["distance_km"] = distances
df["estimated_time_min"] = etas

# Save to new CSV
travel_logs_with_eta=df.to_csv("travel_logs_with_eta.csv", index=False)
print("✅ travel_logs_with_eta.csv saved with distance & ETA!")
# Load the processed dataset
df = pd.read_csv("travel_logs_with_eta.csv")
# Extract hour from time_of_day
df["hour"] = df["time_of_day"].apply(lambda x: int(x.split(":")[0]))

# Encode trip_type
df["trip_type_encoded"] = df["trip_type"].apply(lambda x: 1 if x == "Home to Office" else 0)

# One-hot encode day_of_week
df = pd.get_dummies(df, columns=["day_of_week"], drop_first=True)

# Feature columns
features = ["distance_km", "hour", "trip_type_encoded"] + [col for col in df.columns if col.startswith("day_of_week_")]
X = df[features]

# Target
y = df["estimated_time_min"]

# Load the processed dataset
df = pd.read_csv("travel_logs_with_eta.csv")

# Extract hour from time_of_day
df["hour"] = df["time_of_day"].apply(lambda x: int(x.split(":")[0]))

# Encode trip_type as binary
df["trip_type_encoded"] = df["trip_type"].apply(lambda x: 1 if x == "Home to Office" else 0)

# One-hot encode the day_of_week
df = pd.get_dummies(df, columns=["day_of_week"], drop_first=True)

# Define features and target
feature_cols = ["distance_km", "hour", "trip_type_encoded"] + [col for col in df.columns if col.startswith("day_of_week_")]
X = df[feature_cols]
y = df["estimated_time_min"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\n🎯 R² Score: {r2:.4f}")
print(f"⏱️ Mean Absolute Error: {mae:.2f} minutes")


# Save model
joblib.dump(model, "eta_predictor_model.pkl")

# Save feature columns (to keep input order same in Streamlit)
joblib.dump(feature_cols, "feature_columns.pkl")

print("✅ Model & feature list saved!")


# Load model and features
model = joblib.load("eta_predictor_model.pkl")
feature_cols = joblib.load("feature_columns.pkl")

st.title("🛣️ Travel Time Predictor")

st.markdown("Predict estimated time from Home to Office or vice versa using traffic-based logic.")

# User inputs
trip_type = st.selectbox("Trip Type", ["Home to Office", "Office to Home"])
time_input = st.time_input("Time of Day", datetime.strptime("08:30", "%H:%M").time())
day_of_week = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
distance_km = st.slider("Distance (in km)", min_value=1.0, max_value=50.0, value=12.0, step=0.1)

# Prepare input for model
hour = time_input.hour
trip_type_encoded = 1 if trip_type == "Home to Office" else 0

# Create dummy columns for day_of_week
day_dummies = {f"day_of_week_{day}": 0 for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'] if f"day_of_week_{day}" in feature_cols}
if f"day_of_week_{day_of_week}" in day_dummies:
    day_dummies[f"day_of_week_{day_of_week}"] = 1

# Final input row
input_data = pd.DataFrame([{
    "distance_km": distance_km,
    "hour": hour,
    "trip_type_encoded": trip_type_encoded,
    **day_dummies
}])

# Fill missing columns with 0
for col in feature_cols:
    if col not in input_data.columns:
        input_data[col] = 0

# Reorder
input_data = input_data[feature_cols]

# Prediction
if st.button("Predict ETA"):
    eta_min = model.predict(input_data)[0]
    st.success(f"⏱️ Estimated Travel Time: **{eta_min:.2f} minutes**")
