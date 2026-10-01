# ============================================================
# RJ TEAM - GOLD PREMIUM TEST OTP BOT
# SAFE DEMO / OWN-BACKEND OTP SYSTEM
# ============================================================

import os
import sqlite3
import random
import string
import logging
from datetime import datetime

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

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

OWNER = "@RJteam1"
PARTNER = "@RjSabbir2024"

REQUIRED_CHATS = [
    "https://t.me/+wmN83DGHfoVjMjE1",
    "https://t.me/iphonellc",
    "https://t.me/RJteam123890",
]

DB_NAME = "rj_test_otp.db"

PLATFORMS = {
    "telegram": "📱 Telegram",
    "whatsapp": "💬 WhatsApp",
    "facebook": "🔵 Facebook",
    "tiktok": "🎵 TikTok",
    "apple": "🍎 Apple ID",
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ============================================================
# DATABASE
# ============================================================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            used_numbers INTEGER DEFAULT 0,
            otp_received INTEGER DEFAULT 0,
            otp_shared INTEGER DEFAULT 0,
            orders INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            phone TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            number_id INTEGER,
            platform TEXT,
            phone TEXT,
            otp TEXT,
            shared INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    con.commit()
    con.close()


def ensure_user(user):
    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user.id,)
    )

    if not cur.fetchone():
        cur.execute(
            """
            INSERT INTO users
            (user_id, username)
            VALUES (?, ?)
            """,
            (
                user.id,
                user.username or "",
            )
        )

    con.commit()
    con.close()


# ============================================================
# HELPERS
# ============================================================

def gold(text):
    return f"✨ {text} ✨"


def generate_test_number():
    """
    Demo number only.
    This is NOT a real phone number source.
    """
    return "+999" + "".join(
        random.choice(string.digits)
        for _ in range(9)
    )


def generate_otp():
    return "".join(
        random.choice(string.digits)
        for _ in range(6)
    )


def save_number(user_id, platform, phone):
    con = db()
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO numbers
        (user_id, platform, phone, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            platform,
            phone,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    number_id = cur.lastrowid

    cur.execute(
        """
        UPDATE users
        SET used_numbers = used_numbers + 1
        WHERE user_id=?
        """,
        (user_id,)
    )

    con.commit()
    con.close()

    return number_id


def save_otp(user_id, number_id, platform, phone, otp):
    con = db()
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO otps
        (user_id, number_id, platform, phone, otp, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            number_id,
            platform,
            phone,
            otp,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    cur.execute(
        """
        UPDATE users
        SET otp_received = otp_received + 1
        WHERE user_id=?
        """,
        (user_id,)
    )

    con.commit()
    con.close()


# ============================================================
# KEYBOARDS
# ============================================================

def home_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📱 NUMBER",
                callback_data="numbers"
            ),
            InlineKeyboardButton(
                "🔐 OTP",
                callback_data="otp_menu"
            ),
        ],
        [
            InlineKeyboardButton(
                "👤 PROFILE",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                "📜 HISTORY",
                callback_data="history"
            ),
        ],
        [
            InlineKeyboardButton(
                "♻️ RECOVERY",
                callback_data="recovery"
            ),
        ],
        [
            InlineKeyboardButton(
                "👑 OWNER",
                callback_data="owner"
            ),
            InlineKeyboardButton(
                "🤝 PARTNER",
                callback_data="partner"
            ),
        ],
    ])


def platform_keyboard(prefix):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📱 Telegram",
                callback_data=f"{prefix}:telegram"
            ),
        ],
        [
            InlineKeyboardButton(
                "💬 WhatsApp",
                callback_data=f"{prefix}:whatsapp"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔵 Facebook",
                callback_data=f"{prefix}:facebook"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎵 TikTok",
                callback_data=f"{prefix}:tiktok"
            ),
        ],
        [
            InlineKeyboardButton(
                "🍎 Apple ID",
                callback_data=f"{prefix}:apple"
            ),
        ],
        [
            InlineKeyboardButton(
                "↩️ Back",
                callback_data="home"
            )
        ],
    ])


