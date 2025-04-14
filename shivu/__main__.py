import importlib
import time
import random
import re
import asyncio
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, db, LOGGER, pm_users

from telegram.error import TelegramError

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}

OWNER_ID = 8156600797

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        message_frequency = chat_frequency.get('message_frequency', 100) if chat_frequency else 100

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await update.message.reply_text(f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour Messages Will be ignored for 10 Minutes...")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0

async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"""A New {character['rarity']} SealWaifu💫 Appeared...\n/slavewaifu Character Name and add in Your Sealwaifu Collection 👾""",
        parse_mode='Markdown'
    )

async def guess(update: Update, context: CallbackContext) -> None:
    # Same guess logic as your current version
    pass  # Keep your existing guess logic here

async def fav(update: Update, context: CallbackContext) -> None:
    # Same favorite logic as your current version
    pass  # Keep your existing fav logic here

# Broadcast Function (for PM users)
async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("🎐I've been summoned by Dogesh Bhai🍷 You can't control me!")

    if not update.message.reply_to_message:
        return await update.message.reply_text("🍃Reply to a message to broadcast it.")

    msg = update.message.reply_to_message
    async for user in pm_users.find():
        try:
            if msg.text:
                await context.bot.send_message(
                    chat_id=user['_id'],
                    text=msg.text,
                    entities=msg.entities,
                    reply_markup=msg.reply_markup
                )
            elif msg.photo:
                await context.bot.send_photo(
                    chat_id=user['_id'],
                    photo=msg.photo[-1].file_id,
                    caption=msg.caption or "",
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
            elif msg.video:
                await context.bot.send_video(
                    chat_id=user['_id'],
                    video=msg.video.file_id,
                    caption=msg.caption or "",
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
            else:
                await context.bot.copy_message(
                    chat_id=user['_id'],
                    from_chat_id=msg.chat_id,
                    message_id=msg.message_id
                )
        except TelegramError:
            continue

    await update.message.reply_text(
        "**Sensei i've Completed The Broadcast If you have any other work you need done, let me know🎐**",
        parse_mode="Markdown"
    )

def main() -> None:
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler(["slavewaifu", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()
