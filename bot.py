import os
import sqlite3
import random
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================================================
# RJ TEAM BANGLADESH
# PREMIUM TEST / QA BOT
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "RJteam1").replace("@", "")

# Stored securely as an environment variable.
# This demo does not use it to collect third-party verification OTPs.
FIVESIM_API_KEY = os.getenv("FIVESIM_API_KEY", "")

PARTNER_USERNAME = "RjSabbir2024"

DB_NAME = "rj_test_otp.db"
BD = ZoneInfo("Asia/Dhaka")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# =========================================================
# PLATFORMS
# =========================================================

PLATFORMS = {
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "facebook": "Facebook",
    "tiktok": "TikTok",
    "apple": "Apple ID",
}

# =========================================================
# DATABASE
# =========================================================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            phone TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            phone TEXT,
            otp TEXT,
            created_at TEXT
        )
    """)

    con.commit()
    con.close()


def ensure_user(user):
    con = db()
    cur = con.cursor()

    now = datetime.now(BD).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user.id,
        user.username or "",
        user.first_name or "",
        now,
    ))

    cur.execute("""
        UPDATE users
        SET username = ?, first_name = ?
        WHERE user_id = ?
    """, (
        user.username or "",
        user.first_name or "",
        user.id,
    ))

    con.commit()
    con.close()


# =========================================================
# DEMO NUMBER / OTP
# =========================================================

def generate_test_number(platform):
    prefix = {
        "telegram": "99971",
        "whatsapp": "99972",
        "facebook": "99973",
        "tiktok": "99974",
        "apple": "99975",
    }.get(platform, "99970")

    return "+" + prefix + "".join(
        str(random.randint(0, 9))
        for _ in range(6)
    )


def generate_otp():
    return str(random.randint(100000, 999999))


def save_number(user_id, platform, phone):
    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO numbers
        (user_id, platform, phone, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        platform,
        phone,
        datetime.now(BD).strftime("%Y-%m-%d %H:%M:%S"),
    ))

    con.commit()
    con.close()


def save_otp(user_id, platform, phone, otp):
    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO otps
        (user_id, platform, phone, otp, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        platform,
        phone,
        otp,
        datetime.now(BD).strftime("%Y-%m-%d %H:%M:%S"),
    ))

    con.commit()
    con.close()


# =========================================================
# KEYBOARDS
# =========================================================

def home_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📱 Get Test Number",
                callback_data="number_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "🔐 Generate Test OTP",
                callback_data="otp_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 Profile",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                "📜 History",
                callback_data="history"
            ),
        ],
        [
            InlineKeyboardButton(
                "♻️ Recovery",
                callback_data="recovery"
            ),
            InlineKeyboardButton(
                "🗑 Delete",
                callback_data="delete"
            ),
        ],
        [
            InlineKeyboardButton(
                "👑 Owner",
                callback_data="owner"
            ),
            InlineKeyboardButton(
                "🤝 Partner",
                callback_data="partner"
            ),
        ],
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help"
            )
        ],
    ])


def platform_keyboard(mode):
    buttons = [
        InlineKeyboardButton(
            name,
            callback_data=f"{mode}:{key}"
        )
        for key, name in PLATFORMS.items()
    ]

    return InlineKeyboardMarkup([
        buttons[:2],
        buttons[2:4],
        buttons[4:],
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ],
    ])


# =========================================================
# START / MENU
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)

    text = (
        "🌟 <b>RJ TEAM BANGLADESH</b> 🌟\n\n"
        "💎 <b>PREMIUM TEST BOT</b>\n\n"
        "📱 Test Number\n"
        "🔐 Test OTP\n"
        "👤 Profile\n"
        "📜 History\n"
        "♻️ Recovery\n\n"
        "নিচের menu ব্যবহার করুন।"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=home_keyboard(),
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)

    await update.message.reply_text(
        "🏠 <b>RJ TEAM MAIN MENU</b>",
        parse_mode="HTML",
        reply_markup=home_keyboard(),
    )


# =========================================================
# NUMBER
# =========================================================

async def number_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📱 <b>TEST NUMBER MENU</b>\n\n"
        "Platform নির্বাচন করুন।\n\n"
        "⚠️ Demo/testing number only."
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=platform_keyboard("number"),
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=platform_keyboard("number"),
        )


async def number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await number_menu(update, context)


async def generate_number(update, context, platform):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    phone = generate_test_number(platform)

    save_number(
        user_id,
        platform,
        phone,
    )

    name = PLATFORMS[platform]

    await query.edit_message_text(
        "✅ <b>TEST NUMBER GENERATED</b>\n\n"
        f"📌 Platform: <b>{name}</b>\n"
        f"📞 Number: <code>{phone}</code>\n\n"
        "⚠️ এটি demo/testing number।",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔐 Generate Test OTP",
                    callback_data=f"otp:{platform}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 New Number",
                    callback_data=f"number:{platform}"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="number_menu"
                )
            ],
        ]),
    )


# =========================================================
# OTP
# =========================================================

async def otp_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔐 <b>TEST OTP MENU</b>\n\n"
        "Platform নির্বাচন করুন।\n"
        "Local demo OTP তৈরি হবে।"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=platform_keyboard("otp"),
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=platform_keyboard("otp"),
        )


async def otp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await otp_menu(update, context)


async def create_test_otp(update, context, platform):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT phone
        FROM numbers
        WHERE user_id = ? AND platform = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id, platform))

    row = cur.fetchone()
    con.close()

    if not row:
        await query.edit_message_text(
            "⚠️ আগে একটি test number তৈরি করুন।",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "📱 Generate Number",
                        callback_data=f"number:{platform}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="otp_menu"
                    )
                ],
            ]),
        )
        return

    phone = row[0]
    otp = generate_otp()

    save_otp(
        user_id,
        platform,
        phone,
        otp,
    )

    await query.edit_message_text(
        "🔐 <b>TEST OTP GENERATED</b>\n\n"
        f"📌 Platform: <b>{PLATFORMS[platform]}</b>\n"
        f"📞 Number: <code>{phone}</code>\n"
        f"🔢 Test OTP: <code>{otp}</code>\n\n"
        "⚠️ এটি local demo OTP।",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔄 New Test OTP",
                    callback_data=f"otp:{platform}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📜 History",
                    callback_data="history"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="otp_menu"
                )
            ],
        ]),
    )


# =========================================================
# PROFILE
# =========================================================

async def profile(update, context):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    ensure_user(user)

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM numbers WHERE user_id=?",
        (user.id,)
    )
    numbers = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM otps WHERE user_id=?",
        (user.id,)
    )
    otps = cur.fetchone()[0]

    con.close()

    username = f"@{user.username}" if user.username else "Not Set"

    await query.edit_message_text(
        "👤 <b>MY PROFILE</b>\n\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"👤 Username: <b>{username}</b>\n"
        f"📛 Name: <b>{user.first_name}</b>\n\n"
        f"📱 Test Numbers: <b>{numbers}</b>\n"
        f"🔐 Test OTPs: <b>{otps}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ]
        ]),
    )


async def profile_command(update, context):
    user = update.effective_user
    ensure_user(user)

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM numbers WHERE user_id=?",
        (user.id,)
    )
    numbers = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM otps WHERE user_id=?",
        (user.id,)
    )
    otps = cur.fetchone()[0]

    con.close()

    username = f"@{user.username}" if user.username else "Not Set"

    await update.message.reply_text(
        "👤 <b>MY PROFILE</b>\n\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"👤 Username: <b>{username}</b>\n"
        f"📛 Name: <b>{user.first_name}</b>\n\n"
        f"📱 Test Numbers: <b>{numbers}</b>\n"
        f"🔐 Test OTPs: <b>{otps}</b>",
        parse_mode="HTML",
    )


# =========================================================
# HISTORY
# =========================================================

def history_text(user_id):
    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT platform, phone, created_at
        FROM numbers
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))

    numbers = cur.fetchall()

    cur.execute("""
        SELECT platform, phone, otp, created_at
        FROM otps
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))

    otps = cur.fetchall()

    con.close()

    text = "📜 <b>HISTORY</b>\n\n"

    if numbers:
        text += "📱 <b>Numbers</b>\n"
        for platform, phone, created in numbers:
            text += (
                f"• {PLATFORMS.get(platform, platform)} "
                f"<code>{phone}</code>\n"
                f"  {created}\n"
            )
    else:
        text += "📱 No numbers yet.\n"

    text += "\n"

    if otps:
        text += "🔐 <b>Test OTPs</b>\n"
        for platform, phone, otp, created in otps:
            text += (
                f"• {PLATFORMS.get(platform, platform)}\n"
                f"  📞 <code>{phone}</code>\n"
                f"  🔢 <code>{otp}</code>\n"
                f"  {created}\n"
            )
    else:
        text += "🔐 No OTP yet."

    return text


