from telegram import Update
from telegram.ext import ContextTypes
from utils.pdf_generator import notify_final_group
import database.db_connection as db

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    await query.answer()  # Acknowledge the button press

    if not data.startswith(("accept_", "wait_")):
        return

    group_id = data.split("_")[1]
    group_ref = db.db.collection("groups").document(group_id)
    group_doc = group_ref.get()

    if not group_doc.exists:
        await query.edit_message_text("❌ This ride group no longer exists.")
        return

    group_data = group_doc.to_dict()
    accepted_users = group_data.get("accepted_users", [])
    members = group_data.get("members", [])

    # Match user using user_id
    user_id = user.id
    already_accepted = any(str(u) == str(user_id) for u in accepted_users)

    if data.startswith("accept_") and not already_accepted:
        accepted_users.append(str(user_id))
        group_ref.update({"accepted_users": accepted_users})
        print(f"[INFO] @{user.username} accepted ride for group {group_id}")

        # ✅ Confirm if all accepted or group size is full
        if len(accepted_users) == len(members) or len(members) >= 4:
            group_ref.update({"status": "confirmed"})
            print(f"[INFO] Group {group_id} confirmed. Sending boarding passes...")
            await notify_final_group(members, context.bot)

        await query.edit_message_reply_markup(reply_markup=None)
        await query.answer("✅ You accepted the ride!")

    elif data.startswith("wait_"):
        await query.edit_message_reply_markup(reply_markup=None)
        await query.answer("⏳ You're waiting for more matches.")
