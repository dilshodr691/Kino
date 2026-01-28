import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8537515265:AAFg11_8-asaB0FOg_P8KYdhrZEp2msKVjE"
ADMIN_ID = 6889938539

CHANNELS = [
    "@Qziqarli_kulguli_videolar",
    "@Kino_va_Multifilm_qodi"
]

INSTAGRAM_URL = "https://instagram.com/_kinolar.bot_"

USERS_FILE = "users.txt"
MOVIE_FILE = "movies.json"
MULTI_FILE = "multifilm.json"
# ================================================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ================= USERS TXT =================
def save_user_txt(user_id, username):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w", encoding="utf-8").close()

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = f.read().splitlines()

    line = f"{user_id}:{username}"
    if line not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

# ================= JSON =================
def load_json(file):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_next_code(data: dict):
    if not data:
        return "1"
    return str(max(map(int, data.keys())) + 1)

movies = load_json(MOVIE_FILE)
multis = load_json(MULTI_FILE)

# ================= OBUNA =================
async def check_subs(user_id):
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

# ================= XABAR YUBORISH =================
async def notify_users_new_content():
    if not os.path.exists(USERS_FILE):
        return

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = f.read().splitlines()

    for u in users:
        try:
            user_id = int(u.split(":")[0])
            await bot.send_message(
                user_id,
                "🎉 <b>Kanalga yangi kino va multifilmlar qo‘shildi!</b>\n\n"
                "👉 Kanalga kirib ko‘ring 👇\n"
                "https://t.me/Kino_va_Multifilm_qodi"
            )
        except:
            pass

# ================= TUGMALAR =================
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎬 Kinolar"), KeyboardButton(text="🧸 Multifilmlar")]
    ],
    resize_keyboard=True
)

sub_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 1-kanal", url="https://t.me/Qziqarli_kulguli_videolar")],
        [InlineKeyboardButton(text="📢 2-kanal", url="https://t.me/Kino_va_Multifilm_qodi")],
        [InlineKeyboardButton(text="📸 Instagram", url=INSTAGRAM_URL)],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")]
    ]
)

save_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kino", callback_data="save_movie"),
            InlineKeyboardButton(text="🧸 Multifilm", callback_data="save_multi")
        ]
    ]
)

user_mode = {}
pending_videos = {}

# ================= START =================
@dp.message(CommandStart())
async def start_cmd(message: Message):

    save_user_txt(
        message.from_user.id,
        message.from_user.username
    )

    await bot.send_message(
        ADMIN_ID,
        f"👤 Botga kirdi:\n"
        f"ID: {message.from_user.id}\n"
        f"@{message.from_user.username}"
    )

    if not await check_subs(message.from_user.id):
        await message.answer(
            "❌ Botdan foydalanish uchun obuna bo‘ling:",
            reply_markup=sub_kb
        )
        return

    await message.answer(
        "✅ <b>Obuna tasdiqlandi!</b>\n\n"
        "🎬 Kino va 🧸 multifilm kodlarini\n"
        "shu kanaldan olasiz 👇\n"
        "👉 https://t.me/Kino_va_Multifilm_qodi"
        "👇 Bo'limni tanlang:",
         reply_markup=menu_kb
    )

# ================= TEKSHIRISH =================
@dp.callback_query(F.data == "check")
async def recheck(call: CallbackQuery):
    if not await check_subs(call.from_user.id):
        await call.answer("❌ Kechirasz kanallarga obuna bo'lmagansz", show_alert=True)
        return

    await call.message.answer(
    "✅ <b>Obuna tasdiqlandi!</b>\n\n"
    "🎬 Kino va 🧸 multifilm kodlarini shu kanaldan olasiz 👇\n"
    "👉 https://t.me/Kino_va_Multifilm_qodi\n\n",
    reply_markup=menu_kb
)
# ================= BO‘LIM =================
@dp.message(F.text == "🎬 Kinolar")
async def movie_mode(message: Message):
    user_mode[message.from_user.id] = "movie"
    await message.answer("🎬 Kino <b>kodi yoki nomini</b> yuboring")

@dp.message(F.text == "🧸 Multifilmlar")
async def multi_mode(message: Message):
    user_mode[message.from_user.id] = "multi"
    await message.answer("🧸 Multifilm <b>kodi yoki nomini</b> yuboring")

# ================= ADMIN VIDEO =================
@dp.message(F.video)
async def admin_video(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    pending_videos[message.from_user.id] = message.video.file_id
    await message.answer("❓ Qaysi turga saqlaymiz?", reply_markup=save_choice_kb)

# ================= SAQLASH =================
@dp.callback_query(F.data.in_(["save_movie", "save_multi"]))
async def save_video(call: CallbackQuery):
    file_id = pending_videos.get(call.from_user.id)
    if not file_id:
        return

    if call.data == "save_movie":
        data, file = movies, MOVIE_FILE
    else:
        data, file = multis, MULTI_FILE

    code = get_next_code(data)

    data[code] = {
        "name": code,
        "file_id": file_id
    }
    save_json(file, data)
    pending_videos.pop(call.from_user.id, None)

    await call.message.edit_text("✅ Saqlandi!")
    await notify_users_new_content()

# ================= QIDIRISH =================
@dp.message(F.text)
async def search(message: Message):
    if not await check_subs(message.from_user.id):
        await message.answer("❌ Avval obuna bo‘ling", reply_markup=sub_kb)
        return

    mode = user_mode.get(message.from_user.id)
    if not mode:
        await message.answer("👇 Avval bo‘lim tanlang")
        return

    data = movies if mode == "movie" else multis
    q = message.text.lower()

    if q.isdigit() and q in data:
        await message.answer_video(
            video=data[q]["file_id"],
            caption=f"🎬 <b>{data[q]['name']}</b>"
        )
        return

    for v in data.values():
        if q in v["name"].lower():
            await message.answer_video(
                video=v["file_id"],
                caption=f"🎬 <b>{v['name']}</b>"
            )
            return

    await message.answer("❌ Hech narsa topilmadi")

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())   