async def history(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        history_text(update.effective_user.id),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ]
        ]),
    )


async def history_command(update, context):
    ensure_user(update.effective_user)

    await update.message.reply_text(
        history_text(update.effective_user.id),
        parse_mode="HTML",
    )


# =========================================================
# RECOVERY
# =========================================================

async def recovery(update, context):
    query = update.callback_query
    await query.answer()

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT platform, phone, otp, created_at
        FROM otps
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (update.effective_user.id,))

    row = cur.fetchone()
    con.close()

    if row:
        platform, phone, otp, created = row

        text = (
            "♻️ <b>LAST TEST OTP</b>\n\n"
            f"📌 Platform: <b>{PLATFORMS.get(platform, platform)}</b>\n"
            f"📞 Number: <code>{phone}</code>\n"
            f"🔢 OTP: <code>{otp}</code>\n"
            f"🕒 Time: <b>{created}</b>"
        )
    else:
        text = (
            "♻️ <b>RECOVERY</b>\n\n"
            "কোনো test OTP পাওয়া যায়নি।"
        )

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ]
        ]),
    )


async def recovery_command(update, context):
    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT platform, phone, otp, created_at
        FROM otps
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (update.effective_user.id,))

    row = cur.fetchone()
    con.close()

    if row:
        platform, phone, otp, created = row

        text = (
            "♻️ <b>LAST TEST OTP</b>\n\n"
            f"📌 Platform: <b>{PLATFORMS.get(platform, platform)}</b>\n"
            f"📞 Number: <code>{phone}</code>\n"
            f"🔢 OTP: <code>{otp}</code>\n"
            f"🕒 Time: <b>{created}</b>"
        )
    else:
        text = "♻️ <b>RECOVERY</b>\n\nNo test OTP found."

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


