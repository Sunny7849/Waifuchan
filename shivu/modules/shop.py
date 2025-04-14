import random
import string
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

OWNER_ID = 8156600797

# Memory data
user_balances = {}
user_inventory = {}
user_rarity_choice = {}
redeem_codes = {}
user_gen_data = {}
user_sell_data = {}

# Rarities and Prices
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
    "1": 500,
    "2": 1000,
    "3": 2500,
    "4": 5000,
    "5": 10000,
    "6": 25000,
    "7": 50000,
    "8": 100000,
    "9": 250000,
    "10": 500000
}

def ensure_user(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 1000
    if user_id not in user_inventory:
        user_inventory[user_id] = []

# /shop
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{value} - {RARITY_PRICES[key]} coins", callback_data=f"rarity_{key}")]
        for key, value in RARITIES.items()
    ]
    await update.message.reply_text("Choose a rarity to buy waifu:", reply_markup=InlineKeyboardMarkup(keyboard))

# Handle rarity click
async def rarity_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rarity_key = query.data.split("_")[1]
    user_rarity_choice[query.from_user.id] = rarity_key
    await query.message.reply_text("Send the character ID using /buy <id>")

# /buy command
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if user_id not in user_rarity_choice:
        return await update.message.reply_text("❌ Use /shop and select a rarity first.")

    if len(context.args) == 0:
        return await update.message.reply_text("Usage: /buy <character_id>")

    char_id = context.args[0]
    rarity_key = user_rarity_choice[user_id]
    price = RARITY_PRICES[rarity_key]

    if user_balances[user_id] < price:
        return await update.message.reply_text("❌ Bro You Don’t Have Minimum Balance For Buy That Waifu!")

    user_balances[user_id] -= price
    user_inventory[user_id].append((char_id, rarity_key))
    await update.message.reply_text(f"✅ Bought waifu ID {char_id}\nRarity: {RARITIES[rarity_key]}\nBalance: {user_balances[user_id]}")
    del user_rarity_choice[user_id]

# /bal
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    await update.message.reply_text(f"💰 Balance: {user_balances[user_id]} coins")

# /gen
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    now = time.time()
    count, last_time = user_gen_data.get(user_id, (0, 0))

    if count >= 2 and now - last_time < 86400:
        return await update.message.reply_text("❌ You can only use /gen 2 times per day.")
    if now - last_time < 43200:
        return await update.message.reply_text("⏳ Wait 12 hours before using /gen again.")

    if user_balances[user_id] < 500:
        return await update.message.reply_text("❌ Need 500 coins to generate code.")

    user_balances[user_id] -= 500
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    redeem_codes[code] = 400
    user_gen_data[user_id] = (count + 1, now)

    await update.message.reply_text(f"✅ Generated Code: `{code}`", parse_mode='Markdown')

# /dgen (owner only)
async def dgen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only owner can use this.")
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    redeem_codes[code] = 1_000_000_000_000
    await update.message.reply_text(f"✅ Owner Code: `{code}`", parse_mode='Markdown')

# /redeem
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    if len(context.args) == 0:
        return await update.message.reply_text("Usage: /redeem <code>")
    code = context.args[0].strip().upper()
    if code in redeem_codes and redeem_codes[code] > 0:
        user_balances[user_id] += redeem_codes[code]
        del redeem_codes[code]
        await update.message.reply_text("✅ Code redeemed!")
    else:
        await update.message.reply_text("❌ Invalid or used code.")

# /sell
async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)

    if user_id in user_sell_data and time.time() - user_sell_data[user_id] < 86400:
        next_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user_sell_data[user_id] + 86400))
        return await update.message.reply_text(f"❌ You already sold today. Try after: {next_time}")

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /sell <character_id>")

    char_id = context.args[0]
    for (waifu, rarity_key) in user_inventory[user_id]:
        if waifu == char_id:
            context.user_data["pending_sell"] = (char_id, rarity_key)
            keyboard = [[InlineKeyboardButton("Are You Sure?", callback_data="confirm_sell")]]
            return await update.message.reply_text(f"Do you want to sell {char_id} ({RARITIES[rarity_key]})?", reply_markup=InlineKeyboardMarkup(keyboard))

    await update.message.reply_text("❌ You don't own that waifu.")

# Confirm sell
async def confirm_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if "pending_sell" in context.user_data:
        char_id, rarity_key = context.user_data["pending_sell"]
        if (char_id, rarity_key) in user_inventory[user_id]:
            price = RARITY_PRICES[rarity_key] // 2
            user_inventory[user_id].remove((char_id, rarity_key))
            user_balances[user_id] += price
            user_sell_data[user_id] = time.time()
            await query.message.reply_text(f"✅ Sold {char_id} for {price} coins.")
        else:
            await query.message.reply_text("❌ You don’t own that waifu anymore.")
    else:
        await query.message.reply_text("❌ No pending sell found.")

# Start Bot
app = Application.builder().token("7539465396:AAFT5I6oK0wRJHSFNaAUMosQ4uFm2pHa7_c").build()

app.add_handler(CommandHandler("shop", shop))
app.add_handler(CallbackQueryHandler(rarity_click, pattern=r"^rarity_\d+$"))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("bal", bal))
app.add_handler(CommandHandler("gen", gen))
app.add_handler(CommandHandler("dgen", dgen))
app.add_handler(CommandHandler("redeem", redeem))
app.add_handler(CommandHandler("sell", sell))
app.add_handler(CallbackQueryHandler(confirm_sell, pattern="^confirm_sell$"))

app.run_polling()
