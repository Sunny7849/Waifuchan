import random
import string
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

OWNER_ID = 8156600797
user_balances = {}
user_inventory = {}
user_rarity_choice = {}
pending_sell = {}
redeem_codes = {}

RARITIES = {
    "1": "⚪ Common",
    "2": "🟣 Rare",
    "3": "🟢 Medium",
    "4": "🟡 Legendary",
    "5": "💮 Special Edition",
    "6": "🔮 Limited Edition",
    "7": "🎐 Celestial Beauty",
    "8": "🪽 Divine Edition",
    "9": "💦 Wet Elegance",
    "10": "🎴 Cosplay"
}

RARITY_PRICES = {
    "1": 10_000,
    "2": 50_000,
    "3": 100_000,
    "4": 500_000,
    "5": 1_000_000,
    "6": 5_000_000,
    "7": 10_000_000,
    "8": 25_000_000,
    "9": 50_000_000,
    "10": 100_000_000
}

def ensure_user(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 1000
    if user_id not in user_inventory:
        user_inventory[user_id] = []

async def shop(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"rarity_{key}")] for key, name in RARITIES.items()]
    await update.message.reply_text("Choose a rarity to view waifu price:", reply_markup=InlineKeyboardMarkup(keyboard))

async def rarity_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    rarity_key = query.data.split("_")[1]
    user_id = query.from_user.id
    user_rarity_choice[user_id] = rarity_key
    await query.message.reply_text("Send the waifu name (e.g., Zero Two):")

async def handle_waifu_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    waifu_name = update.message.text
    ensure_user(user_id)

    if user_id in user_rarity_choice:
        rarity_key = user_rarity_choice[user_id]
        price = RARITY_PRICES[rarity_key]
        rarity_name = RARITIES[rarity_key]

        if user_balances[user_id] >= price:
            user_balances[user_id] -= price
            user_inventory[user_id].append((waifu_name, rarity_key))
            await update.message.reply_text(
                f"✅ Bought {waifu_name}\nRarity: {rarity_name}\nCoins Left: {user_balances[user_id]}"
            )
        else:
            await update.message.reply_text("❌ Not enough coins.")
        del user_rarity_choice[user_id]
    else:
        await update.message.reply_text("Please use /shop and select a rarity first.")

async def bal(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    ensure_user(user_id)
    await update.message.reply_text(f"💰 Your balance: {user_balances[user_id]} coins")

async def sell(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    ensure_user(user_id)
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("Usage: /sell <waifu name> <rarity number>")

    waifu_name = " ".join(args[:-1])
    rarity_key = args[-1]

    if (waifu_name, rarity_key) in user_inventory[user_id]:
        pending_sell[user_id] = (waifu_name, rarity_key)
        keyboard = [[InlineKeyboardButton("Are You Sure!🪽", callback_data="confirm_sell")]]
        await update.message.reply_text(
            f"Do you want to sell {waifu_name} ({RARITIES[rarity_key]})?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("❌ You don't own that waifu.")

async def confirm_sell_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id in pending_sell:
        waifu_name, rarity_key = pending_sell[user_id]
        sell_price = RARITY_PRICES[rarity_key] // 2
        user_balances[user_id] += sell_price
        user_inventory[user_id].remove((waifu_name, rarity_key))
        await query.message.reply_text(
            f"✅ Sold {waifu_name} for {sell_price} coins.\n💰 New Balance: {user_balances[user_id]}"
        )
        del pending_sell[user_id]
    else:
        await query.message.reply_text("❌ Nothing to confirm.")

async def gen(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ You can't use this command.")

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    redeem_codes[code] = True
    await update.message.reply_text(f"✅ Generated redeem code: `{code}`", parse_mode='Markdown')

async def redeem(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    ensure_user(user_id)
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: /redeem <code>")

    code = args[0].strip().upper()
    if redeem_codes.get(code):
        user_balances[user_id] += 100_000_000_000
        redeem_codes[code] = False
        await update.message.reply_text("✅ Code redeemed! 100 Billion coins added.")
    else:
        await update.message.reply_text("❌ Invalid or already used code.")

# Handlers
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CallbackQueryHandler(rarity_button_handler, pattern=r"^rarity_\d+$"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waifu_name))
application.add_handler(CommandHandler("bal", bal))
application.add_handler(CommandHandler("sell", sell))
application.add_handler(CallbackQueryHandler(confirm_sell_handler, pattern="^confirm_sell$"))
application.add_handler(CommandHandler("gen", gen))
application.add_handler(CommandHandler("redeem", redeem))
