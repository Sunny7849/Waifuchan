from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from shivu import application

DONATE_IMG = "https://graph.org/file/83e4be836d2030b3abed2-2bb73dde11d2894e58.jpg"

DONATE_TEXT = (
    "Hey kind soul,\n\n"
    "We're building this bot with love and late-night Maggi.\n"
    "If you enjoy it, consider supporting us.\n\n"
    "*Please help us — just ₹10 can fuel a lot.*\n\n"
    "Much love, from the devs!"
)

DONATE_BTN = [[InlineKeyboardButton("🎐 Donate For Our Work 🪽", url="https://t.me/YourDonationLink")]]  # <- Replace this URL with your actual donation/pay link

async def donate(update: Update, context: CallbackContext):
    await update.message.reply_photo(
        photo=DONATE_IMG,
        caption=DONATE_TEXT,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(DONATE_BTN)
    )

application.add_handler(CommandHandler("donate", donate))
