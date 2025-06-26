BOT_TOKEN = "7998140010:AAHUjtVHL1Rc-USWsBQz_o-ajcMF5dy9zo0"

FIRESTORE_CREDENTIALS = "path-to-service-account-key.json"

# For route API (we'll use OpenRouteService free plan now)
ORS_API_KEY = "5b3ce3597851110001cf624864e883a9255042499649a8bac6eedf0c"

# Default cab rates (IITK approx values — feel free to modify)
CAB_RATES = {
    "A/C Cab 🚘": {"base": 60, "per_km": 18},
    "Non A/C Cab 🚖": {"base": 50, "per_km": 15},
    "Auto Rickshaw 🛺": {"base": 30, "per_km": 12}
}

DEFAULT_BUFFER_MINUTES = 60