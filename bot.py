from flask import Flask
import json
import os
import random
import re
import threading
import telebot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# --- CONFIGURATION & INITIALIZATION ---
TOKEN = os.getenv("BOT_TOKEN", "8313028390:AAGNsfFVZpBQ16vU5Tx6NZxQ9NMUzqHbPlk")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running live 24/7!"


def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


DB_FILE = "users_db.json"
db_lock = threading.Lock()

# --- DYNAMIC ADMIN SYSTEM CONFIGURATION ---
MAIN_ADMIN_ID = 1908832842  # आपकी मुख्य Admin ID
ADMINS_FILE = "admins_db.json"


def load_admins():
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "w") as f:
            json.dump([MAIN_ADMIN_ID], f)
        return [MAIN_ADMIN_ID]
    try:
        with open(ADMINS_FILE, "r") as f:
            data = json.load(f)
            if MAIN_ADMIN_ID not in data:
                data.append(MAIN_ADMIN_ID)
            return data
    except Exception:
        return [MAIN_ADMIN_ID]


def save_admins(admins_list):
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins_list, f)


def is_admin(user_id):
    admins = load_admins()
    return int(user_id) in [int(x) for x in admins]


def is_main_admin(user_id):
    return int(user_id) == MAIN_ADMIN_ID


DEFAULT_SETTINGS = {
    "users": [],
    "maintenance": False,
    "welcome_photo": "https://placehold.co/600x400/png",
    "welcome_caption": (
        "🎉 <b>Welcome to Profit Masters!</b>\n\n"
        "🎁 Your signup bonus is ready.\n"
        "👇 Join channels and click verify."
    ),
    "free_code_btn_text": "🎁 Get My Free Code",
    "broadcast_btn_text": "👉 Register Now",
    "verification_delay_enabled": True,
    "verification_text": "⏳ Processing your request... Please wait 5 seconds.",
    "error_text": (
        "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
        "Kripaya upar दिए गए channels join karein.\n\n"
        "📌 <b>Zaruri:</b> Channels ko Pin karke rakho, tabhi code milega!"
    ),
    "custom_buttons": [
        {"text": "🚀 Claim ₹500", "url": "https://t.me/telegram"},
        {"text": "🎁 Unlock Code", "url": "https://t.me/telegram"},
    ],
    "channels": ["@ch1", "@ch2"],
    "broadcast_links": {},
}


def load_system_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for key in DEFAULT_SETTINGS:
                    if key not in data:
                        data[key] = DEFAULT_SETTINGS[key]
                return data
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_system_data(data):
    with db_lock:
        try:
            data_copy = data.copy()
            if "users" in data_copy:
                if isinstance(data_copy["users"], set):
                    data_copy["users"] = list(data_copy["users"])
                elif not isinstance(data_copy["users"], list):
                    data_copy["users"] = []
            with open(DB_FILE, "w") as f:
                json.dump(data_copy, f, indent=4)
        except Exception as e:
            print(f"Database save error: {e}")


sys_db = load_system_data()

if "users" not in sys_db or not isinstance(sys_db["users"], (list, set)):
    sys_db["users"] = set()
else:
    sys_db["users"] = set(sys_db["users"])

if "broadcast_links" not in sys_db:
    sys_db["broadcast_links"] = {}


def save_user_to_db(user_id):
    try:
        if not isinstance(sys_db["users"], set):
            sys_db["users"] = set(sys_db["users"])
        if user_id not in sys_db["users"]:
            sys_db["users"].add(user_id)
            save_system_data(sys_db)
    except Exception as e:
        print(f"User registration error: {e}")


