import logging
from telegram.ext import Application, CommandHandler
from shivu.modules import (
    balance, broadcast, button, changetime, check, claim, dev_crmd,
    donate, eval as eval_cmd, give, harem, help as help_cmd, inlinequery,
    kiss, leaderboard, marry, ping, redeem, rocket, sell, sexplore, shop,
    start, status, sudoadd, trade, transfer, up, upload
)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token
TOKEN = "7539465396:AAFT5I6oK0wRJHSFNaAUMosQ4uFm2pHa7_c"

# Create the application instance
application = Application.builder().token(TOKEN).build()

# Registering all handlers
application.add_handler(CommandHandler("start", start.start))
application.add_handler(CommandHandler("balance", balance.balance))
application.add_handler(CommandHandler("broadcast", broadcast.broadcast))
application.add_handler(CommandHandler("button", button.button))
application.add_handler(CommandHandler("changetime", changetime.changetime))
application.add_handler(CommandHandler("check", check.check))
application.add_handler(CommandHandler("claim", claim.claim))
application.add_handler(CommandHandler("dev", dev_crmd.dev))
application.add_handler(CommandHandler("donate", donate.donate))
application.add_handler(CommandHandler("eval", eval_cmd.eval))
application.add_handler(CommandHandler("give", give.give))
application.add_handler(CommandHandler("harem", harem.harem))
application.add_handler(CommandHandler("help", help_cmd.help))
application.add_handler(CommandHandler("inlinequery", inlinequery.inlinequery))
application.add_handler(CommandHandler("kiss", kiss.kiss))
application.add_handler(CommandHandler("leaderboard", leaderboard.leaderboard))
application.add_handler(CommandHandler("marry", marry.marry))
application.add_handler(CommandHandler("ping", ping.ping))
application.add_handler(CommandHandler("redeem", redeem.redeem))
application.add_handler(CommandHandler("rocket", rocket.rocket))
application.add_handler(CommandHandler("sell", sell.sell))
application.add_handler(CommandHandler("sexplore", sexplore.sexplore))
application.add_handler(CommandHandler("shop", shop.shop))
application.add_handler(CommandHandler("status", status.status))
application.add_handler(CommandHandler("sudoadd", sudoadd.sudoadd))
application.add_handler(CommandHandler("trade", trade.trade))
application.add_handler(CommandHandler("transfer", transfer.transfer))
application.add_handler(CommandHandler("up", up.up))
application.add_handler(CommandHandler("upload", upload.upload))

# Start the bot
if __name__ == '__main__':
    application.run_polling()
