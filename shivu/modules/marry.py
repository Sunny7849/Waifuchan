from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from motor.motor_asyncio import AsyncIOMotorClient
from shivu import application
from datetime import datetime

client = AsyncIOMotorClient("mongodb+srv://GBAN:GBANKACHODA@cluster0gban.ejxkvzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0gban")
db = client["waifu_marry"]
waifu_coll = db["waifu_marriages"]
user_marry_coll = db["user_marriages"]

MARRIED_GIF = "https://media2.giphy.com/media/JUwliZWcyDmTQZ7m9L/giphy.gif"
pending_marry = set()
pending_divorce = set()

# /marry command
async def marry(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone you want to marry.")

    target_user = update.message.reply_to_message.from_user
    user = update.effective_user

    if user.id == target_user.id:
        return await update.message.reply_text("You can't marry yourself.")

    existing = await user_marry_coll.find_one({
        "$or": [{"user1": user.id, "user2": target_user.id}, {"user1": target_user.id, "user2": user.id}]
    })
    if existing:
        return await update.message.reply_text("You're already married.")

    key = frozenset([user.id, target_user.id])
    pending_marry.add(key)

    keyboard = [[InlineKeyboardButton("Will You Marry Me ❤️", callback_data=f"confirmmarry:{user.id}:{target_user.id}")]]
    await context.bot.send_message(
        chat_id=target_user.id,
        text=f"[{user.first_name}](tg://user?id={user.id}) wants to marry you!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Accept marriage
async def confirm_marry(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    from_id, to_id = map(int, query.data.split(":")[1:])
    uid = query.from_user.id
    key = frozenset([from_id, to_id])

    if uid not in key:
        return await query.answer("You're not part of this marriage!", show_alert=True)

    if key in pending_marry:
        pending_marry.remove(key)
        await user_marry_coll.insert_one({"user1": from_id, "user2": to_id, "date": datetime.utcnow()})
        return await query.edit_message_text("💖 Marriage Confirmed! You both are now married!")
    else:
        pending_marry.add(key)
        return await query.edit_message_text("Marriage requested! Waiting for the other person...")

# /divorce command
async def divorce(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    marriage = await user_marry_coll.find_one({"$or": [{"user1": user_id}, {"user2": user_id}]})
    if not marriage:
        return await update.message.reply_text("You're not married.")

    partner_id = marriage["user2"] if marriage["user1"] == user_id else marriage["user1"]
    key = frozenset([user_id, partner_id])
    pending_divorce.add(key)

    keyboard = [[InlineKeyboardButton("Are You Sure 💔", callback_data=f"confirmdivorce:{user_id}:{partner_id}")]]
    await context.bot.send_message(
        chat_id=partner_id,
        text="Divorce requested. Do you accept?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text("Divorce confirmation sent to your partner.")

# Confirm divorce
async def confirm_divorce(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    from_id, to_id = map(int, query.data.split(":")[1:])
    uid = query.from_user.id
    key = frozenset([from_id, to_id])

    if uid not in key:
        return await query.answer("You're not involved in this divorce!", show_alert=True)

    marriage = await user_marry_coll.find_one({"$or": [{"user1": from_id, "user2": to_id}, {"user1": to_id, "user2": from_id}]})
    if not marriage:
        return await query.edit_message_text("You're not married.")

    if key in pending_divorce:
        pending_divorce.remove(key)
        await user_marry_coll.delete_one({"_id": marriage["_id"]})
        return await query.edit_message_text("💔 Divorce successful. You're both single now.")
    else:
        pending_divorce.add(key)
        return await query.edit_message_text("Divorce confirmed by one. Waiting for the other...")

# Register Handlers
application.add_handler(CommandHandler("marry", marry))
application.add_handler(CommandHandler("divorce", divorce))
application.add_handler(CallbackQueryHandler(confirm_marry, pattern=r"^confirmmarry:"))
application.add_handler(CallbackQueryHandler(confirm_divorce, pattern=r"^confirmdivorce:"))
