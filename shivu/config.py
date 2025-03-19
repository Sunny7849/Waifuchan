class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "6675050163"
    sudo_users = "6675050163", "6087651372","7640076990","1420481421","6645960688"
    GROUP_ID = -1002499806698
    TOKEN = "7998493919:AAF26_BXBF3IHiqb7jbAFlCDiTyV3_NeBVA"
    mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
    PHOTO_URL = ["https://graph.org/file/09e83a1d89aceabd480c5-2afc46a31083fe23f2.jpg", "https://graph.org/file/0aa659508c1add9ae4c86-2b335aa5262b7b64d2.jpg"]
    SUPPORT_CHAT = "Anime_Circle_Club"
    UPDATE_CHAT = "Waifu_Chan_Bot_updates"
    BOT_USERNAME = "@@Waifuwaiudnsj_Bot"
    CHARA_CHANNEL_ID = "-1002640379822"
    api_id = 28480539
    api_hash = "6320d9f1bc1f0b72ad66ebdb9d6bfc2c"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
