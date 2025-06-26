# pricing_engine/fare_engine.py
import requests
import os
from dotenv import load_dotenv

# Load ORS key from .env
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

# ORS API endpoint
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

def get_distance_duration(source_coords, dest_coords):
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        "coordinates": [source_coords, dest_coords]
    }

    try:
        response = requests.post(ORS_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        summary = data['routes'][0]['summary']
        distance_km = summary['distance'] / 1000
        duration_min = summary['duration'] / 60

        return round(distance_km, 2), round(duration_min, 2)

    except Exception as e:
        print("ORS API Error:", e)
        return None, None

def calculate_fare(source_coords, dest_coords, preferences):
    distance, duration = get_distance_duration(source_coords, dest_coords)

    if distance is None or duration is None:
        return None, 0, 0

    base_rate = 15 if preferences.lower() == "sedan" else 20
    fare = distance * base_rate

    return round(fare), distance, duration

# Optional testing
if __name__ == "__main__":
    source = [80.233, 26.510]  # IITK
    dest = [80.364, 26.439]    # Kanpur Central

    fare, distance, duration = calculate_fare(source, dest, "Sedan")
    print(f"Fare: ₹{fare} for {distance:.2f} km, Time: {duration:.2f} min")