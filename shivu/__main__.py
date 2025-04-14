from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from shivu import user_collection, collection
from datetime import datetime, timedelta

DEVS = [8156600797]
SUPPORT_CHAT_ID = -1002380442930

last_claim_time = {}

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/Anime_P_F_P")],
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/+ZTeO__YsQoIwNTVl")]
])

async def claim_toggle(state: str):
    await collection.update_one({}, {"$set": {"claim": state}}, upsert=True)

async def get_claim_state():
    doc = await collection.find_one({})
    return doc.get("claim", "False")

async def get_unique_characters(receiver_id, target_rarities=['(💮𝐌𝐲𝐭𝐡𝐢𝐜𝐚𝐥', '🔮𝐋𝐢𝐦𝐢𝐭𝐞𝐝 𝐄𝐝𝐢𝐭𝐢𝐨𝐧']):
    try:
        user = await user_collection.find_one({'id': receiver_id}, {'characters': 1})
        owned_ids = [char['id'] for char in user.get('characters', [])] if user else []

        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': owned_ids}}},
            {'$sample': {'size': 1}}
        ]
        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters
    except Exception as e:
        print(f"Error in get_unique_characters: {e}")
        return []

async def start_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in DEVS:
        return await update.message.reply_text("❌ Only developers can use this command.")
    await claim_toggle("True")
    await update.message.reply_text("✅ Claiming feature enabled!")

async def stop_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in DEVS:
        return await update.message.reply_text("❌ Only developers can use this command.")
    await claim_toggle("False")
    await update.message.reply_text("❌ Claiming feature disabled!")

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_id = user.id

    if chat.id != SUPPORT_CHAT_ID:
        return await update.message.reply_text("Command can only be used here: @Grabbing_Your_WH_Group")

    try:
        member = await context.bot.get_chat_member(SUPPORT_CHAT_ID, user_id)
        if member.status in ["left", "kicked"]:
            return await update.message.reply_text("Join the chat to use this command.", reply_markup=keyboard)
    except Exception:
        return await update.message.reply_text("Join the chat to use this command.", reply_markup=keyboard)

    if user_id == 7162166061:
        return await update.message.reply_text("You're banned from using this command.")

    claim_state = await get_claim_state()
    if claim_state == "False":
        return await update.message.reply_text("Claiming feature is currently disabled.")

    now = datetime.now()
    if user_id in last_claim_time and last_claim_time[user_id].date() == now.date():
        return await update.message.reply_text("You've already claimed today. Come back tomorrow.")

    last_claim_time[user_id] = now
    characters = await get_unique_characters(user_id)

    if characters:
        await user_collection.update_one({'id': user_id}, {'$push': {'characters': {'$each': characters}}})
        for char in characters:
            caption = f"<b>ᴄᴏɴɢʀᴀᴛ𝘀 🎊 {user.mention_html()}!</b>\n\n<b>🎀 ɴᴀᴍᴇ :</b> {char['name']}\n<b>⚜️ ᴀɴɪᴍᴇ :</b> {char['anime']}\n\n<b>ᴄᴏᴍᴇ ᴀɢᴀɪɴ ᴛᴏᴍᴏʀʀᴏᴡ ғᴏʀ ɴᴇ𝘅ᴛ ᴄʟᴀɪᴍ 🍀</b>"
            await update.message.reply_photo(photo=char['img_url'], caption=caption, parse_mode='HTML')
    else:
        await update.message.reply_text("No characters found for you to claim.")
