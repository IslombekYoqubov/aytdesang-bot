import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME: str = os.environ.get("BOT_USERNAME", "aytdesang_bot")
ADMIN_ID: int = int(os.environ.get("ADMIN_ID", "0"))
DB_PATH: str = os.environ.get("DB_PATH", "aytdesang.db")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN mavjud emas! Railway → Variables bo'limini tekshiring.")

TOXIC_WORDS_UZ = [
    "lanat", "ahmoq", "tentak", "eshak", "svoloch",
    "blyad", "pizda", "xui", "eblan", "mudak",
]

MAX_MESSAGE_LENGTH: int = 500
MAX_PENDING_MESSAGES: int = 50
