import importlib
import time
import random
import re
import asyncio
from html import escape

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import SUPPORT_CHAT, UPDATE_CHAT, db, LOGGER
from shivu.modules import ALL_MODULES

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(_, message: Message) -> None:
    chat_id = str(message.chat.id)
    user_id = message.from_user.id

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
                await message.reply_text(f"⚠️ Don't Spam {message.from_user.first_name}...\nYour Messages Will be ignored for 10 Minutes...")
                warned_users[user_id] = time.time()
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(message)
            message_counts[chat_id] = 0

async def send_image(message: Message) -> None:
    chat_id = message.chat.id
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

    await shivuu.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"A New {character['rarity']} SealWaifu💫 Appeared...\n/slavewaifu Character Name and add in Your Sealwaifu Collection 👾"
    )

@shivuu.on_message(filters.command(["slavewaifu", "protecc", "collect", "grab", "hunt"]))
async def guess(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌ Already Guessed By Someone.. Try Next Time Bruhh")
        return

    guess = " ".join(message.command[1:]).lower()

    if "()" in guess or "&" in guess.lower():
        await message.reply_text("Nahh You Can't use This Types of words in your guess..❌️")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        user = await user_collection.find_one({'id': user_id})
        if user:
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
        else:
            await user_collection.insert_one({
                'id': user_id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        await message.reply_text(
            f"<b><a href='tg://user?id={user_id}'>{escape(message.from_user.first_name)}</a></b> You Guessed a New Character ✅️\n\n"
            f"𝗡𝗔𝗠𝗘: <b>{last_characters[chat_id]['name']}</b>\n"
            f"𝗔𝗡𝗜𝗠𝗘: <b>{last_characters[chat_id]['anime']}</b>\n"
            f"𝗥𝗔𝗜𝗥𝗧𝗬: <b>{last_characters[chat_id]['rarity']}</b>\n\n"
            f"This Character added in Your harem.. use /harem To see your harem",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Seal Waifu💫", switch_inline_query_current_chat=f"collection.{user_id}")]]
            )
        )
    else:
        await message.reply_text("Please Write Correct Character Name... ❌️")

@shivuu.on_message(filters.command("fav"))
async def fav(_, message: Message):
    user_id = message.from_user.id
    args = message.command
    if len(args) < 2:
        await message.reply_text("Please provide Character id...")
        return

    character_id = args[1]
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await message.reply_text("You have not Guessed any characters yet....")
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await message.reply_text("This Character is Not In your collection")
        return

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
    await message.reply_text(f"Character {character['name']} has been added to your favorite...")

@shivuu.on_message(filters.all & filters.group)
async def message_track(client, message):
    await message_counter(client, message)

if __name__ == "__main__":
    LOGGER.info("Starting bot...")
    shivuu.run()
