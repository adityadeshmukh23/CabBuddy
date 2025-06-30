# 🚕 CabBuddy – Scalable Ride-Matching Bot for Outstation Travel

CabBuddy is an automated, scalable ride-matching solution designed to streamline outstation cab pooling among IIT Kanpur students. Built using Python, Telegram Bot API, and clustering algorithms, it eliminates manual coordination by leveraging intelligent scheduling, real-time notifications, and dynamic PDF boarding passes.

---

## 📌 Objective

- Automate the process of outstation cab pooling using a conversational bot with real-time, intelligent group matching.
- Design an extensible backend capable of scaling across platforms (Telegram, WhatsApp) and integrating third-party services.

---

## ⚙️ Tech Stack

| Component        | Technologies Used                                   |
|------------------|-----------------------------------------------------|
| Backend Engine   | Python 3.11, APScheduler, asyncio                   |
| Bot Interface    | Telegram Bot API (python-telegram-bot)              |
| Database         | Firebase Firestore (NoSQL, real-time reads/writes) |
| Clustering Logic | DBSCAN (scikit-learn), Greedy batching heuristics   |
| PDF Generation   | ReportLab (dynamic, barcode-enhanced passes)        |
| Deployment Ready | GCP, Railway, or any cloud-based Python runner      |

---

## 🧠 Features

- **🧭 Smart Matching**: Uses DBSCAN to cluster rides based on departure time and destination vectors.
- **⚡ Greedy Batching**: Efficiently forms subgroups from clusters using a greedy algorithm with customizable group size limits.
- **📬 Real-Time Notifications**: Asynchronously notifies matched users via interactive Accept/Wait buttons.
- **📎 Dynamic Boarding Passes**: Sends stylized A6 PDF passes to confirmed users with personalized details and barcode.
- **⏰ Scheduled Reminders**: Sends a ride reminder 1 hour before departure.
- **💾 Persistent State**: Uses Firestore to store bookings, user preferences, group confirmations, and notification states.

---

## 🔁 System Architecture

User (Telegram) ──▶ Telegram Bot API
│
▼
Async Python Backend (Event-driven)
├── Booking Store (Firestore)
├── DBSCAN-based Clustering
├── Greedy Batching Algorithm
├── PDF Pass Generator
└── APScheduler (background tasks)


---

## 🚀 Current Stats

- ✅ **50+ bookings** and **32 confirmed matches** within the first 12 hours of rollout.
- 🧑‍🤝‍🧑 Over **200 group messages** exchanged with zero manual intervention.
- 📄 **100% delivery** of dynamic PDF boarding passes.
- 🔁 **Hourly scheduling** with <1s response latency in message delivery.

---

## 🔮 Roadmap

While the current version is focused on Telegram automation, the backend is built with extensibility in mind:

- ☑️ Plug-and-play support for WhatsApp and Web app frontends.
- ☑️ Ola/Uber API integration for direct cab bookings.
- ☑️ Razorpay/GPay-based in-app payments.
- ☑️ Admin dashboard for analytics, manual overrides, and user insights.

---

## 🧪 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/cabbuddy.git
   cd cabbuddy
2. Install dependencies
   ```bash
    pip install -r requirements.txt
4. Add config
    Place your firebase_key.json under a ~/secrets/ directory.
    Create a .env file with:
   ```bash
    TELEGRAM_BOT_TOKEN=your_bot_token
6. Start the bot
   ```bash
    python main.py



👨‍💻 Author

Aditya Deshmukh                                    
B.Tech, IIT Kanpur





🏁 License

This project is licensed under the MIT License. Contributions and forks are welcome!
