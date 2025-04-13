from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from motor.motor_asyncio import AsyncIOMotorClient
from shivu import application
from datetime import datetime
import asyncio

client = AsyncIOMotorClient("mongodb+srv://GBAN:GBANKACHODA@cluster0gban.ejxkvzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0gban")
db = client["waifu_marry"]
waifu_coll = db["waifu_marriages"]
user_marry_coll = db["user_marriages"]

MARRIED_GIF = "https://media2.giphy.com/media/JUwliZWcyDmTQZ7m9L/giphy.gif"
pending_marry = {}
pending_divorce = {}

# /wmarry
async def wmarry(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        return await update.message.reply_text("Use: /wmarry <character_id>")
    char_id = context.args[0]
    user = update.effective_user
    if await waifu_coll.find_one({"char_id": char_id}):
        return await update.message.reply_text("This waifu is already married!")
    await waifu_coll.insert_one({"char_id": char_id, "user_id": user.id, "username": user.first_name, "date": datetime.utcnow()})
    await update.message.reply_text("You are now married to this waifu!")

# /wcouples
async def wcouples(update: Update, context: CallbackContext):
    cursor = waifu_coll.find()
    couples = [doc async for doc in cursor]
    if not couples:
        return await update.message.reply_text("No waifu marriages found yet.")
    text = "💍 Waifu Couples:\n\n"
    for c in couples:
        days = (datetime.utcnow() - c["date"]).days
        text += f"• Character ID: `{c['char_id']}`\n  Married by: [{c['username']}](tg://user?id={c['user_id']})\n  Since: {days} day(s)\n\n"
    await update.message.reply_text(text, parse_mode='Markdown')

# /wdivorce
async def wdivorce(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    removed = await waifu_coll.delete_one({"user_id": user_id})
    if removed.deleted_count == 0:
        return await update.message.reply_text("You haven't married any waifu.")
    await update.message.reply_text("💔 Waifu marriage ended. You're single again.")

# /marry
async def marry(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone you want to marry.")
    user = update.effective_user
    target = update.message.reply_to_message.from_user
    if user.id == target.id:
        return await update.message.reply_text("You can't marry yourself.")
    if await user_marry_coll.find_one({"$or": [{"user1": user.id, "user2": target.id}, {"user1": target.id, "user2": user.id}]}):
        return await update.message.reply_text("You're already married.")
    key = frozenset([user.id, target.id])
    pending_marry[key] = set()
    keyboard = [[InlineKeyboardButton("Will You Marry Me ❤️", callback_data=f"marry_confirm:{user.id}:{target.id}")]]
    await update.message.reply_text(
        f"[{user.first_name}](tg://user?id={user.id}) wants to marry [{target.first_name}](tg://user?id={target.id})",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Accept marry
async def confirm_marry(update: Update, context: CallbackContext):
    query = update.callback_query
    from_id, to_id = map(int, query.data.split(":")[1:])
    key = frozenset([from_id, to_id])
    uid = query.from_user.id
    if uid not in key:
        return await query.answer("You're not part of this proposal!", show_alert=True)
    if key not in pending_marry:
        return await query.edit_message_text("Request expired or invalid.")

    pending_marry[key].add(uid)
    if len(pending_marry[key]) == 2:
        await user_marry_coll.insert_one({"user1": from_id, "user2": to_id, "date": datetime.utcnow()})
        del pending_marry[key]
        return await query.edit_message_text("💖 Marriage Confirmed! You both are now married!")
    else:
        return await query.edit_message_text("First person is ready. Waiting for the other...")

# /married
async def married(update: Update, context: CallbackContext):
    couples = [doc async for doc in user_marry_coll.find()]
    if not couples:
        return await update.message.reply_text("No user marriages found yet.")
    text = "💍 Married Couples:\n\n"
    for c in couples:
        days = (datetime.utcnow() - c["date"]).days
        text += f"• [{c['user1']}](tg://user?id={c['user1']}) ❤️ [{c['user2']}](tg://user?id={c['user2']}) — {days} day(s)\n"
    await update.message.reply_animation(animation=MARRIED_GIF, caption=text + "\nLove is in the air...", parse_mode='Markdown')

# /divorce
async def divorce(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    match = await user_marry_coll.find_one({"$or": [{"user1": user_id}, {"user2": user_id}]})
    if not match:
        return await update.message.reply_text("You're not married.")
    partner = match["user2"] if match["user1"] == user_id else match["user1"]
    key = frozenset([user_id, partner])
    pending_divorce[key] = set()
    keyboard = [[InlineKeyboardButton("Are You Sure 💔", callback_data=f"divorce_confirm:{match['user1']}:{match['user2']}")]]
    await update.message.reply_text("Divorce initiated. Waiting for both confirmations.", reply_markup=InlineKeyboardMarkup(keyboard))

# Accept divorce
async def confirm_divorce(update: Update, context: CallbackContext):
    query = update.callback_query
    user1, user2 = map(int, query.data.split(":")[1:])
    key = frozenset([user1, user2])
    uid = query.from_user.id
    if uid not in key:
        return await query.answer("You're not part of this divorce!", show_alert=True)
    if key not in pending_divorce:
        return await query.edit_message_text("No active divorce found.")

    pending_divorce[key].add(uid)
    if len(pending_divorce[key]) == 2:
        # Countdown effect
        msg = await query.edit_message_text("Both confirmed. Finalizing in 10...")
        for i in range(9, 0, -1):
            await asyncio.sleep(0.8)
            await msg.edit_text(f"Finalizing in {i}...")
        await asyncio.sleep(1)
        await user_marry_coll.delete_one({"$or": [{"user1": user1, "user2": user2}, {"user1": user2, "user2": user1}]})
        del pending_divorce[key]
        await msg.edit_text("Now You Are UnMarried 🎐")
    else:
        await query.edit_message_text("First person is ready. Waiting for the other...")

# Register handlers
application.add_handler(CommandHandler("wmarry", wmarry))
application.add_handler(CommandHandler("wcouples", wcouples))
application.add_handler(CommandHandler("wdivorce", wdivorce))
application.add_handler(CommandHandler("marry", marry))
application.add_handler(CallbackQueryHandler(confirm_marry, pattern=r"^marry_confirm:"))
application.add_handler(CommandHandler("married", married))
application.add_handler(CommandHandler("divorce", divorce))
application.add_handler(CallbackQueryHandler(confirm_divorce, pattern=r"^divorce_confirm:"))
