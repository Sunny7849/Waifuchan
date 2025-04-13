from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from telegram.error import TelegramError
from shivu import application, pm_users, group_user_totals_collection

OWNER_ID = 8156600797
GROUP_ID = -1002439979524
CHANNEL_ID = -1002646820042

DENY_MSG = "🎐I've been summoned by Dogesh Bhai🍷 You can't control me!"
REPLY_MSG = "🍃Reply to a message to broadcast it."
DONE_MSG = "💫Broadcast sent to all successfully."

# /broadcast to PM users
async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text(DENY_MSG)

    if not update.message.reply_to_message:
        return await update.message.reply_text(REPLY_MSG)

    msg = update.message.reply_to_message
    async for user in pm_users.find():
        try:
            await context.bot.copy_message(chat_id=user['_id'], from_chat_id=msg.chat_id, message_id=msg.message_id)
        except TelegramError:
            continue

    await update.message.reply_text(DONE_MSG)

# /gbroadcast to group
async def gbroadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text(DENY_MSG)

    if not update.message.reply_to_message:
        return await update.message.reply_text(REPLY_MSG)

    msg = update.message.reply_to_message
    try:
        await context.bot.copy_message(chat_id=GROUP_ID, from_chat_id=msg.chat_id, message_id=msg.message_id)
        await update.message.reply_text("✅ Sent to group.")
    except:
        await update.message.reply_text("❌ Failed to send to group.")

# /cbroadcast to channel
async def cbroadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text(DENY_MSG)

    if not update.message.reply_to_message:
        return await update.message.reply_text(REPLY_MSG)

    msg = update.message.reply_to_message
    try:
        await context.bot.copy_message(chat_id=CHANNEL_ID, from_chat_id=msg.chat_id, message_id=msg.message_id)
        await update.message.reply_text("✅ Sent to channel.")
    except:
        await update.message.reply_text("❌ Failed to send to channel.")

# Register handlers
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("gbroadcast", gbroadcast))
application.add_handler(CommandHandler("cbroadcast", cbroadcast))
