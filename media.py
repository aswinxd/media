import asyncio
import requests
from pymongo import MongoClient
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
app = Client(
    "heavyloadmediadeletebot",
    api_id="27589257",  
    api_hash="0af78b04b48361bc117fa4e06d6d2292",
    bot_token="7202657465:AAG76jhYMrrk2EL5idT9_QF58UDwc5sS1Aw"  
)

# MongoDB setup
mongo_client = AsyncIOMotorClient("mongodb+srv://bot:bot@cluster0.8vepzds.mongodb.net/?retryWrites=true&w=mmajority")
db = mongo_client["media_delete_bot"]
messages_collection = db["messages"]
DATABASE_NAME = 'mediabot'
COLLECTION_NAME = 'users'
DELETE_DELAY = 10 
#mongo_client = MongoClient(MONGO_URI)
#db = mongo_client[DATABASE_NAME]
users_collection = db[COLLECTION_NAME]

 
@app.on_message(filters.media & filters.group)
async def schedule_deletion(client, message):
    delete_at = datetime.utcnow() + timedelta(seconds=DELETE_DELAY)
    await messages_collection.insert_one({
        "chat_id": message.chat.id,
        "message_id": message.id,  
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

privacy_responses = {
    "info_collect": "We collect the following user data:\n- First Name\n- Last Name\n- Username\n- User ID\n These are public Telegram details that everyone can see.",
    "why_collect": "The collected data is used solely for improving your experience with the bot and for processing the bot stats and to avoid spammers.",
    "what_we_do": "We use the data to personalize your experience and provide better services.",
    "what_we_do_not_do": "We do not share your data with any third parties.",
    "right_to_process": "You have the right to access, correct, or delete your data. [Contact us](t.me/drxew) for any privacy-related inquiries."
}

@app.on_message(filters.command("privacy"))
async def privacy_command(client, message):
    privacy_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Privacy Policy", callback_data="privacy_policy")]]
    )
    await message.reply_text("Select one of the below options for more information about how the bot handles your privacy.", reply_markup=privacy_button)

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    if data == "privacy_policy":
        buttons = [
            [InlineKeyboardButton("What Information We Collect", callback_data="info_collect")],
            [InlineKeyboardButton("Why We Collect", callback_data="why_collect")],
            [InlineKeyboardButton("What We Do", callback_data="what_we_do")],
            [InlineKeyboardButton("What We Do Not Do", callback_data="what_we_do_not_do")],
            [InlineKeyboardButton("Right to Process", callback_data="right_to_process")]
        ]
        await callback_query.message.edit_text(
            "Our contact details \n Name: automedia deletor \n Telegram: @CodecArchive \n The bot has been made to protect and preserve privacy as best as possible. \n  Our privacy policy may change from time to time. If we make any material changes to our policies, we will place a prominent notice on @CodecBots.", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data in privacy_responses:
        back_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="privacy_policy")]]
        )
        await callback_query.message.edit_text(privacy_responses[data], reply_markup=back_button)

@app.on_message(filters.command("start") & filters.private)
async def handle_start_command(client, message):
    user_id = message.from_user.id
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})
    
    user_count = users_collection.count_documents({})
    
    instructions = (
        "Welcome! This is **media deletor**. This bot can delete media after specific time.\n"
        "• If you face any issues, please contact the support chat so developers can fix your issue.\n"
        "• Use the /privacy command to view the privacy policy, and interact with your data.\n"
        f"• Number of users on bot: {user_count}\n"
    )
    buttons = [
        [
            InlineKeyboardButton("Support Group", url="https://codecarchive.t.me"),
        ],
        [
            InlineKeyboardButton("Updates", url="https://codecbots.t.me")
        ]
    ]
    await message.reply_text(instructions, reply_markup=InlineKeyboardMarkup(buttons))

app.run()