STATE_NONE = "NONE"
STATE_EDIT_PHOTO = "EDIT_PHOTO"
STATE_EDIT_CAPTION = "EDIT_CAPTION"
STATE_ADD_BTN_NAME = "ADD_BTN_NAME"
STATE_ADD_BTN_URL = "ADD_BTN_URL"
STATE_EDIT_BTN_TEXT = "EDIT_BTN_TEXT"
STATE_EDIT_BTN_URL = "EDIT_BTN_URL"
STATE_EDIT_FREE_BTN = "EDIT_FREE_BTN"
STATE_EDIT_BROADCAST_BTN = "EDIT_BROADCAST_BTN"
STATE_EDIT_VERIFY_TEXT = "EDIT_VERIFY_TEXT"
STATE_EDIT_ERROR_TEXT = "EDIT_ERROR_TEXT"
STATE_UPDATE_CHANNELS = "UPDATE_CHANNELS"
STATE_FORWARD_BROADCAST = "FORWARD_BROADCAST"
STATE_COPY_BROADCAST = "COPY_BROADCAST"

admin_states = {}
temp_btn_data = {}
target_edit_index = {}  # एडिट करने वाले बटन का इंडेक्स याद रखने के लिए


def check_user_joined_all(user_id):
    if not sys_db["channels"]:
        return True
    for channel in sys_db["channels"]:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True


def get_admin_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📊 Analytics & Stats"),
        KeyboardButton("⚙️ Default Configuration Settings"),
        KeyboardButton("⏩ Forward Broadcast"),
        KeyboardButton("📝 Copy Broadcast"),
        KeyboardButton("📸 Change Photo"),
        KeyboardButton("✍️ Change Caption"),
        KeyboardButton("+ Add Welcome Button"),
        KeyboardButton("📝 Edit Button Text"),
        KeyboardButton("🔗 Edit Button URL"),
        KeyboardButton("- Remove Welcome Button"),
        KeyboardButton("📝 Edit Free Code Btn Text"),
        KeyboardButton("📝 Broadcast Button Text"),
        KeyboardButton("🔗 Update Channels"),
        KeyboardButton("🎚️ Maintenance Mode"),
        KeyboardButton("🔄 Reset All Link Tracking Data"),
    )
    delay_status = (
        "🟢 Delay Status: ON"
        if sys_db.get("verification_delay_enabled", True)
        else "🔴 Delay Status: OFF"
    )
    markup.add(
        KeyboardButton(delay_status),
        KeyboardButton("⏳ Edit Verification Text"),
        KeyboardButton("📝 Edit Join Error Text"),
        KeyboardButton("📥 Export Users Data"),
    )
    return markup


def extract_first_link(text):
    if not text:
        return None
    urls = re.findall(r"(https?://\S+|t\.me/\S+)", text)
    return urls[0] if urls else None


# --- DYNAMIC ADMIN MANAGEMENT COMMANDS ---
@bot.message_handler(commands=["addadmin"])
def add_admin_command(message):
    if not is_main_admin(message.from_user.id):
        bot.reply_to(message, "❌ यह कमांड केवल Main Admin इस्तेमाल कर सकता है!")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(
                message,
                "⚠️ सही तरीका: `/addadmin <Telegram_User_ID>`",
                parse_mode="Markdown",
            )
            return

        new_admin_id = int(args[1])
        admins = load_admins()

        if new_admin_id in admins:
            bot.reply_to(
                message,
                f"ℹ️ Telegram ID `{new_admin_id}` पहले से एडमिन है।",
                parse_mode="Markdown",
            )
        else:
            admins.append(new_admin_id)
            save_admins(admins)
            bot.reply_to(
                message,
                f"✅ Telegram ID `{new_admin_id}` को सफलतापूर्वक Admin बना दिया गया है!",
                parse_mode="Markdown",
            )

    except ValueError:
        bot.reply_to(message, "❌ अमान्य User ID!")


@bot.message_handler(commands=["removeadmin"])
def remove_admin_command(message):
    if not is_main_admin(message.from_user.id):
        bot.reply_to(message, "❌ यह कमांड केवल Main Admin इस्तेमाल कर सकता है!")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(
                message,
                "⚠️ सही तरीका: `/removeadmin <Telegram_User_ID>`",
                parse_mode="Markdown",
            )
            return

        target_id = int(args[1])
        if target_id == MAIN_ADMIN_ID:
            bot.reply_to(
                message, "❌ आप खुद (Main Admin) को एडमिन सूची से नहीं हटा सकते!"
            )
            return

        admins = load_admins()
        if target_id in admins:
            admins.remove(target_id)
            save_admins(admins)
            bot.reply_to(
                message,
                f"🗑️ Telegram ID `{target_id}` को Admin पद से हटा दिया गया है।",
                parse_mode="Markdown",
            )
        else:
            bot.reply_to(
                message,
                f"ℹ️ Telegram ID `{target_id}` एडमिन लिस्ट में नहीं है।",
                parse_mode="Markdown",
            )

    except ValueError:
        bot.reply_to(message, "❌ अमान्य User ID!")


