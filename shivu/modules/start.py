import random
from html import escape
import importlib
import time
import random
import re
import asyncio
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters
from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES
locks = {}
message_counts = {}
sent_characters = {}
last_characters = {}
first_correct_guesses = {}
last_user = {}
warned_users = {}
# Auto-load other modules
for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)
# Message count logic to trigger spawns
async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]
    async with lock:
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id}) or {}
        message_frequency = chat_frequency.get('message_frequency', 5)
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                warned_users[user_id] = time.time()
                await update.message.reply_text(f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour Messages Will be ignored for 10 Minutes...")
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}
        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0
# Send new character image
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
    first_correct_guesses.pop(chat_id, None)
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character.get('img_file_id') or character.get('img_url'),
        caption=f"A New {character['rarity']} Character Appeared...\n/guess Character Name and add in Your Harem",
        parse_mode='Markdown'
    )
# Guess logic
async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id not in last_characters:
        return
    if chat_id in first_correct_guesses:
        await update.message.reply_text("❌  Already Guessed By Someone.. Try Next Time.")
        return
    guess_text = ' '.join(context.args).lower()
    if "()" in guess_text or "&" in guess_text:
        await update.message.reply_text("You can't use such characters in your guess.")
        return
    character = last_characters[chat_id]
    name_parts = character['name'].lower().split()
    if sorted(name_parts) == sorted(guess_text.split()) or any(part == guess_text for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'username': update.effective_user.username, 'first_name': update.effective_user.first_name},
             '$push': {'characters': character}},
            upsert=True
        )
        await group_user_totals_collection.update_one(
            {'user_id': user_id, 'group_id': chat_id},
            {'$set': {'username': update.effective_user.username, 'first_name': update.effective_user.first_name},
             '$inc': {'count': 1}},
            upsert=True
        )
        await top_global_groups_collection.update_one(
            {'group_id': chat_id},
            {'$set': {'group_name': update.effective_chat.title},
             '$inc': {'count': 1}},
            upsert=True
        )
        keyboard = [[InlineKeyboardButton("See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> You Guessed a New Character ✅ \n\n'
            f'𝗡𝗔𝗠𝗘: <b>{character["name"]}</b>\n𝗔𝗡𝗜𝗠𝗘: <b>{character["anime"]}</b>\n𝗥𝗔𝗥𝗜𝗧𝗬: <b>{character["rarity"]}</b>\n\n'
            'This Character added in Your harem. Use /harem to see.',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("Incorrect guess. Try again!")
# Upload command
async def upload(update: Update, context: CallbackContext) -> None:
    if not context.args or len(context.args) < 3:
        await update.message.reply_text("Please reply to an image or image URL with:\n`/upload Name Anime Rarity`", parse_mode='Markdown')
        return
    name, anime, rarity = context.args[0], context.args[1], context.args[2]
    reply = update.message.reply_to_message
    file_id, img_url = None, None
    if reply:
        if reply.photo:
            file_id = reply.photo[-1].file_id
        elif reply.text and reply.text.startswith("http"):
            img_url = reply.text
        else:
            await update.message.reply_text("Please reply to a photo or image URL.")
            return
    else:
        await update.message.reply_text("Please reply to a photo or image URL.")
        return
    character_id = f"{name.lower()}_{int(time.time())}"
    character_data = {
        'id': character_id,
        'name': name,
        'anime': anime,
        'rarity': rarity,
        'img_file_id': file_id,
        'img_url': img_url
    }
    await collection.insert_one(character_data)
    await update.message.reply_text(f"Character `{name}` from `{anime}` added successfully!", parse_mode='Markdown')
# Set favorite character
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text('Please provide Character ID.')
        return
    character_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})
    if not user or character_id not in [c['id'] for c in user.get('characters', [])]:
        await update.message.reply_text("Character not found in your harem.")
        return
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
    await update.message.reply_text("Character has been added to your favorites.")
def main() -> None:
    application.add_handler(CommandHandler("guess", guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(CommandHandler("upload", upload, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)
if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()