# =========================================================
# DELETE
# =========================================================

async def delete_confirm(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🗑 <b>DELETE DATA</b>\n\n"
        "আপনার সব test number এবং OTP history delete করবেন?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "❌ Delete All",
                    callback_data="delete_all"
                ),
                InlineKeyboardButton(
                    "↩️ Cancel",
                    callback_data="home"
                ),
            ]
        ]),
    )


async def delete_command(update, context):
    await update.message.reply_text(
        "🗑 <b>DELETE DATA</b>\n\n"
        "আপনার সব test data delete করবেন?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "❌ Delete All",
                    callback_data="delete_all"
                ),
                InlineKeyboardButton(
                    "↩️ Cancel",
                    callback_data="home"
                ),
            ]
        ]),
    )


async def delete_all(update, context):
    query = update.callback_query
    await query.answer()

    con = db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM numbers WHERE user_id=?",
        (update.effective_user.id,)
    )

    cur.execute(
        "DELETE FROM otps WHERE user_id=?",
        (update.effective_user.id,)
    )

    con.commit()
    con.close()

    await query.edit_message_text(
        "✅ <b>সব test data delete করা হয়েছে।</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🏠 Main Menu",
                    callback_data="home"
                )
            ]
        ]),
    )


# =========================================================
# OWNER / PARTNER
# =========================================================