@bot.message_handler(commands=["adminlist"])
def list_admins_command(message):
    if not is_admin(message.from_user.id):
        return

    admins = load_admins()
    text = "👮‍♂️ **Admins List:**\n\n"
    for idx, admin_id in enumerate(admins, 1):
        if admin_id == MAIN_ADMIN_ID:
            text += f"{idx}. `{admin_id}` (👑 Main Admin)\n"
        else:
            text += f"{idx}. `{admin_id}`\n"

    bot.reply_to(message, text, parse_mode="Markdown")


# --- USER COMMANDS & HANDLERS ---
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    save_user_to_db(user_id)

    if sys_db.get("maintenance", False) and not is_admin(user_id):
        bot.send_message(
            message.chat.id,
            "🚧 <b>Bot is currently under maintenance. Please try again later.</b>",
            parse_mode="HTML",
        )
        return

    markup = InlineKeyboardMarkup(row_width=2)
    btns_list = [
        InlineKeyboardButton(text=btn["text"], url=btn["url"])
        for btn in sys_db["custom_buttons"]
    ]
    for i in range(0, len(btns_list), 2):
        markup.row(*btns_list[i : i + 2])

    markup.add(
        InlineKeyboardButton(
            text=sys_db["free_code_btn_text"], callback_data="get_free_code"
        )
    )

    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=sys_db["welcome_photo"],
            caption=sys_db["welcome_caption"],
            parse_mode="HTML",
            reply_markup=markup,
        )
    except Exception:
        bot.send_message(
            chat_id=message.chat.id,
            text=sys_db["welcome_caption"],
            parse_mode="HTML",
            reply_markup=markup,
        )


@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return
    admin_states[message.from_user.id] = STATE_NONE
    bot.send_message(
        message.chat.id,
        "🛠 *Profit Masters Administrative Control Console:*",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data == "get_free_code")
def handle_reward_claim(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if sys_db.get("verification_delay_enabled", True):
        status_msg = bot.send_message(
            chat_id, sys_db.get("verification_text", "⏳ Processing...")
        )

        def process_verification_with_delay():
            if not check_user_joined_all(user_id):
                try:
                    bot.delete_message(chat_id, status_msg.message_id)
                except Exception:
                    pass
                error_msg = sys_db.get(
                    "error_text", "<b>⚠️ Aapne Join Nahi Kiya!</b>"
                )
                bot.send_message(chat_id, error_msg, parse_mode="HTML")
                return

            generated_code = f"IW7-PROMO-{random.randint(100000, 999999)}"
            try:
                bot.delete_message(chat_id, status_msg.message_id)
            except Exception:
                pass
            bot.send_message(
                chat_id,
                f"🎁 <b>Verification Successful!</b>\n\n🔑 Your Code:"
                f" <code>{generated_code}</code>",
                parse_mode="HTML",
            )

        threading.Timer(5.0, process_verification_with_delay).start()

    else:
        if not check_user_joined_all(user_id):
            error_msg = sys_db.get(
                "error_text", "<b>⚠️ Aapne Join Nahi Kiya!</b>"
            )
            bot.send_message(chat_id, error_msg, parse_mode="HTML")
            return

        generated_code = f"IW7-PROMO-{random.randint(100000, 999999)}"
        bot.send_message(
            chat_id,
            f"🎁 <b>Verification Successful!</b>\n\n🔑 Your Code:"
            f" <code>{generated_code}</code>",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("track_lnk_"))
def handle_tracked_link_clicks(call):
    link_id = call.data.replace("track_lnk_", "")
    if link_id in sys_db.get("broadcast_links", {}):
        sys_db["broadcast_links"][link_id]["clicks"] += 1
        save_system_data(sys_db)
        target_url = sys_db["broadcast_links"][link_id]["url"]

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Open Link", url=target_url))
        bot.send_message(
            call.message.chat.id,
            f"👉 Click below to open your link:\n{target_url}",
            reply_markup=markup,
        )
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(
            call.id,
            "⚠️ Link configuration error or expired link data.",
            show_alert=True,
        )


# --- INLINE CALLBACK HANDLERS FOR EDITING & DELETING BUTTONS ---
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("sel_edit_txt_")
)
def handle_select_edit_text(call):
    idx = int(call.data.replace("sel_edit_txt_", ""))
    user_id = call.from_user.id
    target_edit_index[user_id] = idx
    admin_states[user_id] = STATE_EDIT_BTN_TEXT
    bot.send_message(call.message.chat.id, f"📥 Send new button text:")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("sel_edit_url_")
)
def handle_select_edit_url(call):
    idx = int(call.data.replace("sel_edit_url_", ""))
    user_id = call.from_user.id
    target_edit_index[user_id] = idx
    admin_states[user_id] = STATE_EDIT_BTN_URL
    bot.send_message(call.message.chat.id, f"📥 Send new button URL:")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("del_btn_"))
