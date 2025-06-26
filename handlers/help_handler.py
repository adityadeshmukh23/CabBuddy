from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP_MESSAGE = r"""
👋 *Welcome to CabBuddy – IITK's Ride\-Sharing Bot\!*

Use this bot to easily find fellow students to share cabs for outstation travel \(e\.g\., Lucknow Airport, Railway Station\)\.

━━━━━━━━━━━━━━━━━━━━

🚖 *Booking a Ride*

Start your journey in either of the two ways:  
• `/start` – Full guided flow  
• `/book` – Quick booking for advanced users

━━━━━━━━━━━━━━━━━━━━

📋 *What You’ll Need to Provide*

• 🏠 Source – usually IITK  
• 🎯 Destination – like Lucknow Airport / Station  
• 🗓️ Departure date & time  
• 🎒 Luggage size – Small \/ Medium \/ Large  
• 🚘 Cab preference – AC \/ Non\-AC \/ Auto Rickshaw

━━━━━━━━━━━━━━━━━━━━

🤝 *Matching Process*

• Matched with 1–3 students with similar timing, route, and preferences  
• You'll be notified when a match is found

━━━━━━━━━━━━━━━━━━━━

✅ *Post\-Match Options*

Choose one of the following:  
• ✅ Accept the match to lock your ride  
• 🔄 Wait for better matches if not satisfied

━━━━━━━━━━━━━━━━━━━━

🎟️ *Buddy Pass*

When all members accept:  
• You’ll receive a beautiful *PDF Buddy Pass*  
• Includes member names, roll numbers, trip time, and destination  
• 🔖 Barcode – currently placeholder; cool features coming soon\!

━━━━━━━━━━━━━━━━━━━━

🧭 *What's Next?*

CabBuddy is just getting started 🚀  
Expect exciting additions like:  
• 📲 Telegram\-native updates  
• 🧠 Smarter group formations  
• 🗺️ Real\-time route tracking  
• 🧾 Match confirmations and more\!

━━━━━━━━━━━━━━━━━━━━

📌 *Available Commands*

\`/start\` – Begin a new ride request  
\`/book\` – Quick\-book your cab  
\`/cancel\` – Cancel your ride request  
\`/help\` – Show this help guide again

━━━━━━━━━━━━━━━━━━━━

ℹ️ Need help later? Just type \`/help\` anytime\.

—

\> build: CabBuddy\.IITK\.2025\.alpha  
\> dev: @adityadeshmukh05 \/\/ system architect
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(HELP_MESSAGE, disable_web_page_preview=True)
