from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from datetime import datetime
import os
import random
import string

# Helvetica and its variants are built-in to ReportLab.
FONT_BASE_NAME = 'Helvetica'
FONT_BASE_BOLD_NAME = 'Helvetica-Bold'
FONT_BASE_OBLIQUE_NAME = 'Helvetica-Oblique'

# Path to emoji image assets
EMOJI_IMAGE_PATHS = {
    "car": "assests/emojis/emoji_u1f697.png",
    "wave": "assests/emojis/emoji_u1f44b.png",
    "user": "assests/emojis/emoji_u1f464.png",
    "location": "assests/emojis/emoji_u1f4cd.png",
    "calendar": "assests/emojis/emoji_u1f5d3.png",
    "taxi": "assests/emojis/emoji_u1f695.png",
    "buddies": "assests/emojis/emoji_u1f465.png",
    "footer_car": "assests/emojis/emoji_u1f696.png"
}

# Hardcoded travel info (used for reference if needed)
HARDCODED_TRAVEL_INFO = {
    "Kanpur Airport": {"distance": "27 km", "duration": "56 min"},
    "Lucknow Airport": {"distance": "97 km", "duration": "1 hr 50 min"},
    "Kanpur Central": {"distance": "16 km", "duration": "30 min"},
    "Jhakarkati Bus Stand": {"distance": "15.5 km", "duration": "30 min"}
}

bot_instance = None

def generate_pass_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def draw_emoji(c, name, x, y, size=16):
    path = EMOJI_IMAGE_PATHS.get(name)
    if path and os.path.exists(path):
        c.drawImage(path, x, y, width=size, height=size, mask='auto')

def generate_premium_buddy_pass(user_data, pass_id):
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"BuddyPass_Premium_{user_data['username']}_{date_str}.pdf"

    output_dir = "generated_passes"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A6)
    width, height = A6

    # --- Background & Header ---
    c.setFillColorRGB(0.09, 0.28, 0.35)
    c.rect(0, 0, width, height, fill=1)

    c.setFillColor(colors.white)
    c.setFont(FONT_BASE_BOLD_NAME, 20)
    greeting = f"Hi {user_data['username'].capitalize()}"
    c.drawString(20, height - 40, greeting)

    c.setFont(FONT_BASE_NAME, 11)
    c.drawString(20, height - 65, "Here's your upcoming ride")

    # --- Main Info Box ---
    box_x = 10
    box_width = width - 20
    box_height = 200
    box_y = height - 85 - box_height

    c.setFillColorRGB(0.97, 0.95, 0.93)
    c.roundRect(box_x, box_y, box_width, box_height, 8, fill=1)

    c.setFillColor(colors.black)
    detail_y = box_y + box_height - 25
    line_height = 25

    # Helper for each line
    def draw_detail(label, value):
        nonlocal detail_y
        c.setFont(FONT_BASE_BOLD_NAME, 10)
        c.drawString(box_x + 20, detail_y, f"{label}")
        c.setFont(FONT_BASE_NAME, 10)
        c.drawString(box_x + 95, detail_y, value)
        detail_y -= line_height

    draw_detail("Username:", f"@{user_data['username']}")
    draw_detail("Route:", user_data.get('destination', 'Unknown'))
    draw_detail("Departure:", user_data['departure_str'])
    draw_detail("Cab Type:", f"{user_data['preferences']}")
    buddies = ', '.join([f"@{b}" for b in user_data.get('ride_buddies', [])]) or 'None'
    draw_detail("Ride Buddies:", buddies)

    # --- Barcode ---
    barcode = code128.Code128(pass_id, barHeight=12 * mm, barWidth=0.8)
    barcode_x = (width - barcode.width) / 2
    barcode.drawOn(c, barcode_x, box_y + 15)

    # --- Footer ---
    c.setFillColor(colors.white)
    c.setFont(FONT_BASE_NAME, 9)
    c.drawCentredString(width / 2, 45, "Verified by CabBuddy")

    c.setFont(FONT_BASE_BOLD_NAME, 9)
    c.drawCentredString(width / 2, 35, "@cab_buddy  |  cabbuddy.in")

    c.setFont(FONT_BASE_OBLIQUE_NAME, 8)
    c.drawCentredString(width / 2, 20, "“Traveling together makes memories stronger.”")

    c.setFont(FONT_BASE_BOLD_NAME, 9)
    c.drawCentredString(width / 2, 10, "– CabBuddy")

    c.save()
    return file_path


async def notify_final_group(group, bot):
    print(f"[INFO] notify_final_group called for group: {[u.get('username', 'N/A') for u in group]}")
    pass_id = generate_pass_id()

    for user in group:
        try:
            departure = datetime.fromisoformat(user['departure'])
        except Exception as e:
            print(f"[ERROR] Invalid departure format for user {user.get('username')}: {e}")
            continue

        user_data = {
            "username": user.get('username', 'N/A'),
            "chat_id": user.get('chat_id'),
            "destination": user.get('destination', 'Unknown'),
            "departure_str": departure.strftime("%d %b %Y, %I:%M %p"),
            "preferences": user.get('preferences', 'N/A'),
            "luggage": user.get('luggage', 'N/A'),
            "ride_buddies": [u.get('username') for u in group if u.get('username') != user.get('username')]
        }

        file_path = generate_premium_buddy_pass(user_data, pass_id)

        try:
            if bot:
                with open(file_path, "rb") as f:
                    await bot.send_document(
                        chat_id=user_data["chat_id"],
                        document=f,
                        filename=f"{user_data['username']}_premium_buddy_pass.pdf",
                        caption="🎟 Here is your Premium CabBuddy Pass!"
                    )
                print(f"[INFO] Sent Premium PDF to @{user_data['username']}")
            else:
                print(f"[INFO] PDF generated for @{user_data['username']} at {file_path}. Bot instance not provided.")
        except Exception as e:
            print(f"[ERROR] Failed to send PDF to @{user_data['username']}: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted temporary file: {file_path}")
