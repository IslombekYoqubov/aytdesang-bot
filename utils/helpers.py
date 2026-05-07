from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME, SHARE_TEXT_TEMPLATE


def make_share_text(user_id: int) -> str:
    return SHARE_TEXT_TEMPLATE.format(bot_username=BOT_USERNAME, user_id=user_id)


def link_keyboard(user_id: int) -> InlineKeyboardMarkup:
    share_text = make_share_text(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Storyga / do'stlarga yuborish",
            url=f"https://t.me/share/url?url={share_text}&text=Menga+anonim+yoz+%F0%9F%98%8F"
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
    share_text = make_share_text(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Ulashish",
            url=f"https://t.me/share/url?url={share_text}"
        )],
    ])
