from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from shivu.modules import (
    start, shop, broadcast, harem, marry, redeem, ping, donate, sexplore,
    rocket, trade, leaderboard, sudoadd, eval, upload, give, changetime,
    claim, transfer, button, check
)

application = Application.builder().token("7539465396:AAFT5I6oK0wRJHSFNaAUMosQ4uFm2pHa7_c").build()

# Start
application.add_handler(CommandHandler("start", start.start))  # ✅ Start registered
application.add_handler(CallbackQueryHandler(start.help_callback, pattern="help_msg"))
application.add_handler(CallbackQueryHandler(start.back_to_start, pattern="back_start"))

# Shop-related
application.add_handler(CommandHandler("shop", shop.shop))
application.add_handler(CommandHandler("buy", shop.buy))
application.add_handler(CommandHandler("bal", shop.bal))
application.add_handler(CommandHandler("gen", shop.gen))
application.add_handler(CommandHandler("dgen", shop.dgen))
application.add_handler(CommandHandler("redeem", shop.redeem))
application.add_handler(CommandHandler("sell", shop.sell))

# Broadcast
application.add_handler(CommandHandler("broadcast", broadcast.broadcast))

# Harem system
application.add_handler(CommandHandler("harem", harem.harem))

# Marry system
application.add_handler(CommandHandler("marry", marry.marry))
application.add_handler(CommandHandler("divorce", marry.divorce))

# Redeem features
application.add_handler(CommandHandler("waifugen", redeem.waifugen))
application.add_handler(CommandHandler("claimwaifu", redeem.claimwaifu))

# Simple utilities
application.add_handler(CommandHandler("ping", ping.ping))
application.add_handler(CommandHandler("donate", donate.donate))

# Extra
application.add_handler(CommandHandler("sexplore", sexplore.random_daily_reward))
application.add_handler(CommandHandler("rocket", rocket.rocket))
application.add_handler(CommandHandler("ptrade", rocket.ptrade))
application.add_handler(CommandHandler("trade", trade.trade))
application.add_handler(CommandHandler("gift", trade.gift))
application.add_handler(CommandHandler("leaderboard", leaderboard.leaderboard))
application.add_handler(CommandHandler("stats", leaderboard.stats))

# Admin/Dev
application.add_handler(CommandHandler("sudoadd", sudoadd.sudoadd))
application.add_handler(CommandHandler("removesudo", sudoadd.removesudo))
application.add_handler(CommandHandler("sudolist", sudoadd.sudolist))
application.add_handler(CommandHandler(["eval", "e", "ev", "eva"], eval.evaluate))
application.add_handler(CommandHandler(["exec", "x", "ex", "exe", "py"], eval.execute))
application.add_handler(CommandHandler("clearlocals", eval.clear))
application.add_handler(CommandHandler("upload", upload.upload_character))

# ✅ GIVE Commands
application.add_handler(CommandHandler("give", give.give_character_command))
application.add_handler(CommandHandler("add", give.add_characters_command))
application.add_handler(CommandHandler("kill", give.kill_character_command))

application.add_handler(CommandHandler("changetime", changetime.change_time))
application.add_handler(CommandHandler("claim", claim.claim))
application.add_handler(CommandHandler("startclaim", claim.start_claim))
application.add_handler(CommandHandler("stopclaim", claim.stop_claim))
application.add_handler(CommandHandler("transfer", transfer.transfer))
application.add_handler(CommandHandler("ik", check.find_users))
application.add_handler(CommandHandler("check", check.check_character))
application.add_handler(CallbackQueryHandler(check.handle_callback_query, pattern="slaves_"))

# Button system
application.add_handler(CommandHandler("button", button.start_button))
application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, button.button_flow))
application.add_handler(MessageHandler(filters.TEXT, button.edit_button_flow))
application.add_handler(CallbackQueryHandler(button.button_callback, pattern="add_more|done_buttons|remove_last|edit_last"))

# Run the bot
if __name__ == "__main__":
    application.run_polling()
