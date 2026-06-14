import telebot
from telebot import types
import json
import os
from flask import Flask
from threading import Thread

# --- RENDER PORT FIX ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT SETTINGS ---
API_TOKEN = "8313028390:AAHYtwlM9mv-W9BeeJZ2q5CgjAQnhsIZVmM"
ADMIN_ID = 1908832842
START_IMAGE_URL = "https://t.me/TG_Looters/3"

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"

def load_settings():
    default = {
        "maintenance": False,
        "force_join": False,
        "start_message": None,
        "start_image": None
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return default

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def get_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

# --- MESSAGE HANDLER ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    users = get_users() 
    settings = load_settings()

    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(
            message.chat.id,
            "🛠 Bot Maintenance Mode Me Hai"
        )
        return

    # --- ADMIN LOGIC (BROADCAST EVERYTHING) ---
    if message.from_user.id == ADMIN_ID:
        if message.text == "/start":
            send_welcome(message)
            return

        bot.send_message(
            ADMIN_ID,
            f"🚀 {len(users)} users ko broadcast shuru ho raha hai..."
        )

        count = 0
        for user_id in users:
            try:
                bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                count += 1
            except:
                pass

        bot.send_message(
            ADMIN_ID,
            f"✅ Done! {count} users ko bhej diya gaya."
        )

    # --- NORMAL USER LOGIC ---
    else:
        if message.content_type == 'text' and message.text == "/start":
            send_welcome(message)

# --- ADMIN COMMAND ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        """
⚙ ADMIN PANEL

/stats
/export

/maintenance_on
/maintenance_off

/forcejoin_on
/forcejoin_off

Broadcast:
Text, Photo, Video send karo
Automatically sab users ko chala jayega.
"""
    )

# --- WELCOME FUNCTION ---
def send_welcome(message):
    users = get_users()

    if message.chat.id not in users:
        users.append(message.chat.id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)

    welcome_text = (
        "<b>🎉 Join Official Big Promo Code Channel</b>\n\n"
        "<b>📅 Daily FREE BIG CODE</b>\n\n"
        "<b>👇 Join our channels below and claim your code!</b>"
    )

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton(
        "🚀 Claim ₹500",
        url="https://t.me/+tmxMobgZYe82ZmNl"
    )

    btn2 = types.InlineKeyboardButton(
        "🎁 Unlock Code",
        url="https://t.me/+uLvuR0wfZ6c5Yzdl"
    )

    btn3 = types.InlineKeyboardButton(
        "🎯 Claim bonus",
        url="https://t.me/TECHNO_FUNDS"
    )

    btn4 = types.InlineKeyboardButton(
        "💎 VIP GIFT",
        url="https://t.me/+MDQ7NXT1pN42NWU1"
    )

    claim_btn = types.InlineKeyboardButton(
        "🎉 Get My Free Code",
        callback_data="claim_code"
    )

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(claim_btn)

    try:
        bot.send_photo(
            message.chat.id,
            START_IMAGE_URL,
            caption=welcome_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    except:
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=markup,
            parse_mode='HTML'
        )

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "claim_code":
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye dono channels join karein.</b>\n\n"
            "📌 <b>Zaruri:</b> Dono channels ko Pin karke rakho, tabhi code milega!"
        )

        bot.answer_callback_query(
            call.id,
            "Checking subscription status..."
        )

        bot.send_message(
            call.message.chat.id,
            stylish_error,
            parse_mode='HTML'
        )

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
    
