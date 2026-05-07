from telethon import TelegramClient, events
import sqlite3
from datetime import datetime
import asyncio
import sys
import os

# --- CONFIGURATION ---
API_ID = 23778342
API_HASH = '9525e6f6e968605d773e16a33a4fcf62'
# Note: Telethon adds .session automatically, so we use the base name
SESSION_NAME = 'spy_pro_session' 
DB_NAME = 'spy_pro_data.db'
# ---------------------

def setup_db():
    """Initializes the database and creates required tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for current user details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_users (
            user_id INTEGER PRIMARY KEY,
            last_name TEXT,
            last_username TEXT
        )
    ''')
    
    # Table for name/username change history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            user_id INTEGER,
            old_name TEXT,
            old_username TEXT,
            changed_at TEXT
        )
    ''')
    
    # Table for message activity logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity (
            user_id INTEGER,
            name TEXT,
            username TEXT,
            group_title TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[*] Database initialized: {DB_NAME}")

def track_and_log(user_id, name, username, group):
    """Logs user activity and tracks name/username changes."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check for existing user to track changes
        cursor.execute("SELECT last_name, last_username FROM current_users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()

        if result:
            old_name, old_username = result
            if old_name != name or old_username != username:
                cursor.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (user_id, old_name, old_username, now))
                cursor.execute("UPDATE current_users SET last_name=?, last_username=? WHERE user_id=?", 
                               (name, username, user_id))
        else:
            cursor.execute("INSERT INTO current_users VALUES (?, ?, ?)", (user_id, name, username))

        # Log the current activity
        cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?)", (user_id, name, username, group, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Database Error: {e}")

# Initialize Telegram Client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH, 
                        connection_retries=10, 
                        timeout=30)

@client.on(events.NewMessage)
async def monitor_handler(event):
    """Handler for incoming messages in groups."""
    if event.is_group:
        try:
            sender = await event.get_sender()
            user_id = event.sender_id
            name = getattr(sender, 'first_name', 'Unknown')
            username = getattr(sender, 'username', 'None')

            chat = await event.get_chat()
            group_title = getattr(chat, 'title', 'Private Group')

            track_and_log(user_id, name, username, group_title)
            print(f"LOG: {name:15} | {group_title}")
        except Exception as e:
            # Silent fail for minor event errors to keep bot alive
            pass

async def main():
    print("="*50)
    print("🚀 STARTING SPY-PRO MONITORING SYSTEM")
    print("="*50)
    
    # Setup Database before starting
    setup_db()
    
    try:
        # Start client (uses the uploaded .session file)
        await client.start()
        
        if await client.is_user_authorized():
            print("✅ LOGIN SUCCESSFUL")
            print(f"📡 STATUS: Monitoring active groups...")
            print("-" * 50)
            await client.run_until_disconnected()
        else:
            print("⚠️ SESSION EXPIRED: Please update the .session file.")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 SYSTEM SHUTDOWN BY USER.")
        sys.exit()
