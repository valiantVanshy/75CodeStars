import pandas as pd
import joblib
import streamlit as st
from datetime import datetime
import math
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# Load the processed dataset
df = pd.read_csv("simulated_travel_logs.csv")

# Extract hour from time_of_day
df["hour"] = df["time_of_day"].apply(lambda x: int(x.split(":")[0]))

# Encode trip_type as binary
df["trip_type_encoded"] = df["trip_type"].apply(lambda x: 1 if x == "Home to Office" else 0)

# One-hot encode the day_of_week
df = pd.get_dummies(df, columns=["day_of_week"], drop_first=True)

# Define features and target
feature_cols = ["distance_km", "hour", "trip_type_encoded"] + [col for col in df.columns if col.startswith("day_of_week_")]
X = df[feature_cols]
y = df["ETA_min"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
r2 = r2_score(y_test, y_pred)
r2_p = r2 * 100
mae = mean_absolute_error(y_test, y_pred)

print(f"\n🎯 R² Score: {r2_p:.2f}")
print(f"⏱️ Mean Absolute Error: {mae:.2f} minutes")

# Save model
joblib.dump(model, "eta_predictor_model.pkl")
joblib.dump(feature_cols, "feature_columns.pkl")
print("✅ Model & feature list saved!")

# --- Load Trained Model ---
model = joblib.load("eta_predictor_model.pkl")
feature_cols = joblib.load("feature_columns.pkl")

# --- Page Title ---
st.set_page_config(page_title="ETA Predictor", page_icon="🛣️")
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>🛣️ Commute Time Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7F8C8D;'>Estimate commute duration based on coordinates, time, and weekday</p>", unsafe_allow_html=True)

st.sidebar.title("👥 Team Members")
st.sidebar.markdown("""
- **Chirantana K M** 🎓
- **Vanshika Sharma** 🧠  
- **Venkata Bhanuteja Yadalla** 💻  
- **Jonathan Samuel Jason** 📊  
""")
st.sidebar.markdown("---")
st.sidebar.info("ETA Prediction App - April 2025")

# --- Input Section ---
st.markdown("---")
st.subheader("📍 Enter Coordinates")

col1, col2 = st.columns(2)
with col1:
    from_lat = st.number_input("From Latitude", value=12.9716, format="%.6f")
    from_lon = st.number_input("From Longitude", value=77.5946, format="%.6f")
with col2:
    to_lat = st.number_input("To Latitude", value=12.9352, format="%.6f")
    to_lon = st.number_input("To Longitude", value=77.6146, format="%.6f")

# --- Display Map ---
st.markdown("### 🗺️ Map View of Route")
st.map(pd.DataFrame({
    'lat': [from_lat, to_lat],
    'lon': [from_lon, to_lon]
}))

# --- Time & Day Section ---
now = datetime.now()
hour = now.hour
day_of_week = now.strftime("%A")
st.markdown(f"""
<div style="background-color:#D6EAF8; padding: 10px; border-radius: 10px;">
    <strong>🕒 Current Time:</strong> {now.strftime('%H:%M')} &nbsp; | &nbsp; <strong>📅 Day:</strong> {day_of_week}
</div>
""", unsafe_allow_html=True)

# --- Distance Calculation ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

raw_distance = haversine(from_lat, from_lon, to_lat, to_lon)
distance_km = round(raw_distance * 1.4, 2)

# --- Build Input Data ---
input_data = {
    "distance_km": distance_km,
    "hour": hour,
    "trip_type_encoded": 1  # Default: Home to Office
}

# Add day_of_week dummies (assuming drop_first was used during training)
day_dummies = {f"day_of_week_{day}": 0 for day in ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
if f"day_of_week_{day_of_week}" in day_dummies:
    day_dummies[f"day_of_week_{day_of_week}"] = 1

input_data.update(day_dummies)

# Fill in missing features
for col in feature_cols:
    if col not in input_data:
        input_data[col] = 0

input_df = pd.DataFrame([input_data])[feature_cols]

# --- Predict Button ---
st.markdown("---")
if st.button("🚀 Predict ETA"):
    try:
        eta = model.predict(input_df)[0]
        st.success(f"⏱️ **Estimated Travel Time: {eta:.2f} minutes**")
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
