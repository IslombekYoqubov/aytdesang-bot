from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME


def make_bot_link(user_id: int) -> str:
    """Returns the raw deep-link URL for the user."""
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"


def make_share_url(user_id: int) -> str:
    """Returns a t.me/share/url link ready to use as a button URL."""
    bot_link = make_bot_link(user_id)
    share_text = quote("Menga anonim yoz 😏")
    return f"https://t.me/share/url?url={quote(bot_link)}&text={share_text}"


def link_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Storyga / do'stlarga yuborish",
            url=make_share_url(user_id),
        )],
        [InlineKeyboardButton(text="👀 Inboxni ko'rish", callback_data="inbox")],
    ])


def message_keyboard(msg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Anonim javob", callback_data=f"reply:{msg_id}"),
            InlineKeyboardButton(text="📤 Ulashish", callback_data=f"share:{msg_id}"),
        ],
        [InlineKeyboardButton(text="🚨 Shikoyat", callback_data=f"report:{msg_id}")],
    ])


def confirm_send_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_send"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_send"),
        ]
    ])


def my_link_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Ulashish",
            url=make_share_url(user_id),
        )],
    ])


# keep backward compat — some handlers call make_share_text()
def make_share_text(user_id: int) -> str:
    return make_bot_link(user_id)