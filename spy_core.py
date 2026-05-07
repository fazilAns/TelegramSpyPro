from telethon import TelegramClient, events
from pymongo import MongoClient
from datetime import datetime
import asyncio
import subprocess
import os

# --- CONFIGURATION ---
API_ID = 23778342
API_HASH = '9525e6f6e968605d773e16a33a4fcf62'
SESSION_NAME = 'spy_pro_session' 

# നിന്റെ പാസ്‌വേഡ് (fazil@2001) ഇതിൽ സുരക്ഷിതമായി എൻകോഡ് ചെയ്തിട്ടുണ്ട് (%40)
MONGO_URI = "mongodb+srv://Fazil:fazil%402001@cluster0.jxxoihs.mongodb.net/?appName=Cluster0"
# ---------------------

# MongoDB Connection Setup
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client['spy_pro_db']
    collection = db['activity_logs']
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

def generate_html_dashboard():
    """MongoDB-ൽ നിന്ന് ഡാറ്റ എടുത്ത് index.html ഫയൽ ഉണ്ടാക്കുന്നു"""
    try:
        # ലേറ്റസ്റ്റ് 30 മെസ്സേജുകൾ എടുക്കുന്നു
        logs = list(collection.find().sort("timestamp", -1).limit(30))
        
        html_content = f"""
        <html>
        <head>
            <title>Spy Pro Live Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta http-equiv="refresh" content="60">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; text-align: center; }}
                .container {{ max-width: 900px; margin: auto; background: #111; padding: 20px; border-radius: 15px; border: 1px solid #00ff00; }}
                h2 {{ color: #00ff00; text-transform: uppercase; letter-spacing: 2px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; border-bottom: 1px solid #333; text-align: left; }}
                th {{ background: #222; color: #00ff00; }}
                tr:hover {{ background: #1a1a1a; }}
                .status {{ font-size: 12px; color: #888; margin-bottom: 10px; }}
                .refresh-note {{ font-size: 10px; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🏎️ Spy Pro GT3 Dashboard</h2>
                <p class="status">Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <table>
                    <tr><th>User</th><th>Group / Chat</th><th>Time</th></tr>
        """
        
        for log in logs:
            html_content += f"<tr><td>{log.get('name')}</td><td>{log.get('group_title')}</td><td>{log.get('timestamp')}</td></tr>"
            
        html_content += """
                </table>
                <p class="refresh-note">Auto-refreshes every 60 seconds</p>
            </div>
        </body>
        </html>
        """

        # index.html സേവ് ചെയ്യുന്നു
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # GitHub Pages-ലേക്ക് ഓട്ടോമാറ്റിക്കായി പുഷ് ചെയ്യുന്നു
        subprocess.run(["git", "config", "user.name", "GitHub Action"])
        subprocess.run(["git", "config", "user.email", "action@github.com"])
        subprocess.run(["git", "add", "index.html"])
        subprocess.run(["git", "commit", "-m", "Update dashboard logs [skip ci]"])
        subprocess.run(["git", "push"])
        print("📊 Dashboard updated and pushed to GitHub Pages!")

    except Exception as e:
        print(f"⚠️ Dashboard Update Error: {e}")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage)
async def monitor_handler(event):
    if event.is_group:
        try:
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            # ഡാറ്റ റെക്കോർഡ് ചെയ്യുന്നു
            log_data = {
                "name": getattr(sender, 'first_name', 'Unknown User'),
                "group_title": getattr(chat, 'title', 'Private Group'),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # MongoDB-ലേക്ക് സേവ് ചെയ്യുന്നു
            collection.insert_one(log_data)
            print(f"📩 New Message from {log_data['name']} in {log_data['group_title']}")
            
            # ഡാഷ്‌ബോർഡ് അപ്‌ഡേറ്റ് ചെയ്യുന്നു
            generate_html_dashboard()
            
        except Exception as e:
            print(f"Error logging message: {e}")

async def main():
    print("🚀 Starting Spy Pro Bot...")
    await client.start()
    print("🏎️ GT3 is now on the track! Monitoring groups...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
