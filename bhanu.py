# Install libraries (run this once)

#!pip install openrouteservice folium

# Import libraries
import streamlit as st
import folium
from openrouteservice import Client, convert
from geopy.geocoders import Nominatim

# Initialize API client
API_KEY = '5b3ce3597851110001cf6248099a7b15f070441bab68a3ebe5ab2a3f'
client = Client(key=API_KEY)

# Convert address to coordinates
geolocator = Nominatim(user_agent="rapido_clone")
start_location = geolocator.geocode("MG Road, Bengaluru")
end_location = geolocator.geocode("Electronic City, Bengaluru")

start_coords = (start_location.latitude, start_location.longitude)
end_coords = (end_location.latitude, end_location.longitude)

# Get route
coords = (start_coords[::-1], end_coords[::-1])  # (lon, lat)
route = client.directions(coords)

# Extract distance and duration
distance_km = route['routes'][0]['summary']['distance'] / 1000  # in km
duration_min = route['routes'][0]['summary']['duration'] / 60  # in min

print(f"Distance: {distance_km:.2f} km")
print(f"Estimated Time: {duration_min:.2f} minutes")

# Plot route on map
m = folium.Map(location=start_coords, zoom_start=13)
folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)

route_coords = convert.decode_polyline(route['routes'][0]['geometry'])['coordinates']
folium.PolyLine([(lat, lon) for lon, lat in route_coords], color="blue", weight=5).add_to(m)
import requests

# Correct lat,lon format
start = "52.379189,4.899431"
end = "52.375,4.918"
api_key = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

# Build the API request URL
url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json?key={api_key}"

# Send the request
response = requests.get(url)
data = response.json()

# Print route details
print("Distance (in meters):", data['routes'][0]['summary']['lengthInMeters'])
print("Travel Time (in seconds):", data['routes'][0]['summary']['travelTimeInSeconds'])
import requests
import folium
from geopy.geocoders import Nominatim

# Replace with your TomTom API key
TOMTOM_API_KEY = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

# Convert address to lat/lon using geopy
geolocator = Nominatim(user_agent="tomtom_route_demo")
start_location = geolocator.geocode("MG Road, Bengaluru")
end_location = geolocator.geocode("Electronic City, Bengaluru")

start_coords = (start_location.latitude, start_location.longitude)
end_coords = (end_location.latitude, end_location.longitude)

# Format lat,lon as required by TomTom
start = f"{start_coords[0]},{start_coords[1]}"
end = f"{end_coords[0]},{end_coords[1]}"

# TomTom Routing API request
route_url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json?key={TOMTOM_API_KEY}&routeRepresentation=polyline&computeTravelTimeFor=all"

response = requests.get(route_url)
data = response.json()

# Extract route summary
distance_km = data['routes'][0]['summary']['lengthInMeters'] / 1000
duration_min = data['routes'][0]['summary']['travelTimeInSeconds'] / 60
print(f"Distance: {distance_km:.2f} km")
print(f"Estimated Time: {duration_min:.2f} minutes")

# Extract and decode polyline
encoded_polyline = data['routes'][0]['legs'][0]['points']
route_points = [(point['latitude'], point['longitude']) for point in encoded_polyline]

# Plot on map using folium
m = folium.Map(location=start_coords, zoom_start=12)
folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
folium.PolyLine(route_points, color="blue", weight=5).add_to(m)

# Save map to HTML or display in notebook
m.save("tomtom_route_map.html")
import requests
import folium
from geopy.geocoders import Nominatim

# Replace with your TomTom API key
TOMTOM_API_KEY = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

# Initialize geolocator
geolocator = Nominatim(user_agent="tomtom_route_demo")

# Define start and end locations
start_location = geolocator.geocode("MG Road, Bengaluru")
end_location = geolocator.geocode("Electronic City, Bengaluru")

# Get latitude and longitude
start_coords = (start_location.latitude, start_location.longitude)
end_coords = (end_location.latitude, end_location.longitude)

# Format coordinates for API
start = f"{start_coords[0]},{start_coords[1]}"
end = f"{end_coords[0]},{end_coords[1]}"

