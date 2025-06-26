from telegram import Update
import random
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import asyncio
from config import BOT_TOKEN
import database.db_connection as db

# ✅ Handlers
from handlers.start_handler import start
from handlers.help_handler import help_command
from handlers.fallback_handler import unknown_message
from handlers.booking_handler import (
    start_booking, destination, departure, luggage, prefs, cancel,
    DESTINATION, DEPARTURE, LUGGAGE, PREFS
)
from handlers import matching_handler
from handlers.confirmation_handler import handle_callback

# ✅ Scheduler and PDF
from scheduler import start_scheduler
from utils import pdf_generator
from scheduler import scheduler  # For setting bot_instance in reminder

# ✅ Admin IDs
ADMIN_IDS = [6335424968, 6486765901]

# 🔐 Admin check
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# 🔐 Admin-only: /match
async def match_admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return
    await matching_handler.show_matches(update, context)

# 📊 Admin-only: /stats
async def stats_admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    bookings = db.db.collection("bookings").stream()
    groups = db.db.collection("groups").stream()
    notified = db.db.collection("notified_groups").stream()

    await update.message.reply_text(
        f"📊 *CabBuddy Stats*\n\n"
        f"• Bookings: {sum(1 for _ in bookings)}\n"
        f"• Groups: {sum(1 for _ in groups)}\n"
        f"• Notified Groups: {sum(1 for _ in notified)}",
        parse_mode="Markdown"
    )

# ⚠️ Admin-only: /reset
async def reset_admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    await update.message.reply_text("⚠️ Resetting all system data...")

    for collection in ["bookings", "groups", "notified_groups"]:
        docs = db.db.collection(collection).stream()
        for doc in docs:
            doc.reference.delete()

    await update.message.reply_text("✅ All bookings, groups, and notifications have been cleared.")

# 🔁 Inject bot instance globally
async def post_init(app):
    import scheduler
    import handlers.matching_handler as matching_handler

    # Inject bot instance
    scheduler.bot_instance = app.bot
    scheduler.loop = asyncio.get_running_loop()  # ✅ Store main loop

    # ✅ Use function to set bot in matching_handler
    matching_handler.set_bot_instance(app.bot)

    # Start scheduler after injection
    start_scheduler()
    print("[INFO] Bot instance injected and scheduler started.")


# 🚀 Build bot
app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

# ⬇️ Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("match", match_admin_only))
app.add_handler(CommandHandler("stats", stats_admin_only))
app.add_handler(CommandHandler("reset", reset_admin_only))
app.add_handler(CallbackQueryHandler(handle_callback))

# 📝 /book flow
app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("book", start_booking)],
    states={
        DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
        DEPARTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, departure)],
        LUGGAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, luggage)],
        PREFS: [MessageHandler(filters.TEXT & ~filters.COMMAND, prefs)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
))

# ❓ Catch-all message handler (fallback)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

# 🟢 Launch bot
if __name__ == "__main__":
    try:
        print("[INFO] Bot starting...")
        app.run_polling()
    except Exception as e:
        print(f"[ERROR] Bot failed to start: {e}")
