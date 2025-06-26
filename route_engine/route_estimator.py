import requests
from config import ORS_API_KEY

ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

# Define locations by name
LOCATIONS = {
    "IITK": (26.5123, 80.2329),
    "Kanpur Airport": (26.4042, 80.4105),
    "Lucknow Airport": (26.7611, 80.8893),
    "Kanpur Central": (26.4499, 80.3319),
}

def get_route_info(route_name: str):
    try:
        source_name, dest_name = [x.strip() for x in route_name.split("➔")]
        start = LOCATIONS[source_name]
        end = LOCATIONS[dest_name]
    except (KeyError, ValueError):
        print(f"Invalid route: '{route_name}'. Make sure both points exist in LOCATIONS.")
        return None

    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        "coordinates": [[start[1], start[0]], [end[1], end[0]]]
    }

    try:
        response = requests.post(ORS_URL, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"ORS API Error {response.status_code}: {response.text}")
            return None

        data = response.json()
        segment = data['features'][0]['properties']['segments'][0]

        return {
            "distance_km": round(segment['distance'] / 1000, 2),
            "duration_min": round(segment['duration'] / 60, 2)
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None