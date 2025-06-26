# handlers/fallback_handler.py

from telegram import Update
from telegram.ext import ContextTypes

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 I didn’t understand that. To start a new ride request, type /start or /book.\n\n"
        "You can also use /help to see how CabBuddy works 🚕"
    )
