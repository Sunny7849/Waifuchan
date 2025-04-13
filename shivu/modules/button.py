from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# States
ASK_CONTENT, ASK_BUTTON_TEXT, ASK_URL = range(3)

# Temporary user data storage
user_data_dict = {}

def button_command(update: Update, context: CallbackContext):
    update.message.reply_text("Send the content for add buttons (image/text/etc.)")
    return ASK_CONTENT

def get_content(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_data_dict[user_id] = {'content': update.message}
    update.message.reply_text("Now send the button text.")
    return ASK_BUTTON_TEXT

def get_button_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_data_dict:
        update.message.reply_text("Please start again with /button.")
        return ConversationHandler.END

    user_data_dict[user_id]['button_text'] = update.message.text
    update.message.reply_text("Now send the sharing URL.")
    return ASK_URL

def get_url(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_data_dict:
        update.message.reply_text("Please start again with /button.")
        return ConversationHandler.END

    data = user_data_dict.pop(user_id)
    url = update.message.text
    button_text = data['button_text']
    content_msg = data['content']

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=url)]])

    if content_msg.text:
        content = content_msg.text
        context.bot.send_message(chat_id=update.effective_chat.id, text=content, reply_markup=keyboard)
    elif content_msg.photo:
        photo_file_id = content_msg.photo[-1].file_id
        caption = content_msg.caption if content_msg.caption else ""
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file_id, caption=caption, reply_markup=keyboard)
    elif content_msg.video:
        video_file_id = content_msg.video.file_id
        caption = content_msg.caption if content_msg.caption else ""
        context.bot.send_video(chat_id=update.effective_chat.id, video=video_file_id, caption=caption, reply_markup=keyboard)
    else:
        update.message.reply_text("Unsupported content. Please send text, image, or video.")

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Add to your handler list
button_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("button", button_command)],
    states={
        ASK_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, get_content)],
        ASK_BUTTON_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_button_text)],
        ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_url)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