# ============================================================
# START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    ensure_user(user)

    text = f"""
╔══════════════════════════╗
      👑 RJ TEAM
   GOLD PREMIUM BOT
╚══════════════════════════╝

🔥 Welcome {user.first_name}!

এই Bot একটি নিজের/Testing OTP System।

📱 Number
🔐 Test OTP
👤 Profile
📜 History
♻️ Recovery

━━━━━━━━━━━━━━━━━━━━

⚠️ এই Bot কোনো তৃতীয়-পক্ষের
বাস্তব OTP সংগ্রহ করে না।
"""

    await update.message.reply_text(
        text,
        reply_markup=home_keyboard()
    )


# ============================================================
# NUMBER MENU
# ============================================================

async def number_menu(query):

    text = """
📱 NUMBER CENTER

আপনার Testing Platform নির্বাচন করুন:

নিচের Platform থেকে একটি নির্বাচন করুন।
"""

    await query.edit_message_text(
        text,
        reply_markup=platform_keyboard("number")
    )


# ============================================================
# GENERATE NUMBER
# ============================================================

async def generate_number(query, user_id, platform):

    phone = generate_test_number()

    number_id = save_number(
        user_id,
        platform,
        phone
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔄 REFRESH",
                callback_data=f"number:{platform}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔐 GET TEST OTP",
                callback_data=f"makeotp:{number_id}:{platform}"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ BACK",
                callback_data="numbers"
            )
        ],
    ])

    text = f"""
✨ GOLD NUMBER ✨

Platform:
{PLATFORMS[platform]}

📞 Test Number:
`{phone}`

━━━━━━━━━━━━━━━━━━

এই নম্বরটি শুধুমাত্র Demo/Test
সিস্টেমের জন্য।

বাস্তব WhatsApp / Facebook /
Telegram / TikTok / Apple account
verification-এর জন্য নয়।
"""

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
# CREATE TEST OTP
# ============================================================

async def create_test_otp(query, user_id, number_id, platform):

    con = db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT phone
        FROM numbers
        WHERE id=? AND user_id=?
        """,
        (number_id, user_id)
    )

    row = cur.fetchone()
    con.close()

    if not row:
        await query.answer(
            "Number পাওয়া যায়নি!",
            show_alert=True
        )
        return

    phone = row[0]

    otp = generate_otp()

    save_otp(
        user_id,
        number_id,
        platform,
        phone,
        otp
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 SHARE",
                callback_data=f"share:{number_id}:{platform}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 NEW OTP",
                callback_data=f"makeotp:{number_id}:{platform}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔐 OTP MENU",
                callback_data="otp_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ BACK",
                callback_data="numbers"
            )
        ],
    ])

    text = f"""
🔐 TEST OTP

Platform:
{PLATFORMS[platform]}

📞 Number:
`{phone}`

━━━━━━━━━━━━━━━━━━

🔑 TEST OTP:
`{otp}`

━━━━━━━━━━━━━━━━━━

⚠️ এটি আপনার নিজের Bot-এর
generated TEST OTP।

কোনো external service-এর
real verification code নয়।
"""

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
# OTP MENU
# ============================================================

async def otp_menu(query):

    text = """
🔐 OTP CENTER

কোন Platform-এর নিজের Test OTP
দেখতে চান?
"""

    await query.edit_message_text(
        text,
        reply_markup=platform_keyboard("otp")
    )


# ============================================================
# SHOW OTP HISTORY BY PLATFORM
# ============================================================

async def show_platform_otps(query, user_id, platform):

    con = db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT phone, otp, created_at, shared
        FROM otps
        WHERE user_id=? AND platform=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (user_id, platform)
    )

    rows = cur.fetchall()
    con.close()

    text = f"""
🔐 {PLATFORMS[platform]} TEST OTP

