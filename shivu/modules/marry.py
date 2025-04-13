from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from motor.motor_asyncio import AsyncIOMotorClient
from shivu import application
from datetime import datetime

# MongoDB Setup
client = AsyncIOMotorClient("mongodb+srv://GBAN:GBANKACHODA@cluster0gban.ejxkvzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0gban")
db = client["waifu_marry"]
waifu_coll = db["waifu_marriages"]
user_marry_coll = db["user_marriages"]

MARRIED_GIF = "https://media2.giphy.com/media/JUwliZWcyDmTQZ7m9L/giphy.gif"

# 1. /wmarry
async def wmarry(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        return await update.message.reply_text("Use: /wmarry <character_id>")

    user_id = update.effective_user.id
    char_id = context.args[0]

    already = await waifu_coll.find_one({"char_id": char_id})
    if already:
        return await update.message.reply_text("This waifu is already married!")

    await waifu_coll.insert_one({
        "char_id": char_id,
        "user_id": user_id,
        "username": update.effective_user.first_name,
        "date": datetime.utcnow()
    })
    await update.message.reply_text("You are now married to this waifu!")

# 2. /wcouples
async def wcouples(update: Update, context: CallbackContext):
    cursor = waifu_coll.find()
    couples = [doc async for doc in cursor]
    if not couples:
        return await update.message.reply_text("No waifu marriages found yet.")

    text = "💍 Waifu Couples:\n\n"
    for c in couples:
        days = (datetime.utcnow() - c["date"]).days
        text += f"• Character ID: `{c['char_id']}`\n  Married by: [{c['username']}](tg://user?id={c['user_id']})\n  Duration: {days} day(s)\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')

# 3. /marry
async def marry(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone you want to marry.")

    target_user = update.message.reply_to_message.from_user
    user = update.effective_user

    if user.id == target_user.id:
        return await update.message.reply_text("You can't marry yourself, silly.")

    keyboard = [[InlineKeyboardButton("Will You Marry Me 🍫", callback_data=f"acceptmarry:{user.id}")]]
    await update.message.reply_text(
        f"Hey [{target_user.first_name}](tg://user?id={target_user.id})!\n\n"
        f"[{user.first_name}](tg://user?id={user.id}) wants to marry you!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Accept callback
async def accept_marry_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    from_id = int(query.data.split(":")[1])
    to_id = query.from_user.id

    already = await user_marry_coll.find_one({
        "$or": [{"user1": from_id, "user2": to_id}, {"user1": to_id, "user2": from_id}]
    })
    if already:
        return await query.edit_message_text("You're already married.")

    await user_marry_coll.insert_one({
        "user1": from_id,
        "user2": to_id,
        "date": datetime.utcnow()
    })

    await query.edit_message_text("💖 Marriage Accepted! You both are now married!")

# 4. /married
async def married(update: Update, context: CallbackContext):
    cursor = user_marry_coll.find()
    pairs = [doc async for doc in cursor]
    if not pairs:
        return await update.message.reply_text("No user marriages found yet.")

    text = "💍 Married Couples:\n\n"
    for pair in pairs:
        days = (datetime.utcnow() - pair["date"]).days
        text += f"• [{pair['user1']}](tg://user?id={pair['user1']}) ❤️ [{pair['user2']}](tg://user?id={pair['user2']}) — {days} day(s)\n"

    await update.message.reply_animation(
        animation=MARRIED_GIF,
        caption=text + "\nLove is in the air... always.",
        parse_mode='Markdown'
    )

# 5. /divorce
async def divorce(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    removed = await user_marry_coll.delete_one({"$or": [{"user1": user_id}, {"user2": user_id}]})
    if removed.deleted_count == 0:
        return await update.message.reply_text("You're not married.")
    await update.message.reply_text("💔 Divorce done. You are now single.")

# 6. /wdivorce
async def wdivorce(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    removed = await waifu_coll.delete_one({"user_id": user_id})
    if removed.deleted_count == 0:
        return await update.message.reply_text("You haven't married any waifu.")
    await update.message.reply_text("💔 Waifu marriage ended. You're single again.")

# Register handlers
application.add_handler(CommandHandler("wmarry", wmarry))
application.add_handler(CommandHandler("wcouples", wcouples))
application.add_handler(CommandHandler("marry", marry))
application.add_handler(CallbackQueryHandler(accept_marry_callback, pattern=r'^acceptmarry:'))
application.add_handler(CommandHandler("married", married))
application.add_handler(CommandHandler("divorce", divorce))
application.add_handler(CommandHandler("wdivorce", wdivorce))