# Build TomTom Routing API URL with traffic enabled
route_url = (
    f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    f"?key={TOMTOM_API_KEY}"
    f"&routeRepresentation=polyline"
    f"&traffic=true"
    f"&computeTravelTimeFor=all"
)

# Make the request
response = requests.get(route_url)
data = response.json()

# Extract route summary
summary = data['routes'][0]['summary']
distance_km = summary['lengthInMeters'] / 1000
travel_time_min = summary['travelTimeInSeconds'] / 60
traffic_delay_min = summary.get('trafficDelayInSeconds', 0) / 60
free_flow_time_min = (summary['travelTimeInSeconds'] - summary.get('trafficDelayInSeconds', 0)) / 60

# Print route information
print(f"Distance: {distance_km:.2f} km")
print(f"Estimated Time (with traffic): {travel_time_min:.2f} minutes")
print(f"Traffic Delay: {traffic_delay_min:.2f} minutes")
print(f"Estimated Time (without traffic): {free_flow_time_min:.2f} minutes")

# Extract and decode polyline points
encoded_polyline = data['routes'][0]['legs'][0]['points']
route_points = [(point['latitude'], point['longitude']) for point in encoded_polyline]

# Create Folium map
m = folium.Map(location=start_coords, zoom_start=12)

# Add start and end markers
folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(end_coords, tooltip="End", icon=folium.Icon(color='red')).add_to(m)

# Add route line
folium.PolyLine(route_points, color="blue", weight=5, tooltip="Route").add_to(m)

# Save map to HTML
m.save("tomtom_route_map.html")
print("Map saved to tomtom_route_map.html")
import requests
import folium
from geopy.geocoders import Nominatim
from IPython.display import display

st.title("🛣️ Travel Time Predictor")
st.markdown("Predict estimated time from Home to Office or vice versa using traffic-based logic.")

# Replace with your own TomTom API key
TOMTOM_API_KEY = "fq1a0usQt7qLbvM8Vwu3myhsFfNrEF5A"

# Initialize geolocator
geolocator = Nominatim(user_agent="tomtom_route_demo")

# Define start and end locations
start_location = geolocator.geocode("MG Road, Bengaluru")
end_location = geolocator.geocode("Electronic City, Bengaluru")

# Get coordinates
start_coords = (start_location.latitude, start_location.longitude)
end_coords = (end_location.latitude, end_location.longitude)

# Format coordinates for TomTom API
start = f"{start_coords[0]},{start_coords[1]}"
end = f"{end_coords[0]},{end_coords[1]}"

# Build TomTom Routing API URL
route_url = (
    f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    f"?key={TOMTOM_API_KEY}"
    f"&routeRepresentation=polyline"
    f"&traffic=true"
    f"&computeTravelTimeFor=all"
)

# Make API request
response = requests.get(route_url)
data = response.json()

# Extract route summary
summary = data['routes'][0]['summary']
distance_km = summary['lengthInMeters'] / 1000
travel_time_min = summary['travelTimeInSeconds'] / 60
traffic_delay_min = summary.get('trafficDelayInSeconds', 0) / 60
free_flow_time_min = (summary['travelTimeInSeconds'] - summary.get('trafficDelayInSeconds', 0)) / 60

# Print route info
print(f"📍 Distance: {distance_km:.2f} km")
print(f"🚗 Estimated Time (with traffic): {travel_time_min:.2f} minutes")
print(f"🐢 Traffic Delay: {traffic_delay_min:.2f} minutes")
print(f"🚀 Estimated Time (without traffic): {free_flow_time_min:.2f} minutes")

# Extract route points
encoded_polyline = data['routes'][0]['legs'][0]['points']
route_points = [(point['latitude'], point['longitude']) for point in encoded_polyline]

# Create map centered on start location
m = folium.Map(location=start_coords, zoom_start=12)

# Add start and end markers
folium.Marker(start_coords, tooltip="Start (MG Road)", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(end_coords, tooltip="End (Electronic City)", icon=folium.Icon(color='red')).add_to(m)

# Add route polyline
folium.PolyLine(route_points, color="blue", weight=5, tooltip="Route").add_to(m)

# Save the map as HTML
m.save("tomtom_route_map.html")
print("✅ Map also saved to 'tomtom_route_map.html'")

# Display the map inline in Jupyter Notebook
display(m)