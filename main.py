import os
import random
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ========= CONFIG =========

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ADMIN_IDS = [7275042647, 1179613392]

IMAGE_URL = "https://i.imgur.com/70Q9M0d.jpeg"

participantes = {}
sorteo_abierto = False

# ========= BOTONES =========

def teclado_sorteo():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("𓈒. 𝗣𝗔𝗥𝗧𝗜𝗖𝗜𝗣𝗔𝗥 ๋", callback_data="participar")],
        [InlineKeyboardButton("⊹ 𝗦𝗢𝗥𝗧𝗘𝗔𝗥 ⋆", callback_data="sortear")],
    ])

def botones_resorteo():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⊹ 𝗦𝗢𝗥𝗧𝗘𝗔𝗥 ⋆", callback_data="resortear")],
    ])

def botones_admins():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🐰༘ 𝗖𝗔𝗧𝗔", url="tg://user?id=7275042647"),
            InlineKeyboardButton("🥟༘ 𝗖𝗔𝗧", url="tg://user?id=1179613392"),
        ]
    ])

# ========= COMANDO =========

async def sorteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global participantes, sorteo_abierto

    participantes.clear()
    sorteo_abierto = True

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE_URL,
        caption=(
            "◟₊ 𝓜𝗜𝗡𝗛𝗢𝗡𝗡𝗜𝗘 𝗦𝗢𝗥𝗧𝗘𝗢𝗦 ˚◞\n\n"
            "Presiona el botón para participar 💗"
        ),
        reply_markup=teclado_sorteo()
    )

# ========= CALLBACKS =========

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sorteo_abierto

    query = update.callback_query
    user = query.from_user
    await query.answer()

    chat_id = query.message.chat.id

    # PARTICIPAR
    if query.data == "participar":
        if not sorteo_abierto:
            await context.bot.send_message(chat_id, "⛔ El sorteo ya está cerrado")
            return

        if user.id in participantes:
            await context.bot.send_message(chat_id, "⚠️ Ya estás participando")
            return

        nombre = f"@{user.username}" if user.username else user.full_name
        participantes[user.id] = nombre

        await context.bot.send_message(
            chat_id,
            f"✅ {nombre} se unió al sorteo"
        )

    # SORTEAR / RESORTEAR
    elif query.data in ("sortear", "resortear"):
        if user.id not in ADMIN_IDS:
            await context.bot.send_message(chat_id, "⛔ Solo admins")
            return

        if not participantes:
            await context.bot.send_message(chat_id, "❌ No hay participantes")
            return

        sorteo_abierto = False

        await context.bot.send_message(
            chat_id,
            "🎲 𝗠𝗜𝗡 está eligiendo al ganador..."
        )

        await asyncio.sleep(3)

        ganador = random.choice(list(participantes.values()))

        await context.bot.send_message(
            chat_id,
            (
                "⋮ ¡ 𝐅𝐄𝐋𝐈𝐂𝐈𝐃𝐀𝐃𝐄𝐒 ⵑ ֹ ₊\n\n"
                f"✨ {ganador} ✨\n\n"
                "puedes acercarte con cualquiera de las dos para reclamar ‹3"
            ),
            reply_markup=botones_resorteo()
        )

# ========= APP =========

if not TOKEN:
    raise RuntimeError("❌ Falta la variable TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("sorteo", sorteo))
app.add_handler(CallbackQueryHandler(botones))

print("🤖 Bot de sorteos activo")
app.run_polling()
