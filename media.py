from pyrogram import Client, filters
import time
app = Client(
    "media_delete_bot",
    api_id="27589257",  
    api_hash="0af78b04b48361bc117fa4e06d6d2292",
    bot_token="7202657465:AAG76jhYMrrk2EL5idT9_QF58UDwc5sS1Aw"  
)
@app.on_message(filters.media & filters.group)
def delete_media_messages(client, message):
    time.sleep(10)
    try:
        message.delete()
        print(f"Deleted message from {message.chat.title} after 3000 seconds.")
    except Exception as e:
        print(f"Failed to delete message: {e}")
app.run()
