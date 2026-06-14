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
API_TOKEN = "8313028390:AAHYtwlM9mv-W9BeeJZ2q5CgjAQnhsIZVmM"  # Yahan apna token dalein
ADMIN_ID = 1908832842

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"

# --- INIT FILES & DEFAULT SETTINGS ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

def load_settings():
    default = {
        "maintenance": False,
        "text": "<b>🎉 Join Official Big Promo Code Channel</b>\n\n<b>📅 Daily FREE BIG CODE</b>\n\n<b>👇 Join our channels below and claim your code!</b>",
        "image": "https://t.me/TG_Looters/3",
        "code": "FREE100LOOT",
        "ch1": "https://t.me/+tmxMobgZYe82ZmNl",
        "ch2": "https://t.me/+uLvuR0wfZ6c5Yzdl",
        "ch3": "https://t.me/TECHNO_FUNDS",
        "ch4": "https://t.me/+MDQ7NXT1pN42NWU1"
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                current_data = json.load(f)
                # Ensure all new keys exist
                for key, val in default.items():
                    if key not in current_data:
                        current_data[key] = val
                return current_data
        except:
            pass

    with open(SETTINGS_FILE, "w") as f: json.dump(default, f)
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

def save_user(user_id):
    users = get_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)

# --- ADMIN COMMANDS HANDLERS ---
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    bot.reply_to(message, f"📊 Total Users: {len(users)}")

@bot.message_handler(commands=['export'])
def export_database(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users:
            f.write(f"{u_id}\n")
    
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Aapka Users Database Backup File.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: ON 🔴 (Normal users bot use nahi kar sakte)")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: OFF 🟢 (Ab sabhi users use kar sakte hain)")

@bot.message_handler(commands=['setlink'])
def change_link(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split(maxsplit=2)
        ch_num = parts[1]
        new_url = parts[2]
        
        if ch_num in ['1', '2', '3', '4']:
            settings = load_settings()
            settings[f"ch{ch_num}"] = new_url
            save_settings(settings)
            bot.reply_to(message, f"✅ Channel {ch_num} ka link update ho gaya bina restart kiye!")
        else:
            bot.reply_to(message, "❌ Sirf 1 se 4 tak choose karein. Example: /setlink 1 https://t.me/link")
    except:
        bot.reply_to(message, "❌ Format galat hai! Sahi format: `/setlink 1 https://t.me/link`")

@bot.message_handler(commands=['settext'])
def change_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Text badal gaya bina restart kiye!")
    except:
        bot.reply_to(message, "❌ Format galat hai. Example: `/settext Aapka Text`")

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Bot ki Main Photo URL badal gayi!")
    except:
        bot.reply_to(message, "❌ Format galat hai. Example: `/setphoto https://link_to_image.jpg`")

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_code = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Claim Button ka Promo Code ab badal kar <b>{new_code}</b> ho gaya hai!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format galat hai. Example: `/setcode NEWCODE100`")

# --- MAIN MESSAGE HANDLER & BROADCAST ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    users = get_users() 
    settings = load_settings()

    # Normal users ke liye maintenance check
    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai. Kripaya thodi der baad koshish karein.")
        return

    # --- ADMIN LOGIC (BROADCAST EVERYTHING SAME AS BEFORE) ---
    if message.from_user.id == ADMIN_ID:
        if message.text == "/start":
            send_welcome(message)
            return
        
        # Agar admin command likh raha hai toh broadcast nahi karega
        if message.text and message.text.startswith('/'):
            return

        bot.send_message(ADMIN_ID, f"🚀 {len(users)} users ko broadcast shuru ho raha hai...")

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

        bot.send_message(ADMIN_ID, f"✅ Done! {count} users ko bhej diya gaya.")

    # --- NORMAL USER LOGIC ---
    else:
        if message.content_type == 'text' and message.text == "/start":
            send_welcome(message)

# --- ADMIN PANEL MAIN MENU COMMAND ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return

    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "📊 <code>/stats</code> - Total Users dekhne ke liye\n"
        "💾 <code>/export</code> - Database ka text backup file lene ke liye\n\n"
        "🔴 <code>/maintenance_on</code> - Maintenance ON karne ke liye\n"
        "🟢 <code>/maintenance_off</code> - Maintenance OFF karne ke liye\n\n"
        "🔗 <code>/setlink [1-4] [link]</code> - Channel link badalna\n"
        "📝 <code>/settext [text]</code> - Welcome text badalna\n"
        "🖼 <code>/setphoto [image_url]</code> - Main photo badalna\n"
        "🎁 <code>/setcode [code]</code> - Promo Code badalna\n\n"
        "📢 <b>Broadcast:</b>\n"
        "Pehle ki tarah koi bhi message/photo/video direct send ya forward karo, sabko chala jayega."
    )
    bot.send_message(message.chat.id, panel_text, parse_mode='HTML')

# --- WELCOME FUNCTION ---
def send_welcome(message):
    save_user(message.chat.id)
    settings = load_settings()

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("🚀 Claim ₹500", url=settings.get("ch1"))
    btn2 = types.InlineKeyboardButton("🎁 Unlock Code", url=settings.get("ch2"))
    btn3 = types.InlineKeyboardButton("🎯 Claim bonus", url=settings.get("ch3"))
    btn4 = types.InlineKeyboardButton("💎 VIP GIFT", url=settings.get("ch4"))
    claim_btn = types.InlineKeyboardButton("🎉 Get My Free Code", callback_data="claim_code")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(claim_btn)

    try:
        bot.send_photo(
            message.chat.id,
            settings.get("image"),
            caption=settings.get("text"),
            reply_markup=markup,
            parse_mode='HTML'
        )
    except:
        bot.send_message(
            message.chat.id,
            settings.get("text"),
            reply_markup=markup,
            parse_mode='HTML'
        )

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    settings = load_settings()
    if call.data == "claim_code":
        bot.answer_callback_query(call.id, "Success!")
        
        # Ab claim button dabaane par aapka set kiya hua real code dikhega
        success_message = (
            f"<b>🎉 Aapka Code: {settings.get('code')}</b>\n\n"
            "Enjoy aapka free reward!"
        )
        bot.send_message(call.message.chat.id, success_message, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
