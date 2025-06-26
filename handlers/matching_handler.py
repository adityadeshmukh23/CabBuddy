from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database.db_connection as db_connection
from datetime import datetime
from .clustering import cluster_bookings
from .greedy_batching import greedy_batching
from utils.pdf_generator import notify_final_group
import uuid
import asyncio
import hashlib

# ✅ Hardcoded distance & duration info
HARDCODED_TRAVEL_INFO = {
    "IITK ➔ Kanpur Airport": {"distance": "27 km", "duration": "56 min"},
    "Kanpur Airport ➔ IITK": {"distance": "27 km", "duration": "56 min"},
    "IITK ➔ Lucknow Airport": {"distance": "97 km", "duration": "2 hr 20 min"},
    "Lucknow Airport ➔ IITK": {"distance": "97 km", "duration": "2 hr 20 min"},
    "IITK ➔ Kanpur Central": {"distance": "16 km", "duration": "34 min"},
    "Kanpur Central ➔ IITK": {"distance": "16 km", "duration": "34 min"},
    "IITK ➔ Bus Stand": {"distance": "15.5 km", "duration": "30 min"},
    "Bus Stand ➔ IITK": {"distance": "15.5 km", "duration": "30 min"},
}

bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

# 🔄 Load bookings from Firestore
def load_clean_bookings():
    all_docs = db_connection.db.collection("bookings").stream()
    bookings = [doc.to_dict() for doc in all_docs]
    return bookings

# 🧠 Generate hash for group based on members and destination
def generate_group_signature(group):
    ids = sorted([str(b['user_id']) for b in group])
    dest = group[0]['destination']
    timestamp = group[0]['departure'][:16]  # yyyy-mm-ddThh:mm
    raw = '_'.join(ids + [dest, timestamp])
    return hashlib.md5(raw.encode()).hexdigest()


# 🎯 Run clustering + batching
def match_rides_with_greedy():
    bookings = load_clean_bookings()
    clustered_groups = cluster_bookings(bookings)
    optimized_groups = []
    for group in clustered_groups:
        batches = greedy_batching(group)
        optimized_groups.extend(batches)
    return optimized_groups

# 🚀 Scheduled matching with deduplication
async def match_and_notify():
    groups = match_rides_with_greedy()
    print(f"[DEBUG] Found {len(groups)} matched groups")
    for group in groups:
        signature = generate_group_signature(group)
        ref = db_connection.db.collection("notified_groups").document(signature)
        if not ref.get().exists:
            print(f"[INFO] Notifying group with signature: {signature}")
            await notify_users(group)
            ref.set({"notified_at": datetime.utcnow().isoformat()})
        else:
            print(f"[SKIPPED] Already notified group: {signature}")

# 📬 Notify users with dynamic invite
# 📬 Notify users with dynamic invite
async def notify_users(group):
    group_id = str(uuid.uuid4())
    destination = group[0]["destination"]
    departure = group[0]["departure"]
    dep_time_str = datetime.fromisoformat(departure).strftime("%d %b %Y, %I:%M %p")

    travel_info = HARDCODED_TRAVEL_INFO.get(destination, {"distance": "N/A", "duration": "N/A"})
    distance_info = f"📏 Distance: {travel_info['distance']}\n⏱ Duration: {travel_info['duration']}\n"

    user_mentions = ', '.join(['@' + b.get('username', 'N/A') for b in group])
    msg = (
        f"🚖 You’ve been matched with {user_mentions} for a ride to {destination} on {dep_time_str}!\n\n"
        f"{distance_info}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Accept", callback_data=f"accept_{group_id}")],
        [InlineKeyboardButton("⏳ Wait", callback_data=f"wait_{group_id}")]
    ])

    for b in group:
        chat_id = b.get('chat_id')
        if chat_id:
            try:
                if bot_instance is None:
                    print(f"[ERROR] bot_instance is None! Cannot send message to {chat_id}")
                    continue

                await bot_instance.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)
                print(f"[INFO] Sent Accept/Wait to {chat_id}")

            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")

    # Save group to Firestore
    db_connection.db.collection("groups").document(group_id).set({
        "members": group,
        "accepted_users": [],
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat()
    })


# 🧪 Admin test command
async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = match_rides_with_greedy()
    if not groups:
        await update.message.reply_text("No optimized rides found yet.")
        return

    for idx, group in enumerate(groups, start=1):
        msg = f"\U0001F696 Optimized Group {idx} \U0001F696\n"
        for b in group:
            dep_time_str = datetime.fromisoformat(b['departure']).strftime("%d %b %Y, %I:%M %p")
            full_destination = b['destination']
            cab_type = b['preferences']

            travel_info = HARDCODED_TRAVEL_INFO.get(full_destination, {"distance": "N/A", "duration": "N/A"})
            msg += (
                f"\n👤 @{b.get('username', 'N/A')}\n"
                f"📍 Destination: {full_destination}\n"
                f"🕰 Departure: {dep_time_str}\n"
                f"🎒 Luggage: {b.get('luggage', 'N/A')}\n"
                f"🚗 Cab Type: {cab_type}\n"
                f"📏 Distance: {travel_info['distance']}\n"
                f"⏱ Duration: {travel_info['duration']}\n"
            )

        await update.message.reply_text(msg)
