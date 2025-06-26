import database.db_connection as db_connection
from collections import defaultdict
from datetime import datetime
import dateparser
from sklearn.cluster import DBSCAN
import numpy as np

# Unified booking loader
def load_clean_bookings():
    all_docs = db_connection.db.collection("bookings").stream()
    bookings = []

    for doc in all_docs:
        booking = doc.to_dict()

        # parse departure time
        departure_raw = booking.get("departure")
        parsed_date = dateparser.parse(departure_raw)

        if not parsed_date:
            print(f"Skipping invalid date: {departure_raw}")
            continue

        booking['departure_dt'] = parsed_date
        bookings.append(booking)

    return bookings

# --- Interval Matching ---

def interval_matching(bookings, interval_minutes=60):
    bookings.sort(key=lambda b: b['departure_dt'])
    groups = []

    while bookings:
        group = []
        current = bookings.pop(0)
        group.append(current)

        to_remove = []
        for other in bookings:
            diff = abs((other['departure_dt'] - current['departure_dt']).total_seconds() / 60)
            if diff <= interval_minutes:
                group.append(other)
                to_remove.append(other)

        for r in to_remove:
            bookings.remove(r)

        groups.append(group)

    return groups

# --- DBSCAN Matching ---

def dbscan_matching(bookings, eps_minutes=60, min_samples=2):
    if not bookings:
        return []

    X = np.array([b['departure_dt'].timestamp() for b in bookings]).reshape(-1, 1)
    clustering = DBSCAN(eps=eps_minutes*60, min_samples=min_samples).fit(X)

    groups = defaultdict(list)
    for label, booking in zip(clustering.labels_, bookings):
        if label != -1:
            groups[label].append(booking)

    return list(groups.values())

# --- Final match_rides interface ---

def match_rides():
    bookings = load_clean_bookings()

    if len(bookings) <= 10:
        print("Using Interval Matching")
        return interval_matching(bookings)
    else:
        print("Using DBSCAN Matching")
        return dbscan_matching(bookings)