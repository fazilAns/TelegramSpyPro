import os
import asyncio
import datetime
import subprocess
from telethon import TelegramClient, events
from pymongo import MongoClient

# --- CONFIGURATION ---
API_ID = 23778342 
API_HASH = '9525e6f6e968605d773e16a33a4fcf62'
MONGO_URI = "mongodb+srv://Fazil:fazil%402001@cluster0.jxxoihs.mongodb.net/?appName=Cluster0"
SESSION_NAME = 'spy_pro_live' 

# --- DATABASE SETUP ---
cluster = MongoClient(MONGO_URI)
db = cluster["telegram_spy"]
collection = db["messages"]

# --- TELEGRAM CLIENT SETUP ---
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def update_github_pages():
    """index.html ഗിറ്റ്‌ഹബ്ബിലേക്ക് പുഷ് ചെയ്യുന്നു"""
    try:
        subprocess.run(["git", "config", "--global", "user.email", "bot@spypro.com"])
        subprocess.run(["git", "config", "--global", "user.name", "SpyProBot"])
        subprocess.run(["git", "add", "index.html"])
        subprocess.run(["git", "commit", "-m", "🏎️ GT3 Dashboard Update"])
        subprocess.run(["git", "push"])
        print("🚀 Dashboard pushed to GitHub Pages!")
    except Exception as e:
        print(f"❌ GitHub Push Error: {e}")

def generate_html_dashboard():
    """ഡാറ്റാബേസിൽ നിന്നുള്ള വിവരങ്ങൾ വെച്ച് HTML ഫയൽ ഉണ്ടാക്കുന്നു"""
    try:
        messages = list(collection.find().sort("timestamp", -1).limit(50))
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GT3 Spy Pro Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 900px; margin: auto; }}
                h1 {{ color: #e30613; text-align: center; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px rgba(227, 6, 19, 0.5); }}
                .card {{ background: #1a1a1a; border-left: 5px solid #e30613; margin-bottom: 15px; padding: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }}
                .user {{ color: #00aaff; font-weight: bold; font-size: 1.1em; }}
                .time {{ color: #777; font-size: 0.8em; float: right; }}
                .message {{ margin-top: 8px; line-height: 1.5; color: #eee; font-size: 1.05em; }}
                .footer {{ text-align: center; margin-top: 40px; color: #444; font-size: 0.8em; border-top: 1px solid #222; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏎️ GT3 Spy Pro Live Feed</h1>
        """
        
        for msg in messages:
            html_content += f"""
                <div class="card">
                    <span class="time">{msg['timestamp']}</span>
                    <div class="user">👤 {msg['sender']}</div>
                    <div class="message">{msg['text']}</div>
                </div>
            """
            
        html_content += """
                <div class="footer">🏁 Powered by GT3 Spy Bot | 2026 Live Tracking</div>
            </div>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✅ index.html generated locally!")
        update_github_pages()
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")

@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        sender = await event.get_sender()
        name = getattr(sender, 'first_name', 'Unknown')
        text = event.raw_text
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if text:
            collection.insert_one({
                "sender": name,
                "text": text,
                "timestamp": timestamp
            })
            print(f"📩 New message from {name}: {text}")
            generate_html_dashboard()
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Starting Spy Pro Bot...")
    await client.start()
    print("✅ Connected to Telegram!")
    print("🏎️ GT3 is now on the track with new power!")
    
    generate_html_dashboard()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
