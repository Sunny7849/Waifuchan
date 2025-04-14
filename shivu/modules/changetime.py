from telegram import Update
from telegram.ext import ContextTypes
from pymongo import ReturnDocument
from shivu import user_totals_collection

ADMIN_STATUSES = ["administrator", "creator"]

async def change_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ADMIN_STATUSES:
            await update.message.reply_text("You are not an Admin.")
            return

        if len(context.args) != 1:
            await update.message.reply_text("Please use: /changetime NUMBER")
            return

        new_frequency = int(context.args[0])
        if new_frequency < 10:
            await update.message.reply_text("The message frequency must be greater than or equal to 10.")
            return

        await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat.id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await update.message.reply_text(f"Successfully changed to {new_frequency}")

    except Exception as e:
        await update.message.reply_text(f"Failed to change: {e}")
