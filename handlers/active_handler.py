from telegram import Update
from telegram.ext import ContextTypes
import database.db_connection as db_connection

async def show_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bookings = db_connection.db.collection("bookings").limit(5).stream()

    active_rides = []
    count = 0
    for booking in bookings:
        data = booking.to_dict()
        count += 1
        ride_info = (
            f"📍 {data.get('destination', 'N/A')}\n"
            f"🗓 {data.get('departure', 'N/A')}\n"
            f"👥 Seats: {data.get('seats', 'N/A')}\n"
            f"🎒 Luggage: {data.get('luggage', 'N/A')}\n"
            f"🚖 Preference: {data.get('preferences', 'N/A')}\n"
            f"👤 @{data.get('username', 'N/A')}" 
        )
        active_rides.append(ride_info)

    if active_rides:
        await update.message.reply_text(
            "🚕 Active Ride Requests:\n\n" + "\n\n".join(active_rides)
        )
    else:
        await update.message.reply_text("No active ride requests found.")