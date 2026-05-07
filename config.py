import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "aytdesang_bot")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
DB_PATH: str = os.getenv("DB_PATH", "aytdesang.db")

TOXIC_WORDS_UZ = [
    "lanat", "ahmoq", "tentak", "it", "eshak", "svoloch",
    "blyad", "pizda", "xui", "eblan", "mudak", "zalupa",
    "ублюдок", "сука", "пиздец",
]

SHARE_TEXT_TEMPLATE = (
    "Menga kimdir anonim xabar yozdi… senchi? 👀\n"
    "https://t.me/{bot_username}?start={user_id}"
)

MAX_MESSAGE_LENGTH = 500
MAX_PENDING_MESSAGES = 50
