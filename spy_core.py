from telethon import TelegramClient, events
import sqlite3
from datetime import datetime
import asyncio
import sys

# --- CONFIGURATION ---
# നിന്റെ സ്വന്തം API ഡീറ്റൈൽസ്
API_ID = 23778342
API_HASH = '9525e6f6e968605d773e16a33a4fcf62'
# ---------------------

# ബോട്ട് ടോക്കൺ മാറ്റി, ഇനി നേരിട്ട് അക്കൗണ്ട് വഴി ലോഗിൻ ചെയ്യും
client = TelegramClient('spy_pro_session', API_ID, API_HASH,
                        connection_retries=10,
                        timeout=30)


def track_and_log(user_id, name, username, group):
    try:
        conn = sqlite3.connect('spy_pro_data.db')
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # യൂസർ ഉണ്ടോ എന്ന് നോക്കുന്നു
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

        # ആക്ടിവിറ്റി സേവ് ചെയ്യുന്നു
        cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?)", (user_id, name, username, group, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")


@client.on(events.NewMessage)
async def monitor_handler(event):
    # നീ മെമ്പർ ആയിട്ടുള്ള എല്ലാ ഗ്രൂപ്പുകളിലെയും മെസ്സേജുകൾ ഇത് ട്രാക്ക് ചെയ്യും
    if event.is_group:
        try:
            sender = await event.get_sender()
            user_id = event.sender_id
            name = getattr(sender, 'first_name', 'Unknown')
            username = getattr(sender, 'username', 'None')

            chat = await event.get_chat()
            group_title = getattr(chat, 'title', 'Private Group')

            # ഡാറ്റാബേസിലേക്ക് മാറ്റുന്നു
            track_and_log(user_id, name, username, group_title)
            print(f"📩 Logged: {name} in {group_title}")
        except Exception as e:
            print(f"Tracking Error: {e}")


async def main():
    print("🚀 Starting User-Bot Mode... Please wait.")
    try:
        # ഇവിടെ നിന്റെ ഫോൺ നമ്പർ ചോദിക്കും
        await client.start()
        print("✅ Success! Your account is now monitoring groups.")
        print("💡 Now, any message in your groups will be logged to the dashboard.")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        sys.exit()