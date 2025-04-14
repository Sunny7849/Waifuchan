from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from shivu import user_collection, collection

DEV_LIST = [8156600797]  # ✅ Only allowed for you

async def give_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in DEV_LIST:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to give a waifu!")
        return

    try:
        character_id = context.args[0]
        receiver_id = update.message.reply_to_message.from_user.id
        character = await collection.find_one({'id': character_id})

        if not character:
            return await update.message.reply_text("Character not found.")

        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': character}})

        caption = (
            f"Successfully Given To {receiver_id}\n"
            f" 🎏 𝙍𝙖𝙧𝙞𝙩𝙮: {character['rarity']}\n"
            f"🎐 𝘼𝙣𝙞𝙢𝙚: {character['anime']}\n"
            f"💕 𝙉𝙖𝙢𝙚: {character['name']}\n"
            f"🪅 𝙄𝘿: {character['id']}"
        )

        await update.message.reply_photo(photo=character['img_url'], caption=caption)

    except IndexError:
        await update.message.reply_text("Please provide a character ID.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def add_characters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in DEV_LIST:
        return

    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user:
        return await update.message.reply_text("User not found.")

    all_characters = await collection.find({}).to_list(None)
    existing_ids = {char['id'] for char in user.get('characters', [])}
    new_chars = [char for char in all_characters if char['id'] not in existing_ids]

    if not new_chars:
        return await update.message.reply_text("No new characters to add.")

    await user_collection.update_one({'id': user_id}, {'$push': {'characters': {'$each': new_chars}}})
    await update.message.reply_text(f"✅ {len(new_chars)} characters added.")


async def kill_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in DEV_LIST:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to the user whose character you want to remove.")

    try:
        character_id = context.args[0]
        receiver_id = update.message.reply_to_message.from_user.id

        await user_collection.update_one(
            {'id': receiver_id},
            {'$pull': {'characters': {'id': character_id}}}
        )

        await update.message.reply_text(f"Character {character_id} removed from {receiver_id}.")

    except IndexError:
        await update.message.reply_text("Please provide a character ID.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
