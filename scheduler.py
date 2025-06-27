from datetime import datetime, timedelta
import pytz
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.matching_handler import match_and_notify

# Global scheduler and loop
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
bot_instance = None  # Injected in post_init
loop = None  # Event loop will be set in post_init


# 🔁 Match scheduler every 1 min
def start_scheduler():
    print("[SCHEDULER] Starting scheduler...")
    scheduler.add_job(match_and_notify, 'interval', minutes=1)
    print("[SCHEDULER] Match job scheduled every 1 min.")
    scheduler.start()


# ⏰ Trip Reminder Scheduler
def schedule_reminder(user_id, chat_id, destination, departure_time_str):
    try:
        tz = pytz.timezone("Asia/Kolkata")
        
        # Ensure departure time is timezone-aware
        departure_time = datetime.fromisoformat(departure_time_str)
        if departure_time.tzinfo is None:
            departure_time = tz.localize(departure_time)

        reminder_time = departure_time - timedelta(hours=1)
        now = datetime.now(tz)

        print(f"[REMINDER DEBUG] Scheduling reminder for user {user_id} at {reminder_time} for destination: {destination}")

        if reminder_time <= now:
            print(f"[REMINDER SKIPPED] Reminder time {reminder_time} is in the past. Current time: {now}")
            return

        job_id = f"reminder_{user_id}_{departure_time.strftime('%Y%m%d%H%M')}"

        scheduler.add_job(
            send_reminder,
            trigger='date',
            run_date=reminder_time,
            args=[chat_id, destination, departure_time.strftime('%I:%M %p')],
            id=job_id,
            replace_existing=True,
        )

        print(f"[REMINDER SCHEDULED] ✅ Job ID: {job_id} set for {reminder_time}")

    except Exception as e:
        print(f"[SCHEDULER ERROR] Failed to schedule reminder: {e}")
        import traceback
        traceback.print_exc()


# 📤 Async reminder sender (called inside event loop)
async def send_reminder_async(chat_id, destination, departure_time_str):
    print(f"[REMINDER SEND] Sending reminder to chat_id {chat_id} for destination {destination} at {departure_time_str}")
    await bot_instance.send_message(
        chat_id=chat_id,
        text=(
            f"⏰ *Trip Reminder*\n\n"
            f"Your cab to *{destination}* is scheduled for *{departure_time_str}*.\n"
            f"Please be ready 10–15 minutes in advance. Have a safe journey! 🚕✨"
        ),
        parse_mode="Markdown"
    )


# 🔁 Wrapper for APScheduler (runs from thread, submits to loop)
def send_reminder(chat_id, destination, departure_time_str):
    print(f"[REMINDER WRAPPER] Triggered for chat_id {chat_id}")
    try:
        asyncio.run_coroutine_threadsafe(
            send_reminder_async(chat_id, destination, departure_time_str),
            loop
        )
    except Exception as e:
        print(f"[REMINDER ERROR] Failed to run async reminder: {e}")
        import traceback
        traceback.print_exc()
