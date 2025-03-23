from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from itertools import groupby
import random
import math

# MongoDB Connection
from shivu import collection, user_collection, application  

async def harem(update: Update, context: CallbackContext, page=0):
    user_id = update.effective_user.id  
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user or not user['characters']:
        message = "<b>ʏᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ɢᴜᴇssᴇᴅ ᴀɴʏ ᴄʜᴀʀᴀᴄᴛᴇʀs ʏᴇᴛ.</b>"
        await update.message.reply_html(message) if update.message else await update.callback_query.edit_message_html(message)
        return
    
    # Retrieve selected rarity from the user's document
    selected_rarity = user.get('selected_rarity', "Default")
    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    
    # Filter characters based on rarity
    if selected_rarity != "Default":
        characters = [character for character in characters if character['rarity'][0] == selected_rarity[0]]
    
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    unique_characters = list({character['id']: character for character in characters}.values())

    total_pages = math.ceil(len(unique_characters) / 15)
    page = max(0, min(page, total_pages - 1))

    harem_message = f"{update.effective_user.first_name}'s ʜᴀʀᴇᴍ - ᴘᴀɢᴇ {page+1}/{total_pages}\n"

    current_characters = unique_characters[page*15:(page+1)*15]
    grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in grouped_characters.items():
        harem_message += f'\n<b>{anime}</b> ｛{len(characters)}/{await collection.count_documents({"anime": anime})}｝\n'
        harem_message += f'⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋\n'
        for character in characters:
            count = character_counts[character['id']]  
            harem_message += f'𒄬 {character["id"]} [{character["rarity"][0]}] {character["name"]} ×{count}\n'
        harem_message += f'⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋⚋\n'

    total_count = len(user['characters'])
    keyboard = [[InlineKeyboardButton(f"sᴇᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")]]

    if total_pages > 1:
        nav_buttons = [
            InlineKeyboardButton("⬅️ 1x", callback_data=f"harem:{page-1}:{user_id}") if page > 0 else None,
            InlineKeyboardButton("1x ➡️", callback_data=f"harem:{page+1}:{user_id}") if page < total_pages - 1 else None
        ]
        keyboard.append([btn for btn in nav_buttons if btn])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if user.get('favorites'):
        fav_character_id = user['favorites'][0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)
        image_url = fav_character.get('img_url') if fav_character else None
    else:
        random_character = random.choice(user['characters'])
        image_url = random_character.get('img_url') if 'img_url' in random_character else None

    if image_url:
        if update.message:
            await update.message.reply_photo(photo=image_url, caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        if update.message:
            await update.message.reply_text(harem_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.callback_query.edit_message_text(harem_message, reply_markup=reply_markup, parse_mode='HTML')


async def harem_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, page, user_id = query.data.split(':')
    page, user_id = int(page), int(user_id)

    if query.from_user.id != user_id:
        await query.answer("ᴅᴏɴ'ᴛ sᴛᴀʟᴋ ᴏᴛʜᴇʀ ᴜsᴇʀ's ʜᴀʀᴇᴍ..  OK", show_alert=True)
        return

    await harem(update, context, page)


# Handlers Register
application.add_handler(CommandHandler("harem", harem))
application.add_handler(CallbackQueryHandler(harem_callback, pattern='^harem'))

# Run the bot
if __name__ == "__main__":
    application.run_polling()