async def owner(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "👑 <b>OWNER</b>\n\n"
        f"👤 Admin: <b>@{ADMIN_USERNAME}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "👤 Contact Owner",
                    url=f"https://t.me/{ADMIN_USERNAME}"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ],
        ]),
    )


async def owner_command(update, context):
    await update.message.reply_text(
        "👑 <b>OWNER</b>\n\n"
        f"👤 Admin: <b>@{ADMIN_USERNAME}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "👤 Contact Owner",
                    url=f"https://t.me/{ADMIN_USERNAME}"
                )
            ]
        ]),
    )


async def partner(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🤝 <b>PARTNER</b>\n\n"
        f"👤 Partner: <b>@{PARTNER_USERNAME}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🤝 Contact Partner",
                    url=f"https://t.me/{PARTNER_USERNAME}"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ],
        ]),
    )


async def partner_command(update, context):
    await update.message.reply_text(
        "🤝 <b>PARTNER</b>\n\n"
        f"👤 Partner: <b>@{PARTNER_USERNAME}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🤝 Contact Partner",
                    url=f"https://t.me/{PARTNER_USERNAME}"
                )
            ]
        ]),
    )


# =========================================================
# HELP
# =========================================================

async def help_command(update, context):
    await update.message.reply_text(
        "❓ <b>RJ TEAM HELP</b>\n\n"
        "/start - Start\n"
        "/menu - Main Menu\n"
        "/number - Test Number\n"
        "/otp - Test OTP\n"
        "/profile - Profile\n"
        "/history - History\n"
        "/recovery - Recovery\n"
        "/delete - Delete Data\n"
        "/owner - Owner\n"
        "/partner - Partner\n"
        "/help - Help\n\n"
        "⚠️ Test/demo system only.",
        parse_mode="HTML",
    )


# =========================================================
# CALLBACK
# =========================================================

async def callback_handler(update, context):
    query = update.callback_query
    data = query.data

    if data == "home":
        await query.answer()

        await query.edit_message_text(
            "🏠 <b>RJ TEAM MAIN MENU</b>",
            parse_mode="HTML",
            reply_markup=home_keyboard(),
        )

    elif data == "number_menu":
        await query.answer()
        await number_menu(update, context)

    elif data == "otp_menu":
        await query.answer()
        await otp_menu(update, context)

    elif data.startswith("number:"):
        platform = data.split(":", 1)[1]

        if platform in PLATFORMS:
            await generate_number(
                update,
                context,
                platform
            )

    elif data.startswith("otp:"):
        platform = data.split(":", 1)[1]

        if platform in PLATFORMS:
            await create_test_otp(
                update,
                context,
                platform
            )

    elif data == "profile":
        await profile(update, context)

    elif data == "history":
        await history(update, context)

    elif data == "recovery":
        await recovery(update, context)

    elif data == "delete":
        await delete_confirm(update, context)

    elif data == "delete_all":
        await delete_all(update, context)

    elif data == "owner":
        await owner(update, context)

    elif data == "partner":
        await partner(update, context)

    elif data == "help":
        await query.answer()

        await query.edit_message_text(
            "❓ <b>HELP</b>\n\n"
            "Available commands:\n"
            "/start\n"
            "/menu\n"
            "/number\n"
            "/otp\n"
            "/profile\n"
            "/history\n"
            "/recovery\n"
            "/delete\n"
            "/owner\n"
            "/partner\n"
            "/help",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="home"
                    )
                ]
            ]),
        )


# =========================================================
# ERROR
# =========================================================

async def error_handler(update, context):
    logger.error(
        "Bot error: %s",
        context.error,
        exc_info=True,
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable সেট করুন।"
        )

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("number", number_command))
    app.add_handler(CommandHandler("otp", otp_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("recovery", recovery_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("partner", partner_command))
    app.add_handler(CommandHandler("help", help_command))

    # Inline buttons
    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    app.add_error_handler(error_handler)

    print("================================")
    print(" RJ TEAM TEST BOT STARTED")
    print("================================")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
