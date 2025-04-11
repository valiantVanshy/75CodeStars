import requests
import random
import pandas as pd
from datetime import datetime, timedelta
import os
import time

API_KEY = "GmdIGSwG6ER0QVA4JRgWtyl4sD5aJbGd"  # ⬅️ Replace with your new key
OUTPUT_FILE = "data/simulated_travel_data.csv"

# 50 locations in Bangalore
locations = [
    {"name": "Whitefield", "latitude": 12.9698, "longitude": 77.7499},
    {"name": "Jayanagar", "latitude": 12.9250, "longitude": 77.5938},
    {"name": "Koramangala", "latitude": 12.9352, "longitude": 77.6245},
    {"name": "Indiranagar", "latitude": 12.9716, "longitude": 77.6412},
    {"name": "Electronic City", "latitude": 12.8452, "longitude": 77.6600},
    {"name": "HSR Layout", "latitude": 12.9121, "longitude": 77.6446},
    {"name": "Hebbal", "latitude": 13.0352, "longitude": 77.5912},
    {"name": "Banashankari", "latitude": 12.9184, "longitude": 77.5736},
    {"name": "Malleshwaram", "latitude": 13.0097, "longitude": 77.5690},
    {"name": "Marathahalli", "latitude": 12.9550, "longitude": 77.7019},
    {"name": "BTM Layout", "latitude": 12.9166, "longitude": 77.6101},
    {"name": "Rajajinagar", "latitude": 12.9911, "longitude": 77.5560},
    {"name": "MG Road", "latitude": 12.9756, "longitude": 77.6050},
    {"name": "Basavanagudi", "latitude": 12.9407, "longitude": 77.5848},
    {"name": "Kengeri", "latitude": 12.9141, "longitude": 77.5145},
    {"name": "Yelahanka", "latitude": 13.1007, "longitude": 77.5963},
    {"name": "Vijayanagar", "latitude": 12.9798, "longitude": 77.5441},
    {"name": "RT Nagar", "latitude": 13.0086, "longitude": 77.5917},
    {"name": "Nagavara", "latitude": 13.0458, "longitude": 77.6245},
    {"name": "Sarjapur", "latitude": 12.8618, "longitude": 77.7900},
    {"name": "Hoodi", "latitude": 12.9918, "longitude": 77.7114},
    {"name": "KR Puram", "latitude": 13.0116, "longitude": 77.6856},
    {"name": "Domlur", "latitude": 12.9581, "longitude": 77.6388},
    {"name": "Ulsoor", "latitude": 12.9784, "longitude": 77.6192},
    {"name": "Bellandur", "latitude": 12.9355, "longitude": 77.6762},
    {"name": "Richmond Town", "latitude": 12.9613, "longitude": 77.6005},
    {"name": "Peenya", "latitude": 13.0272, "longitude": 77.5180},
    {"name": "JP Nagar", "latitude": 12.9010, "longitude": 77.5855},
    {"name": "Bannerghatta Road", "latitude": 12.8732, "longitude": 77.5771},
    {"name": "Hennur", "latitude": 13.0410, "longitude": 77.6520},
    {"name": "Bagalur", "latitude": 13.1400, "longitude": 77.6860},
    {"name": "HSR Sector 2", "latitude": 12.9163, "longitude": 77.6475},
    {"name": "HSR Sector 7", "latitude": 12.9060, "longitude": 77.6460},
    {"name": "Bommanahalli", "latitude": 12.8926, "longitude": 77.6101},
    {"name": "Jeevan Bima Nagar", "latitude": 12.9635, "longitude": 77.6533},
    {"name": "Kumaraswamy Layout", "latitude": 12.9072, "longitude": 77.5659},
    {"name": "Lalbagh", "latitude": 12.9507, "longitude": 77.5848},
    {"name": "Shivajinagar", "latitude": 12.9912, "longitude": 77.6050},
    {"name": "Majestic", "latitude": 12.9763, "longitude": 77.5712},
    {"name": "Girinagar", "latitude": 12.9444, "longitude": 77.5443},
    {"name": "Padmanabhanagar", "latitude": 12.9240, "longitude": 77.5601},
    {"name": "Varthur", "latitude": 12.9351, "longitude": 77.7500},
    {"name": "Sanjay Nagar", "latitude": 13.0338, "longitude": 77.5675},
    {"name": "Malleswaram West", "latitude": 13.0095, "longitude": 77.5601},
    {"name": "Attiguppe", "latitude": 12.9733, "longitude": 77.5333},
    {"name": "Sadashivanagar", "latitude": 13.0084, "longitude": 77.5801},
    {"name": "Banerghatta Circle", "latitude": 12.9100, "longitude": 77.5952},
    {"name": "Frazer Town", "latitude": 12.9983, "longitude": 77.6220},
    {"name": "Kasturinagar", "latitude": 13.0086, "longitude": 77.6614},
    {"name": "Cooke Town", "latitude": 13.0019, "longitude": 77.6198}
]

def get_eta(lat1, lon1, lat2, lon2, depart_time):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{lat1},{lon1}:{lat2},{lon2}/json"
    params = {
        "key": API_KEY,
        "departAt": depart_time.isoformat(),
        "traffic": "true",
        "travelMode": "car"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code} - {response.text}")
    data = response.json()
    return data["routes"][0]["summary"]["travelTimeInSeconds"] / 60  # minutes

# Load existing data
if os.path.exists(OUTPUT_FILE):
    df = pd.read_csv(OUTPUT_FILE)
else:
    df = pd.DataFrame(columns=["home", "office", "home_lat", "home_lon", "office_lat", "office_lon", "day_of_week", "time", "duration_mins"])

api_call_count = 0
MAX_CALLS = 2000

try:
    while api_call_count < MAX_CALLS:
        home, office = random.sample(locations, 2)

        # Random time between 08:00 and 18:59
        random_hour = random.randint(8, 18)
        random_minute = random.randint(0, 59)

        # Random day in last 90 days
        day_offset = random.randint(1, 90)
        random_day = datetime.now() - timedelta(days=day_offset)
        departure = random_day.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

        try:
            duration = get_eta(home["latitude"], home["longitude"], office["latitude"], office["longitude"], departure)
            df = pd.concat([df, pd.DataFrame([{
                "home": home["name"],
                "office": office["name"],
                "home_lat": home["latitude"],
                "home_lon": home["longitude"],
                "office_lat": office["latitude"],
                "office_lon": office["longitude"],
                "day_of_week": departure.strftime("%A"),
                "time": departure.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_mins": duration
            }])], ignore_index=True)
            api_call_count += 1
            print(f"✅ {api_call_count}. {home['name']} ➡ {office['name']} at {departure.strftime('%Y-%m-%d %H:%M')} = {round(duration, 2)} mins")
            time.sleep(0.8)

        except Exception as e:
            print(e)

finally:
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n🟢 Completed {api_call_count} API calls.")
