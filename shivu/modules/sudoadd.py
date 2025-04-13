from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application
import json
import os

SUDO_FILE = "sudo_users.json"
OWNER_ID = 8156600797

# Create sudo file if doesn't exist
if not os.path.exists(SUDO_FILE):
    with open(SUDO_FILE, "w") as f:
        json.dump([str(OWNER_ID)], f)

# Load sudo users
with open(SUDO_FILE) as f:
    sudo_users = json.load(f)

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(sudo_users, f)

# /sudoadd
async def sudoadd(update: Update, context: CallbackContext):
    if str(update.effective_user.id) != str(OWNER_ID):
        return await update.message.reply_text("You are Not Worthy To Do This 🪽")

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a user to add as sudo.")

    user_id = str(update.message.reply_to_message.from_user.id)
    if user_id in sudo_users:
        return await update.message.reply_text("User is already a sudo.")

    sudo_users.append(user_id)
    save_sudo()
    await update.message.reply_text(f"Added [{update.message.reply_to_message.from_user.first_name}](tg://user?id={user_id}) as SUDO.", parse_mode="Markdown")

# /removesudo
async def removesudo(update: Update, context: CallbackContext):
    if str(update.effective_user.id) != str(OWNER_ID):
        return await update.message.reply_text("You are Not Worthy To Do This 🪽")

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to a sudo user to remove.")

    user_id = str(update.message.reply_to_message.from_user.id)
    if user_id not in sudo_users:
        return await update.message.reply_text("User is not in sudo list.")

    sudo_users.remove(user_id)
    save_sudo()
    await update.message.reply_text(f"Removed [{update.message.reply_to_message.from_user.first_name}](tg://user?id={user_id}) from SUDO list.", parse_mode="Markdown")

# /sudolist
async def sudolist(update: Update, context: CallbackContext):
    if not sudo_users:
        return await update.message.reply_text("No sudo users found.")

    msg = "👑 Current SUDO Users:\n\n" + "\n".join([f"• <code>{uid}</code>" for uid in sudo_users])
    await update.message.reply_text(msg, parse_mode="HTML")

# Add handlers
application.add_handler(CommandHandler("sudoadd", sudoadd))
application.add_handler(CommandHandler("removesudo", removesudo))
application.add_handler(CommandHandler("sudolist", sudolist))
