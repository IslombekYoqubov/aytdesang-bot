from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, CommandObject

from config import BOT_USERNAME, MAX_MESSAGE_LENGTH, MAX_PENDING_MESSAGES
from database import upsert_user, get_user, save_message, count_pending_messages
from middlewares import contains_toxic
from utils import confirm_send_keyboard, link_keyboard, my_link_keyboard

router = Router()


class SenderState(StatesGroup):
    waiting_message = State()
    confirm_message = State()


@router.message(CommandStart(deep_link=True))
async def deep_link_entry(message: Message, command: CommandObject, state: FSMContext):
    sender = message.from_user
    await upsert_user(sender.id, sender.username, sender.full_name)

    raw = command.args or ""
    if not raw.isdigit():
        return  # not our format, skip

    target_id = int(raw)

    if target_id == sender.id:
        link = f"https://t.me/{BOT_USERNAME}?start={sender.id}"
        await message.answer(
            "😄 Bu sening o'z linking! Do'stlarga yubor:\n"
            f"<code>{link}</code>",
            reply_markup=my_link_keyboard(sender.id),
            parse_mode="HTML",
        )
        return

    target = await get_user(target_id)
    if not target:
        await message.answer("❌ Bu link endi ishlamaydi.")
        return

    pending = await count_pending_messages(target_id)
    if pending >= MAX_PENDING_MESSAGES:
        await message.answer(
            "😅 Bu odamning xabar qutisi to'lib ketgan. Keyinroq urinib ko'ring."
        )
        return

    name = target["full_name"] or target["username"] or "bu odamga"

    await state.set_state(SenderState.waiting_message)
    await state.update_data(target_id=target_id, target_name=name)

    await message.answer(
        f"✍️ <b>{name}</b>ga anonim xabar yoz.\n"
        f"U kim ekaningni <b>bilmaydi</b>. 😏\n\n"
        f"Xabaringni yoz (max {MAX_MESSAGE_LENGTH} ta belgi):",
        parse_mode="HTML",
    )


@router.message(SenderState.waiting_message, F.text)
async def receive_anon_message(message: Message, state: FSMContext):
    text = message.text.strip()

    if len(text) > MAX_MESSAGE_LENGTH:
        await message.answer(
            f"❌ Xabar juda uzun! Max {MAX_MESSAGE_LENGTH} ta belgi."
        )
        return

    if contains_toxic(text):
        await message.answer(
            "🚫 Xabarda haqoratli so'zlar bor.\n"
            "Iltimos, muloqot madaniyatiga rioya qiling va qayta yozing."
        )
        return

    await state.set_state(SenderState.confirm_message)
    await state.update_data(draft_text=text)

    data = await state.get_data()
    target_name = data.get("target_name", "bu odamga")

    await message.answer(
        f"📝 <b>Xabaring:</b>\n\n<i>\u201c{text}\u201d</i>\n\n"
        f"➡️ <b>{target_name}</b>ga yuboriladi.\n\n"
        f"Davom etamizmi?",
        reply_markup=confirm_send_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(SenderState.confirm_message, F.data == "confirm_send")
async def confirm_send(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    target_id = data.get("target_id")
    text = data.get("draft_text")

    if not target_id or not text:
        await state.clear()
        await call.message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
        return

    msg_id = await save_message(
        sender_id=call.from_user.id,
        receiver_id=target_id,
        text=text,
    )

    await state.clear()

    # notify receiver
    try:
        from utils import message_keyboard
        await call.bot.send_message(
            target_id,
            f"📩 Senga yangi <b>anonim xabar</b> keldi! 😏",
            parse_mode="HTML",
        )
        await call.bot.send_message(
            target_id,
            f"💌 <i>\u201c{text}\u201d</i>",
            reply_markup=message_keyboard(msg_id),
            parse_mode="HTML",
        )
    except Exception:
        pass  # user may have blocked bot — silent fail

    # sender confirmation + viral hook
    await call.message.edit_text(
        "✅ Xabar yuborildi!\n\n"
        "Senga ham anonim xabarlar kelishini xohlaysanmi? 😄\n"
        "O'z linkingni yarat va do'stlaringdan xabar ol!",
        reply_markup=link_keyboard(call.from_user.id),
    )


@router.callback_query(SenderState.confirm_message, F.data == "cancel_send")
async def cancel_send(call: CallbackQuery, state: FSMContext):
    await call.answer("Bekor qilindi")
    await state.clear()
    await call.message.edit_text("❌ Xabar yuborilmadi.")
