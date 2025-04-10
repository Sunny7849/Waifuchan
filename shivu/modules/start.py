import asyncio
import random
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler

from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection 

# Alag lists for gifs
PHOTO_URL_PM = [
    "https://media0.giphy.com/media/BfevCgt1YxDTW/giphy.gif",
    "https://media4.giphy.com/media/6sv3Z8wXzyEzC/giphy.gif",
    "https://media4.giphy.com/media/5D8fDjKyQfuZW/giphy.gif"
]

PHOTO_URL_GC = [
    "https://media2.giphy.com/media/HXN6ZE2FbnH44/giphy.gif",
    "https://media1.giphy.com/media/bJ0TSiVhirmlG/giphy.gif",
    "https://media0.giphy.com/media/8SEnoMhrEeBDa/giphy.gif"
]

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    args = context.args
    if args and args[0] == "help":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Help Command Here...")
        return

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        await context.bot.send_message(chat_id=GROUP_ID, 
                                       text=f"New user Started The Bot..\nUser: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>", 
                                       parse_mode='HTML')
    else:
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    # Summoning animation lines
    loading_lines = [
        "⏳ Initializing summoning core...",
        "⚡ Channeling chakra streams...",
        "🔍 Searching anime multiverse...",
        "🌀 Binding character essence...",
        "✨ Summoning Jutsu Activated! ✨"
    ]

    for line in loading_lines:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=line)
        await asyncio.sleep(1.2)

    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
        [InlineKeyboardButton("SUPPORT", url='https://t.me/Anime_Circle_Club'),
         InlineKeyboardButton("UPDATES", url='https://t.me/+vDcCB_w1fxw1YTll')],
        [InlineKeyboardButton("HELP", url=f"http://t.me/{BOT_USERNAME}?start=help")],
        [InlineKeyboardButton("SOURCE", url='https://github.com/MyNameIsShekhar/WAIFU-HUSBANDO-CATCHER')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.effective_chat.type == "private":
        caption = """
✨ 𝙎𝙪𝙢𝙢𝙤𝙣𝙞𝙣𝙜 𝙅𝙪𝙩𝙨𝙪 𝘼𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙! ✨  
𝙄’𝙢 𝙣𝙤𝙩 𝙟𝙪𝙨𝙩 𝙖 𝙗𝙤𝙩...  
𝙄’𝙢 𝙩𝙝𝙚 𝙜𝙖𝙩𝙚𝙠𝙚𝙚𝙥𝙚𝙧 𝙩𝙤 𝙮𝙤𝙪𝙧 𝙡𝙚𝙜𝙚𝙣𝙙𝙖𝙧𝙮 𝙃𝙖𝙧𝙚𝙢.

𝗛𝗲𝗿𝗲’𝘀 𝘄𝗵𝗮𝘁 𝗜 𝗱𝗼:
— 𝘼𝙛𝙩𝙚𝙧 𝙚𝙫𝙚𝙧𝙮 𝟭𝟬𝟬 𝙢𝙚𝙨𝙨𝙖𝙜𝙚𝙨  
— 𝙄 𝙙𝙧𝙤𝙥 𝙖 𝙧𝙖𝙣𝙙𝙤𝙢 𝙖𝙣𝙞𝙢𝙚 𝙘𝙝𝙖𝙧𝙖𝙘𝙩𝙚𝙧  
— 𝙁𝙞𝙧𝙨𝙩 𝙩𝙤 𝙪𝙨𝙚 /𝙜𝙪𝙚𝙨𝙨 𝙬𝙞𝙣𝙨 𝙩𝙝𝙚𝙢  
— 𝘽𝙪𝙞𝙡𝙙 𝙮𝙤𝙪𝙧 𝙘𝙤𝙡𝙡𝙚𝙘𝙩𝙞𝙤𝙣, 𝙩𝙧𝙖𝙙𝙚, 𝙜𝙞𝙛𝙩, 𝙛𝙡𝙚𝙭 𝙬𝙞𝙩𝙝 /𝙝𝙖𝙧𝙚𝙢, /𝙩𝙤𝙥 𝙖𝙣𝙙 𝙢𝙤𝙧𝙚

𝗕𝗨𝗧 𝗪𝗔𝗜𝗧...

𝙏𝙝𝙞𝙨 𝙞𝙨𝙣’𝙩 𝙟𝙪𝙨𝙩 𝙖 𝙜𝙖𝙢𝙚 —  
𝙏𝙝𝙞𝙨 𝙞𝙨 𝙮𝙤𝙪𝙧 𝙧𝙞𝙨𝙚 𝙩𝙤 𝙗𝙚𝙘𝙤𝙢𝙞𝙣𝙜 𝙩𝙝𝙚 𝗛𝗮𝗿𝗲𝗺 𝗞𝗶𝗻𝗴/𝗤𝘂𝗲𝗲𝗻.

𝗦𝗼 𝘄𝗵𝗮𝘁 𝗻𝗼𝘄?  
𝗝𝘂𝘀𝘁 𝗼𝗻𝗲 𝗰𝗹𝗶𝗰𝗸...  
𝗨𝗻𝗹𝗲𝗮𝘀𝗵 𝘁𝗵𝗲 𝗺𝗮𝗱𝗻𝗲𝘀𝘀. 𝗥𝘂𝗹𝗲 𝘁𝗵𝗲 𝘄𝗮𝗶𝗳𝘂 𝘄𝗼𝗿𝗹𝗱.

[ + ] 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽  
𝗟𝗲𝘁 𝘁𝗵𝗲 𝗵𝘂𝗻𝘁 𝗯𝗲𝗴𝗶𝗻!
"""
        gif_url = random.choice(PHOTO_URL_PM)
    else:
        caption = "🎴Alive!?... \nConnect to me in PM for more information"
        gif_url = random.choice(PHOTO_URL_GC)

    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

# Handler registration
application.add_handler(CommandHandler('start', start, block=False))
