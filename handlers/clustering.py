# matching/clustering.py

from sklearn.cluster import DBSCAN
from datetime import datetime
from dateparser import parse as parse_date
import numpy as np

# Destination encoding (mapping for 2D clustering)
DESTINATION_MAPPING = {
    'IITK ➔ Kanpur Airport': 1,
    'Kanpur Airport ➔ IITK': 2,
    'IITK ➔ Lucknow Airport': 3,
    'Lucknow Airport ➔ IITK': 4,
    'IITK ➔ Kanpur Central': 5,
    'Kanpur Central ➔ IITK': 6,
    'IITK ➔ Bus Stand': 7,
    'Bus Stand ➔ IITK': 8
}

def cluster_bookings(bookings):
    data_points = []
    clean_bookings = []

    for booking in bookings:
        dest_num = DESTINATION_MAPPING.get(booking['destination'], 0)
        parsed_time = parse_date(booking['departure'])
        
        if not parsed_time:
            print(f"Skipping invalid date: {booking['departure']}")
            continue

        dep_timestamp = parsed_time.timestamp()

        # Normalize both dimensions
        scaled_dest = dest_num * 10          # destination weight
        scaled_time = dep_timestamp / 86400  # time scaled to days

        data_points.append([scaled_dest, scaled_time])

        booking['departure_dt'] = parsed_time
        clean_bookings.append(booking)

    if not data_points:
        return []

    X = np.array(data_points)

    # DBSCAN: eps tweaked for 2D distance
    dbscan = DBSCAN(eps=0.05, min_samples=2)
    labels = dbscan.fit_predict(X)

    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:
            continue
        clusters.setdefault(label, []).append(clean_bookings[idx])

    return list(clusters.values())