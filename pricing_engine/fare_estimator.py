# pricing_engine/fare_estimator.py

# Static dummy rates (modify as you collect real vendor data)
FARE_RATES = {
    "A/C Cab 🚘": {"base": 80, "per_km": 18},
    "Non A/C Cab 🚖": {"base": 60, "per_km": 15},
    "Auto Rickshaw 🛺": {"base": 40, "per_km": 12}
}

TRAFFIC_BUFFER = 1.10
SURGE_MULTIPLIER = 1.20

def estimate_fare(distance_km, cab_type, surge=False, traffic=False):
    rates = FARE_RATES.get(cab_type, FARE_RATES["A/C Cab 🚘"])
    
    base = rates['base']
    per_km = rates['per_km']
    
    fare = base + (distance_km * per_km)

    if surge:
        fare *= SURGE_MULTIPLIER

    if traffic:
        fare *= TRAFFIC_BUFFER

    return round(fare, 2)