def handle_delete_button(call):
    idx = int(call.data.replace("del_btn_", ""))
    if 0 <= idx < len(sys_db["custom_buttons"]):
        removed = sys_db["custom_buttons"].pop(idx)
        save_system_data(sys_db)
        bot.send_message(
            call.message.chat.id,
            f"🗑️ Removed button: {removed['text']}",
        )
    bot.answer_callback_query(call.id)


# --- ADMIN INPUTS HANDLER ---
@bot.message_handler(
    func=lambda message: is_admin(message.from_user.id),
    content_types=["text", "photo", "video", "document", "animation"],
)
def handle_admin_inputs(message):
    user_id = message.from_user.id
    text = message.text if message.content_type == "text" else ""
    state = admin_states.get(user_id, STATE_NONE)

    if text == "🎚️ Maintenance Mode":
        sys_db["maintenance"] = not sys_db["maintenance"]
        save_system_data(sys_db)
        status = "ENABLED 🛑" if sys_db["maintenance"] else "DISABLED 🟢"
        bot.send_message(
            message.chat.id,
            f"✅ Maintenance Mode is now {status}",
            reply_markup=get_admin_keyboard(),
        )
        return

    elif text.startswith("🟢 Delay Status:") or text.startswith(
        "🔴 Delay Status:"
    ):
        sys_db["verification_delay_enabled"] = not sys_db[
            "verification_delay_enabled"
        ]
        save_system_data(sys_db)
        status = (
            "ENABLED 🟢"
            if sys_db["verification_delay_enabled"]
            else "DISABLED 🔴"
        )
        bot.send_message(
            message.chat.id,
            f"✅ Verification Delay is now {status}.",
            reply_markup=get_admin_keyboard(),
        )
        return

    elif text == "⚙️ Default Configuration Settings":
        channels_str = (
            ", ".join(sys_db["channels"]) if sys_db["channels"] else "None"
        )
        delay_status_str = (
            "ON 🟢" if sys_db["verification_delay_enabled"] else "OFF 🔴"
        )
        m_status_str = "ON 🛑" if sys_db["maintenance"] else "OFF 🟢"

        config_text = (
            "⚙️ <b>Current System Configuration Master Matrix:</b>\n\n"
            f"🛠 <b>Maintenance Mode:</b> <code>{m_status_str}</code>\n"
            f"⏳ <b>Delay Status:</b> <code>{delay_status_str}</code>\n"
            f"📝 <b>Loader String:</b>"
            f" <code>{sys_db['verification_text']}</code>\n"
            f"🎁 <b>Free Code Text:</b>"
            f" <code>{sys_db['free_code_btn_text']}</code>\n"
            f"📢 <b>Authentication Channels:</b>"
            f" <code>{channels_str}</code>\n"
            f"🖼 <b>Welcome Photo URL:</b>"
            f" <code>{sys_db['welcome_photo']}</code>\n"
            f"👥 <b>Total Custom Buttons:</b>"
            f" <code>{len(sys_db['custom_buttons'])}</code>"
        )
        bot.send_message(message.chat.id, config_text, parse_mode="HTML")
        return

    elif text == "+ Add Welcome Button":
        admin_states[user_id] = STATE_ADD_BTN_NAME
        bot.send_message(
            message.chat.id, "📥 Send the button text (e.g., 🚀 Join Channel):"
        )
        return

    elif text == "📝 Edit Button Text":
        if not sys_db["custom_buttons"]:
            bot.send_message(
                message.chat.id, "❌ No buttons available to edit."
            )
            return
        markup = InlineKeyboardMarkup()
        for idx, btn in enumerate(sys_db["custom_buttons"]):
            markup.add(
                InlineKeyboardButton(
                    f"✏️ {btn['text']}", callback_data=f"sel_edit_txt_{idx}"
                )
            )
        bot.send_message(
            message.chat.id,
            "Select a button to change its text string:",
            reply_markup=markup,
        )
        return

    elif text == "🔗 Edit Button URL":
        if not sys_db["custom_buttons"]:
            bot.send_message(
                message.chat.id, "❌ No buttons available to edit."
            )
            return
        markup = InlineKeyboardMarkup()
        for idx, btn in enumerate(sys_db["custom_buttons"]):
            markup.add(
                InlineKeyboardButton(
                    f"🔗 {btn['text']}", callback_data=f"sel_edit_url_{idx}"
                )
            )
        bot.send_message(
            message.chat.id,
            "Select a button to change its Target URL link:",
            reply_markup=markup,
        )
        return

    elif text == "- Remove Welcome Button":
        if not sys_db["custom_buttons"]:
            bot.send_message(message.chat.id, "❌ No buttons to remove.")
            return
        markup = InlineKeyboardMarkup()
        for idx, btn in enumerate(sys_db["custom_buttons"]):
            markup.add(
                InlineKeyboardButton(
                    f"❌ {btn['text']}", callback_data=f"del_btn_{idx}"
                )
            )
        bot.send_message(
            message.chat.id,
            "Select a button to delete permanently:",
            reply_markup=markup,
        )
        return

    elif text == "📝 Edit Free Code Btn Text":
        admin_states[user_id] = STATE_EDIT_FREE_BTN
        bot.send_message(
            message.chat.id,
            f"📥 Send new Free Code button text:\n<b>Current:</b>"
            f" <code>{sys_db.get('free_code_btn_text')}</code>",
            parse_mode="HTML",
        )
        return

    elif text == "📝 Broadcast Button Text":
        admin_states[user_id] = STATE_EDIT_BROADCAST_BTN
        bot.send_message(
            message.chat.id,
            f"📥 Send new Broadcast button text:\n<b>Current:</b>"
            f" <code>{sys_db.get('broadcast_btn_text')}</code>",
            parse_mode="HTML",
        )
        return

    elif text == "⏳ Edit Verification Text":
        admin_states[user_id] = STATE_EDIT_VERIFY_TEXT
        bot.send_message(
            message.chat.id,
            f"📥 Send me the new text loader string:\n\n<b>Current:</b>"
            f" <code>{sys_db.get('verification_text')}</code>",
            parse_mode="HTML",
        )
        return

    elif text == "📝 Edit Join Error Text":
        admin_states[user_id] = STATE_EDIT_ERROR_TEXT
        bot.send_message(
            message.chat.id,
            f"📥 Send me the new HTML Join Error text:\n\n<b>Current:</b>\n{sys_db.get('error_text', 'None')}",
            parse_mode="HTML",
        )
        return

    elif text == "📥 Export Users Data":
        total_users = len(sys_db["users"])
        if total_users == 0:
            bot.send_message(
                message.chat.id, "❌ Database me abhi koi user nahi hai."
            )
            return

        file_name = "profit_masters_users.txt"
        with open(file_name, "w") as f:
            for uid in sys_db["users"]:
                f.write(f"{uid}\n")

        with open(file_name, "rb") as f:
            bot.send_document(
                chat_id=message.chat.id,
                document=f,
                caption=(
                    "📊 <b>Profit Masters User Database Backup</b>\n\n👥 Total"
                    f" Unique Users: <code>{total_users}</code>"
                ),
                parse_mode="HTML",
            )
        os.remove(file_name)
        return

    elif text == "⏩ Forward Broadcast":
        admin_states[user_id] = STATE_FORWARD_BROADCAST
        bot.send_message(
            message.chat.id, "📢 Send or forward any message now:"
        )
        return

    elif text == "📝 Copy Broadcast":
        admin_states[user_id] = STATE_COPY_BROADCAST
        bot.send_message(
            message.chat.id, "📢 Send or forward any message now:"
        )
        return

    elif text == "📸 Change Photo":
        admin_states[user_id] = STATE_EDIT_PHOTO
        bot.send_message(message.chat.id, "📥 Send me the new photo URL:")
        return

    elif text == "✍️ Change Caption":
        admin_states[user_id] = STATE_EDIT_CAPTION
        bot.send_message(message.chat.id, "📥 Send me the new HTML caption:")
        return

    elif text == "📊 Analytics & Stats":
        report_str = (
            "📊 <b>Core Analytics & Broadcast Links Tracker Node:</b>\n\n"
        )
        report_str += (
            f"👥 Total Unique Users: <code>{len(sys_db['users'])}</code>\n"
        )
        report_str += "───────────────────\n"
        report_str += "🔗 <b>Live Broadcast Link Clicks:</b>\n"

        tracked_links = sys_db.get("broadcast_links", {})
        if not tracked_links:
            report_str += "<i>Abhi koi links data tracked nahi h.</i>"
        else:
            for l_id, info in list(tracked_links.items())[-15:]:
                report_str += (
                    f"📍 <code>{info['url'][:30]}...</code> ➜"
                    f" <b>{info['clicks']} Clicks</b>\n"
                )

        bot.send_message(message.chat.id, report_str, parse_mode="HTML")
        return

    elif text == "🔄 Reset All Link Tracking Data":
        sys_db["broadcast_links"] = {}
        save_system_data(sys_db)
        bot.send_message(
            message.chat.id,
            "✅ Tracking node refresh completed. All broadcast link metrics"
            " reset to 0.",
        )
        return

    elif text == "🔗 Update Channels":
        admin_states[user_id] = STATE_UPDATE_CHANNELS
        bot.send_message(
            message.chat.id,
            "📥 Send channels separated by space (e.g. @ch1 @ch2 @ch3):",
        )
        return

    # --- ADVANCED TRANSMISSION ENGINE ---
    if state in [STATE_FORWARD_BROADCAST, STATE_COPY_BROADCAST]:
        admin_states[user_id] = STATE_NONE

        with db_lock:
            target_users_snapshot = list(sys_db["users"])

        total_target = len(target_users_snapshot)
        success_count = 0
        failed_count = 0

        extracted_link = None
        if message.content_type == "text":
            extracted_link = extract_first_link(message.text)
        elif message.caption:
            extracted_link = extract_first_link(message.caption)

        broadcast_markup = None
        if extracted_link:
            import uuid

            link_uuid = str(uuid.uuid4())[:8]
            sys_db["broadcast_links"][link_uuid] = {
                "url": extracted_link,
                "clicks": 0,
            }
            save_system_data(sys_db)

            broadcast_markup = InlineKeyboardMarkup()
            btn_label = sys_db.get("broadcast_btn_text", "👉 Register Now")
            broadcast_markup.add(
                InlineKeyboardButton(
                    text=btn_label, callback_data=f"track_lnk_{link_uuid}"
                )
            )

        for uid in target_users_snapshot:
            try:
                try:
                    bot.unpin_chat_message(chat_id=uid)
                except Exception:
                    pass

                if state == STATE_FORWARD_BROADCAST:
                    if broadcast_markup:
                        sent_msg = bot.copy_message(
                            chat_id=uid,
                            from_chat_id=message.chat.id,
                            message_id=message.message_id,
                            reply_markup=broadcast_markup,
                        )
                    else:
                        sent_msg = bot.forward_message(
                            chat_id=uid,
                            from_chat_id=message.chat.id,
                            message_id=message.message_id,
                        )
                else:
                    sent_msg = bot.copy_message(
                        chat_id=uid,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id,
                        reply_markup=broadcast_markup,
                    )

                if sent_msg:
                    msg_id_to_pin = (
                        sent_msg.message_id
                        if hasattr(sent_msg, "message_id")
                        else sent_msg.get("message_id")
                    )
                    try:
                        bot.pin_chat_message(
                            chat_id=uid,
                            message_id=msg_id_to_pin,
                            disable_notification=False,
                        )
                    except Exception:
                        pass
                success_count += 1
            except Exception:
                failed_count += 1

        bot.send_message(
            message.chat.id,
            f"📢 <b>Broadcast Completed!</b>\n\n🎯 Total Target:"
            f" {total_target}\n✅ Success: {success_count}\n❌ Failed:"
            f" {failed_count}",
            parse_mode="HTML",
        )
        return

    # Dynamic States Handlers
    elif state == STATE_ADD_BTN_NAME:
        temp_btn_data[user_id] = {"text": text}
        admin_states[user_id] = STATE_ADD_BTN_URL
        bot.send_message(
            message.chat.id,
            "📥 Send button URL (e.g., https://t.me/example):",
        )

    elif state == STATE_ADD_BTN_URL:
        if user_id in temp_btn_data:
            temp_btn_data[user_id]["url"] = text
            sys_db["custom_buttons"].append(temp_btn_data[user_id])
            save_system_data(sys_db)
            del temp_btn_data[user_id]
            admin_states[user_id] = STATE_NONE
            bot.send_message(
                message.chat.id, "✅ New custom button added successfully!"
            )

    elif state == STATE_EDIT_BTN_TEXT:
        idx = target_edit_index.get(user_id)
        if idx is not None and 0 <= idx < len(sys_db["custom_buttons"]):
            sys_db["custom_buttons"][idx]["text"] = text
            save_system_data(sys_db)
            bot.send_message(
                message.chat.id, "✅ Button text updated successfully!"
            )
        admin_states[user_id] = STATE_NONE

    elif state == STATE_EDIT_BTN_URL:
        idx = target_edit_index.get(user_id)
        if idx is not None and 0 <= idx < len(sys_db["custom_buttons"]):
            sys_db["custom_buttons"][idx]["url"] = text
            save_system_data(sys_db)
            bot.send_message(
                message.chat.id, "✅ Button URL updated successfully!"
            )
        admin_states[user_id] = STATE_NONE

    elif state == STATE_EDIT_FREE_BTN:
        sys_db["free_code_btn_text"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(message.chat.id, "✅ Free Code Button text updated!")

    elif state == STATE_EDIT_BROADCAST_BTN:
        sys_db["broadcast_btn_text"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(message.chat.id, "✅ Broadcast Button text updated!")

    elif state == STATE_EDIT_PHOTO:
        sys_db["welcome_photo"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(
            message.chat.id, "✅ Welcome Photo URL updated successfully!"
        )

    elif state == STATE_EDIT_CAPTION:
        sys_db["welcome_caption"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(
            message.chat.id, "✅ Welcome Caption updated successfully!"
        )

    elif state == STATE_UPDATE_CHANNELS:
        sys_db["channels"] = text.split()
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(
            message.chat.id,
            f"✅ Required Channels updated: {', '.join(sys_db['channels'])}",
        )

    elif state == STATE_EDIT_VERIFY_TEXT:
        sys_db["verification_text"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(
            message.chat.id, "✅ Verification loader text updated!"
        )

    elif state == STATE_EDIT_ERROR_TEXT:
        sys_db["error_text"] = text
        save_system_data(sys_db)
        admin_states[user_id] = STATE_NONE
        bot.send_message(message.chat.id, "✅ Join error text updated!")


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot is polling...")
    bot.infinity_polling()
