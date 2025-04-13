from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters
from shivu import application

user_data = {}

# Start command
async def start_button(update: Update, context: CallbackContext):
    user_data[update.effective_user.id] = {"step": "content", "buttons": []}
    await update.message.reply_text("Send the content (text/photo/video) to attach buttons.")

# Message flow
async def button_flow(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in user_data:
        return

    state = user_data[user_id]

    if state["step"] == "content":
        state["content"] = update.message
        state["step"] = "btn_text"
        await update.message.reply_text("Send the button text.")

    elif state["step"] == "btn_text":
        state["current_btn_text"] = update.message.text
        state["step"] = "btn_url"
        await update.message.reply_text("Now send the button URL.")

    elif state["step"] == "btn_url":
        btn_text = state.pop("current_btn_text")
        btn_url = update.message.text
        state["buttons"].append(InlineKeyboardButton(btn_text, url=btn_url))
        state["step"] = "add_more"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add More Buttons", callback_data="add_more")],
            [InlineKeyboardButton("✏️ Edit Last Button", callback_data="edit_last")],
            [InlineKeyboardButton("➖ Remove Last Button", callback_data="remove_last")],
            [InlineKeyboardButton("✅ Done", callback_data="done_buttons")]
        ])
        await update.message.reply_text("Button added! What next?", reply_markup=keyboard)

# Button callbacks
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        return

    state = user_data[user_id]

    if query.data == "add_more":
        state["step"] = "btn_text"
        await query.message.reply_text("Send next button text.")

    elif query.data == "remove_last":
        if state["buttons"]:
            removed = state["buttons"].pop()
            await query.message.reply_text(f"Removed button: {removed.text}")
        else:
            await query.message.reply_text("No buttons to remove.")

    elif query.data == "edit_last":
        if state["buttons"]:
            state["editing"] = True
            state["step"] = "btn_text"
            await query.message.reply_text("Send new text for last button.")
        else:
            await query.message.reply_text("No button to edit.")

    elif query.data == "done_buttons":
        content = state["content"]
        buttons = InlineKeyboardMarkup([[btn] for btn in state["buttons"]])

        try:
            if content.photo:
                await query.message.reply_photo(photo=content.photo[-1].file_id, reply_markup=buttons)
            elif content.video:
                await query.message.reply_video(video=content.video.file_id, reply_markup=buttons)
            elif content.text:
                await query.message.reply_text(text=content.text, reply_markup=buttons)
            else:
                await query.message.reply_text("Unsupported content.")
        except Exception as e:
            await query.message.reply_text(f"Error: {e}")

        del user_data[user_id]

# Edit flow
async def edit_button_flow(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in user_data:
        return

    state = user_data[user_id]

    if state.get("editing"):
        state["current_btn_text"] = update.message.text
        state["step"] = "btn_url"
        state["editing"] = "url"
        await update.message.reply_text("Now send new URL for last button.")
        return

    if state.get("editing") == "url":
        new_text = state.pop("current_btn_text")
        new_url = update.message.text
        state["buttons"][-1] = InlineKeyboardButton(new_text, url=new_url)
        state["editing"] = False
        state["step"] = "add_more"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add More Buttons", callback_data="add_more")],
            [InlineKeyboardButton("✏️ Edit Last Button", callback_data="edit_last")],
            [InlineKeyboardButton("➖ Remove Last Button", callback_data="remove_last")],
            [InlineKeyboardButton("✅ Done", callback_data="done_buttons")]
        ])
        await update.message.reply_text("Last button updated!", reply_markup=keyboard)

# Register handlers
application.add_handler(CommandHandler("button", start_button))
application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, button_flow))
application.add_handler(MessageHandler(filters.TEXT, edit_button_flow))
application.add_handler(CallbackQueryHandler(button_callback, pattern="add_more|done_buttons|remove_last|edit_last"))
