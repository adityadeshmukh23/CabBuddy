from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import database.db_connection as db_connection
from datetime import datetime, timedelta
import dateparser
import pytz
from scheduler import schedule_reminder

# Define conversation states
DESTINATION, DEPARTURE, LUGGAGE, PREFS = range(4)

# 🔰 Allowed destination options
DESTINATIONS = [
    "IITK ➔ Kanpur Airport", "Kanpur Airport ➔ IITK",
    "IITK ➔ Lucknow Airport", "Lucknow Airport ➔ IITK",
    "IITK ➔ Kanpur Central", "Kanpur Central ➔ IITK",
    "IITK ➔ Bus Stand", "Bus Stand ➔ IITK"
]

# 🚫 Basic abuse word filter (example list)
ABUSE_WORDS = {"fuck", "shit", "bitch", "asshole", "chutiya", "madarchod", "mc", "bc", "lund"}

# 🚖 Start booking flow
async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.utcnow()
    last = context.user_data.get("last_booking")

    if last and now - last < timedelta(minutes=2):
        await update.message.reply_text("⏳ Please wait 2 minutes before trying again.")
        return ConversationHandler.END

    context.user_data["last_booking"] = now

    reply_keyboard = [[d] for d in DESTINATIONS]
    await update.message.reply_text(
        "🚖 Where are you traveling to?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DESTINATION

# 📍 Capture destination
async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    if any(bad_word in user_input for bad_word in ABUSE_WORDS):
        await update.message.reply_text("🚫 Yo chill! We’re here to vibe, not roast the server 😄")
        return DESTINATION

    if update.message.text.strip() not in DESTINATIONS:
        await update.message.reply_text("⚠️ Please select a valid destination from the keyboard.")
        return DESTINATION

    context.user_data['destination'] = update.message.text.strip()
    await update.message.reply_text("🕰 Enter departure time (e.g. 15th July 3pm):", reply_markup=ReplyKeyboardRemove())
    return DEPARTURE

# 🕰 Capture and validate departure time
async def departure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    if any(bad_word in user_input for bad_word in ABUSE_WORDS):
        await update.message.reply_text("🚫 Please avoid using inappropriate language.")
        return DEPARTURE

    departure_dt = dateparser.parse(update.message.text.strip(), settings={'PREFER_DATES_FROM': 'future'})

    if not departure_dt or departure_dt < datetime.now() + timedelta(minutes=5):
        await update.message.reply_text("⚠️ Please enter a valid time at least 5 minutes in the future (e.g. 15th July 3pm):")
        return DEPARTURE

    context.user_data['departure'] = departure_dt.isoformat()
    await update.message.reply_text("🎒 Luggage size per person? (Small/Medium/Large):")
    return LUGGAGE

# 🎒 Capture luggage size
async def luggage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    if any(bad_word in user_input for bad_word in ABUSE_WORDS):
        await update.message.reply_text("🚫 Please avoid using inappropriate language.")
        return LUGGAGE

    context.user_data['luggage'] = update.message.text.strip()

    reply_keyboard = [
        ["A/C Cab 🚘"],
        ["Non A/C Cab 🚖"],
        ["Auto Rickshaw 🛺"]
    ]

    await update.message.reply_text(
        "🚗 Select your cab type preference:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PREFS

# ✅ Save booking in Firestore
async def prefs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cab_choice = update.message.text.strip()
    if any(bad_word in cab_choice.lower() for bad_word in ABUSE_WORDS):
        await update.message.reply_text("🚫 Please avoid using inappropriate language.")
        return PREFS

    allowed_cabs = {"A/C Cab 🚘", "Non A/C Cab 🚖", "Auto Rickshaw 🛺"}

    if cab_choice not in allowed_cabs:
        await update.message.reply_text("⚠️ Please select a cab type from the given options.")
        return PREFS

    context.user_data['preferences'] = cab_choice
    user = update.effective_user

    departure_time_str = context.user_data['departure']

    booking_data = {
        "user_id": user.id,
        "username": user.username or user.first_name,
        "chat_id": user.id,
        "destination": context.user_data['destination'],
        "departure": departure_time_str,
        "luggage": context.user_data['luggage'],
        "preferences": context.user_data['preferences'],
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "last_notified_signature": ""
    }

    db_connection.db.collection("bookings").add(booking_data)

    # ⏰ Schedule reminder for 1 hour before departure
    try:
        schedule_reminder(user.id, user.id, context.user_data['destination'], departure_time_str)
        print(f"[REMINDER DEBUG] Scheduled for user {user.id} to {context.user_data['destination']} at {departure_time_str}")
    except Exception as e:
        print(f"[ERROR] Reminder schedule failed: {e}")

    await update.message.reply_text(
        "✅ Your cab request has been saved!\nThank you.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ❌ Cancel flow
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Booking cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
