from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋\nI’m CabBuddy IITK 🚖\nLet’s share a ride together to/from IIT Kanpur.\n\nUse /book to start booking!"
    )