━━━━━━━━━━━━━━━━━━
"""

    if not rows:
        text += "\nকোনো Test OTP নেই।\n"
    else:
        for i, row in enumerate(rows, 1):

            phone, otp, created, shared = row

            text += (
                f"\n#{i}\n"
                f"📞 {phone}\n"
                f"🔑 `{otp}`\n"
                f"🕐 {created}\n"
                f"📤 Shared: {'Yes' if shared else 'No'}\n"
                f"━━━━━━━━━━━━\n"
            )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data=f"otp:{platform}"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ Back",
                callback_data="otp_menu"
            )
        ],
    ])

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
# PROFILE
# ============================================================

async def profile(query, user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT
        used_numbers,
        otp_received,
        otp_shared,
        orders
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    row = cur.fetchone()
    con.close()

    if not row:
        values = (0, 0, 0, 0)
    else:
        values = row

    text = f"""
╔══════════════════════╗
        👤 PROFILE
╚══════════════════════╝

📱 Number Used:
{values[0]}

🔐 OTP Received:
{values[1]}

📤 OTP Shared:
{values[2]}

📦 Orders:
{values[3]}

━━━━━━━━━━━━━━━━━━

⚠️ Statistics are for this
Bot's own test system.
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🗑️ DELETE DATA",
                callback_data="delete_confirm"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 HISTORY",
                callback_data="history"
            )
        ],
        [
            InlineKeyboardButton(
                "♻️ RECOVERY",
                callback_data="recovery"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ BACK",
                callback_data="home"
            )
        ],
    ])

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


# ============================================================
# HISTORY
# ============================================================

async def history(query, user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT platform, phone, otp, created_at
        FROM otps
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 15
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    con.close()

    text = """
📜 OTP HISTORY

━━━━━━━━━━━━━━━━━━
"""

    if not rows:
        text += "\nকোনো History নেই।"
    else:

        for i, row in enumerate(rows, 1):

            platform, phone, otp, created = row

            text += (
                f"\n{i}. {PLATFORMS.get(platform, platform)}\n"
                f"📞 {phone}\n"
                f"🔑 `{otp}`\n"
                f"🕐 {created}\n"
                f"━━━━━━━━━━━━\n"
            )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "↩️ BACK",
                callback_data="home"
            )
        ]
    ])

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
# RECOVERY
# ============================================================

async def recovery(query, user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT platform, phone, created_at
        FROM numbers
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 15
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    con.close()

    text = """
♻️ RECOVERY CENTER

আপনার সাম্প্রতিক Test Numbers:

━━━━━━━━━━━━━━━━━━
"""

    if not rows:
        text += "\nকোনো Recovery data নেই।"
    else:

        for i, row in enumerate(rows, 1):

            platform, phone, created = row

            text += (
                f"\n{i}. {PLATFORMS.get(platform, platform)}\n"
                f"📞 {phone}\n"
                f"🕐 {created}\n"
            )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "↩️ BACK",
                callback_data="home"
            )
        ]
    ])

    await query.edit_message_text(
        text,
        reply_markup=keyboard
    )


# ============================================================
# DELETE
# ============================================================

async def delete_confirm(query):

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❌ YES, DELETE",
                callback_data="delete_all"
            ),
            InlineKeyboardButton(
                "↩️ NO",
                callback_data="profile"
            ),
        ]
    ])

    await query.edit_message_text(
        """
⚠️ DELETE CONFIRMATION

আপনার Bot-এর test data মুছে ফেলবেন?

এই action-এর পরে recovery
থেকে আগের data আর পাওয়া যাবে না।
""",
        reply_markup=keyboard
    )


async def delete_all(query, user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM otps WHERE user_id=?",
        (user_id,)
    )

    cur.execute(
        "DELETE FROM numbers WHERE user_id=?",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE users
        SET
        used_numbers=0,
        otp_received=0,
        otp_shared=0,
        orders=0
        WHERE user_id=?
        """,
        (user_id,)
    )

    con.commit()
    con.close()

    await query.edit_message_text(
        "✅ আপনার Test data delete হয়েছে।",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🏠 HOME",
                    callback_data="home"
                )
            ]
        ])
    )


# ============================================================
# OWNER
# ============================================================

async def owner(query):

    await query.edit_message_text(
        f"""
👑 OWNER

{OWNER}

━━━━━━━━━━━━━━━━━━

RJ TEAM Official Owner
""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "↩️ BACK",
                    callback_data="home"
                )
            ]
        ])
    )


