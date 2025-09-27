import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

API_TOKEN = "8267465259:AAHYRxwccqb-mbj5GJ6_cZqYOu3jycsVOgI"
CHANNEL_USERNAME = "@RishLaptop"
ADMIN_ID = 6743839154

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Postlar xotirasi
posts = {}         # post_id -> { "post": Message, "sticker_emoji": str, "votes": set() }
pending_post = {}  # admin_id -> post message


# Stiker variantlari (10 ta)
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


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Salom! Menga post yuboring (matn, rasm, video, link va hokazo).")


# Har qanday postni qabul qilish
@dp.message(F.text | F.photo | F.video | F.document | F.animation)
async def get_post(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    pending_post[ADMIN_ID] = message

    # Stiker tanlash tugmalari
    kb = InlineKeyboardBuilder()
    for i in range(1, 11):
        kb.button(text=f"{i}️⃣ {STICKER_OPTIONS[str(i)]}", callback_data=f"choose:{i}")
    kb.adjust(2)

    await message.answer("✅ Post qabul qilindi!\nEndi reaksiyani bildiruvchi stiker turini tanlang:", reply_markup=kb.as_markup())


# Stiker tanlash
@dp.callback_query(F.data.startswith("choose:"))
async def choose_sticker(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Faqat admin tanlashi mumkin!", show_alert=True)
        return

    choice = callback.data.split(":")[1]
    emoji = STICKER_OPTIONS.get(choice, "👍")

    post = pending_post.get(ADMIN_ID)
    if not post:
        await callback.answer("Post topilmadi!", show_alert=True)
        return

    post_id = post.message_id
    posts[post_id] = {"post": post, "sticker_emoji": emoji, "votes": set()}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga yuborish", callback_data=f"send:{post_id}")]
    ])

    await callback.message.edit_text(f"👉 Siz {emoji} reaksiyasini tanladingiz!\nEndi postni kanalga yuborishingiz mumkin.", reply_markup=kb)


# Kanalga yuborish
@dp.callback_query(F.data.startswith("send:"))
async def send_to_channel(callback: types.CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    data = posts.get(post_id)

    if not data:
        await callback.answer("Post topilmadi!", show_alert=True)
        return

    post = data["post"]
    emoji = data["sticker_emoji"]

    kb = InlineKeyboardBuilder()
    kb.button(text=f"{emoji} 0", callback_data=f"vote:{post_id}")
    kb.adjust(1)

    if post.photo:
        await bot.send_photo(CHANNEL_USERNAME, post.photo[-1].file_id, caption=post.caption or "", reply_markup=kb.as_markup())
    elif post.video:
        await bot.send_video(CHANNEL_USERNAME, post.video.file_id, caption=post.caption or "", reply_markup=kb.as_markup())
    elif post.text:
        await bot.send_message(CHANNEL_USERNAME, post.text, reply_markup=kb.as_markup())
    else:
        await bot.send_message(CHANNEL_USERNAME, "Post", reply_markup=kb.as_markup())

    await callback.message.answer("✅ Post kanalga yuborildi!")


# Ovoz berish
@dp.callback_query(F.data.startswith("vote:"))
async def vote_handler(callback: types.CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    data = posts.get(post_id)

    if not data:
        await callback.answer("Post topilmadi!", show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id in data["votes"]:
        await callback.answer("Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    data["votes"].add(user_id)
    count = len(data["votes"])
    emoji = data["sticker_emoji"]

    kb = InlineKeyboardBuilder()
    kb.button(text=f"{emoji} {count}", callback_data=f"vote:{post_id}")
    kb.adjust(1)

    await callback.message.edit_reply_markup(reply_markup=kb.as_markup())
    await callback.answer("Ovoz qabul qilindi! ✅")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


# hello world
