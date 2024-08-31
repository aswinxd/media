import asyncio
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

app = Client(
    "heavyloadmediadeletebot",
    api_id="27589257",  
    api_hash="0af78b04b48361bc117fa4e06d6d2292",
    bot_token="7202657465:AAG76jhYMrrk2EL5idT9_QF58UDwc5sS1Aw"  
)

# MongoDB setup
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client["media_delete_bot"]
messages_collection = db["messages"]

DELETE_DELAY = 10  
 
@app.on_message(filters.media & filters.group)
async def schedule_deletion(client, message):
    delete_at = datetime.utcnow() + timedelta(seconds=DELETE_DELAY)
    await messages_collection.insert_one({
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "delete_at": delete_at
    })

    print(f"Scheduled deletion for message {message.message_id} in chat {message.chat.id} at {delete_at}")

async def delete_expired_messages():

        now = datetime.utcnow()
        expired_messages = await messages_collection.find({"delete_at": {"$lte": now}}).to_list(None)
        for msg in expired_messages:
            try:
                await app.delete_messages(chat_id=msg["chat_id"], message_ids=msg["message_id"])
                print(f"Deleted message {msg['message_id']} in chat {msg['chat_id']}")
                await messages_collection.delete_one({"_id": msg["_id"]})
            except Exception as e:
                print(f"Failed to delete message {msg['message_id']} in chat {msg['chat_id']}: {e}")

        await asyncio.sleep(10)
app.add_handler(asyncio.ensure_future(delete_expired_messages()))
app.run()