# ============================================================
# PARTNER
# ============================================================

async def partner(query):

    await query.edit_message_text(
        f"""
🤝 PARTNER

{PARTNER}

━━━━━━━━━━━━━━━━━━

RJ TEAM Partner
""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "↩️ BACK",
                    callback_data="home"
                )
            ]
        ])
    )


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = update.effective_user
    ensure_user(user)

    data = query.data

    # HOME
    if data == "home":

        await query.edit_message_text(
            """
╔══════════════════════════╗
      👑 RJ TEAM
   GOLD PREMIUM BOT
╚══════════════════════════╝

🔥 Main Menu
""",
            reply_markup=home_keyboard()
        )

    # NUMBER
    elif data == "numbers":

        await number_menu(query)

    # OTP MENU
    elif data == "otp_menu":

        await otp_menu(query)

    # PROFILE
    elif data == "profile":

        await profile(
            query,
            user.id
        )

    # HISTORY
    elif data == "history":

        await history(
            query,
            user.id
        )

    # RECOVERY
    elif data == "recovery":

        await recovery(
            query,
            user.id
        )

    # OWNER
    elif data == "owner":

        await owner(query)

    # PARTNER
    elif data == "partner":

        await partner(query)

    # DELETE CONFIRM
    elif data == "delete_confirm":

        await delete_confirm(query)

    # DELETE
    elif data == "delete_all":

        await delete_all(
            query,
            user.id
        )

    # NUMBER PLATFORM
    elif data.startswith("number:"):

        platform = data.split(":")[1]

        if platform not in PLATFORMS:
            return

        await generate_number(
            query,
            user.id,
            platform
        )

    # OTP PLATFORM
    elif data.startswith("otp:"):

        platform = data.split(":")[1]

        if platform not in PLATFORMS:
            return

        await show_platform_otps(
            query,
            user.id,
            platform
        )

    # CREATE OTP
    elif data.startswith("makeotp:"):

        parts = data.split(":")

        number_id = int(parts[1])
        platform = parts[2]

        await create_test_otp(
            query,
            user.id,
            number_id,
            platform
        )

    # SHARE
    elif data.startswith("share:"):

        parts = data.split(":")

        number_id = int(parts[1])
        platform = parts[2]

        con = db()
        cur = con.cursor()

        cur.execute(
            """
            SELECT otp
            FROM otps
            WHERE
            user_id=?
            AND number_id=?
            AND platform=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user.id,
                number_id,
                platform
            )
        )

        row = cur.fetchone()

        if row:

            cur.execute(
                """
                UPDATE otps
                SET shared=1
                WHERE
                user_id=?
                AND number_id=?
                AND platform=?
                """,
                (
                    user.id,
                    number_id,
                    platform
                )
            )

            cur.execute(
                """
                UPDATE users
                SET otp_shared=otp_shared+1
                WHERE user_id=?
                """,
                (user.id,)
            )

            con.commit()

        con.close()

        if row:

            await query.message.reply_text(
                f"""
📤 SHARE TEST OTP

{PLATFORMS[platform]}

🔐 Test OTP:
`{row[0]}`

⚠️ এটি শুধুমাত্র নিজের
Demo/Test OTP।
""",
                parse_mode="Markdown"
            )

            await query.answer(
                "Test OTP share করা হয়েছে!"
            )

        else:

            await query.answer(
                "কোনো OTP পাওয়া যায়নি!",
                show_alert=True
            )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logging.error(
        "Bot Error: %s",
        context.error
    )


# ============================================================
# MAIN
# ============================================================

def main():

    init_db()

    if BOT_TOKEN == "YOUR_BOT_TOKEN":

        print(
            "ERROR: BOT_TOKEN সেট করুন।"
        )
        return

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    app.add_error_handler(
        error_handler
    )

    print(
        "RJ TEAM GOLD TEST OTP BOT STARTED..."
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
