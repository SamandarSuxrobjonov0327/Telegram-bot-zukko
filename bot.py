import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = "TOKENINGNI_BU_YERGA_QO'Y"
CHANNEL_USERNAME = "@zukko_school"
ADMIN_ID = 226830885

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

posts = {}
pending_post = {}

STICKER_OPTIONS = {
    "1": "👍",
    "2": "👎",
    "3": "❤️",
    "4": "😂",
    "5": "🔥",
    "6": "👏",
    "7": "🤔",
    "8": "🥲",
    "9": "👌",
    "10": "🎉"
}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Salom! Menga post yuboring.")


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def get_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    pending_post[ADMIN_ID] = message

    kb = InlineKeyboardMarkup(row_width=2)
    for i in range(1, 11):
        kb.insert(InlineKeyboardButton(f"{i}️⃣ {STICKER_OPTIONS[str(i)]}", callback_data=f"choose:{i}"))

    await message.answer("Stiker tanlang:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("choose:"))
async def choose_sticker(callback: types.CallbackQuery):
    choice = callback.data.split(":")[1]
    emoji = STICKER_OPTIONS.get(choice, "👍")

    post = pending_post.get(ADMIN_ID)
    post_id = post.message_id

    posts[post_id] = {"post": post, "emoji": emoji, "votes": set()}

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📢 Kanalga yuborish", callback_data=f"send:{post_id}")
    )

    await callback.message.edit_text(f"{emoji} tanlandi", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("send:"))
async def send_post(callback: types.CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    data = posts.get(post_id)

    post = data["post"]
    emoji = data["emoji"]

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(f"{emoji} 0", callback_data=f"vote:{post_id}")
    )

    if post.photo:
        await bot.send_photo(CHANNEL_USERNAME, post.photo[-1].file_id, caption=post.caption or "", reply_markup=kb)
    elif post.text:
        await bot.send_message(CHANNEL_USERNAME, post.text, reply_markup=kb)

    await callback.message.answer("Post yuborildi!")


@dp.callback_query_handler(lambda c: c.data.startswith("vote:"))
async def vote(callback: types.CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    data = posts.get(post_id)

    user_id = callback.from_user.id

    if user_id in data["votes"]:
        await callback.answer("Oldin ovoz bergansiz!", show_alert=True)
        return

    data["votes"].add(user_id)
    count = len(data["votes"])
    emoji = data["emoji"]

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(f"{emoji} {count}", callback_data=f"vote:{post_id}")
    )

    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer("Ovoz qabul qilindi!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
