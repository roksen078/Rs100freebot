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
API_TOKEN = "8313028390:AAGQb8H9nEz46OyXvy7Qg7E4QkT1KP8Uh0E"  # Yahan apna token dalein
ADMIN_ID = 1908832842
CONNECTED_CHANNEL = -1002145879632  # Aapki channel ID

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"
MSG_LOG_FILE = "msg_log.json"

# --- INIT FILES & DEFAULT SETTINGS ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

if not os.path.exists(MSG_LOG_FILE):
    with open(MSG_LOG_FILE, "w") as f: json.dump({}, f)

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
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_user(user_id):
    users = get_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f: json.dump(users, f)

def load_msg_log():
    try:
        with open(MSG_LOG_FILE, "r") as f: return json.load(f)
    except: return {}

def save_msg_log(data):
    with open(MSG_LOG_FILE, "w") as f: json.dump(data, f)

# --- CHANNEL POST HANDLERS (FOR LIVE EDIT) ---
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        users = get_users()
        sent_msg_ids = []
        
        for user_id in users:
            try:
                # Channel se aane wali post ko automatic original channel tag ke sath forward karega
                sent_msg = bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                sent_msg_ids.append({"user_id": user_id, "msg_id": sent_msg.message_id})
            except: pass
            
        logs = load_msg_log()
        logs[str(message.message_id)] = sent_msg_ids
        save_msg_log(logs)

@bot.edited_channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_edited_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        logs = load_msg_log()
        ch_msg_id = str(message.message_id)
        
        if ch_msg_id in logs:
            for target in logs[ch_msg_id]:
                try:
                    if message.text:
                        bot.edit_message_text(text=message.text, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                    elif message.caption:
                        bot.edit_message_caption(caption=message.caption, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                except: pass

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
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Aapka Users Database Backup File.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: ON 🔴")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: OFF 🟢")

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
            bot.reply_to(message, f"✅ Channel {ch_num} ka link update ho gaya!")
        else:
            bot.reply_to(message, "❌ 1 se 4 tak choose karein.")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['settext'])
def change_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Text badal gaya!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Bot ki Main Photo URL badal gayi!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_code = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Code badal kar <b>{new_code}</b> ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "📊 <code>/stats</code> | 💾 <code>/export</code>\n"
        "🔴 <code>/maintenance_on</code> | 🟢 <code>/maintenance_off</code>\n\n"
        "🔗 <code>/setlink [1-4] [link]</code>\n"
        "📝 <code>/settext [text]</code>\n"
        "🖼 <code>/setphoto [image_url]</code>\n"
        "🎁 <code>/setcode [code]</code>\n\n"
        "📢 <b>Broadcast Options:</b>\n"
        "1. Bot me direct forward karo (Smart: Tag messages forward honge, normal copy honge).\n"
        "2. Apne connected channel me post daalo (Live Edit support ke sath)."
    )
    bot.send_message(message.chat.id, panel_text, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def handle_start(message):
    send_welcome(message)

# --- SMART BROADCAST HANDLER (FOR TAG & COPIED MESSAGES) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    users = get_users() 
    settings = load_settings()

    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai.")
        return

    if message.from_user.id == ADMIN_ID:
        if message.text and message.text.startswith('/'): return

        bot.send_message(ADMIN_ID, f"🚀 {len(users)} users ko broadcast shuru...")
        count = 0
        
        for user_id in users:
            try:
                # Agar message admin ne kisi channel se FORWARD kiya hai, toh forward_message chalega (With Tag)
                if message.forward_from_chat or message.forward_from:
                    bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                # Agar admin ne DIRECT likha ya khud photo select karke bheji hai, toh copy_message chalega (Bina Tag Ke)
                else:
                    bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                count += 1
            except: pass
            
        bot.send_message(ADMIN_ID, f"✅ Done! {count} users ko bhej diya gaya.")
    else:
        if message.content_type == 'text' and message.text == "/start":
            send_welcome(message)

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
        bot.send_photo(message.chat.id, settings.get("image"), caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, settings.get("text"), reply_markup=markup, parse_mode='HTML')

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "claim_code":
        bot.answer_callback_query(call.id, "Checking...")
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye dono channels join karein.</b>\n\n"
            "📌 <b>Zaruri:</b> Dono channels ko Pin karke rakho, tabhi code milega!"
        )
        bot.send_message(call.message.chat.id, stylish_error, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
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
API_TOKEN = ""  # Yahan apna token dalein
ADMIN_ID = 1908832842
CONNECTED_CHANNEL = -1002145879632  # Aapki channel ID

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"
MSG_LOG_FILE = "msg_log.json"

# --- INIT FILES & DEFAULT SETTINGS ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

if not os.path.exists(MSG_LOG_FILE):
    with open(MSG_LOG_FILE, "w") as f: json.dump({}, f)

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
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_user(user_id):
    users = get_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f: json.dump(users, f)

def load_msg_log():
    try:
        with open(MSG_LOG_FILE, "r") as f: return json.load(f)
    except: return {}

def save_msg_log(data):
    with open(MSG_LOG_FILE, "w") as f: json.dump(data, f)

# --- CHANNEL POST HANDLERS (FOR LIVE EDIT) ---
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        users = get_users()
        sent_msg_ids = []
        
        for user_id in users:
            try:
                # Channel se aane wali post ko automatic original channel tag ke sath forward karega
                sent_msg = bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                sent_msg_ids.append({"user_id": user_id, "msg_id": sent_msg.message_id})
            except: pass
            
        logs = load_msg_log()
        logs[str(message.message_id)] = sent_msg_ids
        save_msg_log(logs)

@bot.edited_channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_edited_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        logs = load_msg_log()
        ch_msg_id = str(message.message_id)
        
        if ch_msg_id in logs:
            for target in logs[ch_msg_id]:
                try:
                    if message.text:
                        bot.edit_message_text(text=message.text, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                    elif message.caption:
                        bot.edit_message_caption(caption=message.caption, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                except: pass

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
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Aapka Users Database Backup File.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: ON 🔴")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: OFF 🟢")

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
            bot.reply_to(message, f"✅ Channel {ch_num} ka link update ho gaya!")
        else:
            bot.reply_to(message, "❌ 1 se 4 tak choose karein.")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['settext'])
def change_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Text badal gaya!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Bot ki Main Photo URL badal gayi!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_code = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Code badal kar <b>{new_code}</b> ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "📊 <code>/stats</code> | 💾 <code>/export</code>\n"
        "🔴 <code>/maintenance_on</code> | 🟢 <code>/maintenance_off</code>\n\n"
        "🔗 <code>/setlink [1-4] [link]</code>\n"
        "📝 <code>/settext [text]</code>\n"
        "🖼 <code>/setphoto [image_url]</code>\n"
        "🎁 <code>/setcode [code]</code>\n\n"
        "📢 <b>Broadcast Options:</b>\n"
        "1. Bot me direct forward karo (Smart: Tag messages forward honge, normal copy honge).\n"
        "2. Apne connected channel me post daalo (Live Edit support ke sath)."
    )
    bot.send_message(message.chat.id, panel_text, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def handle_start(message):
    send_welcome(message)

# --- SMART BROADCAST HANDLER (FOR TAG & COPIED MESSAGES) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    users = get_users() 
    settings = load_settings()

    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai.")
        return

    if message.from_user.id == ADMIN_ID:
        if message.text and message.text.startswith('/'): return

        bot.send_message(ADMIN_ID, f"🚀 {len(users)} users ko broadcast shuru...")
        count = 0
        
        for user_id in users:
            try:
                # Agar message admin ne kisi channel se FORWARD kiya hai, toh forward_message chalega (With Tag)
                if message.forward_from_chat or message.forward_from:
                    bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                # Agar admin ne DIRECT likha ya khud photo select karke bheji hai, toh copy_message chalega (Bina Tag Ke)
                else:
                    bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                count += 1
            except: pass
            
        bot.send_message(ADMIN_ID, f"✅ Done! {count} users ko bhej diya gaya.")
    else:
        if message.content_type == 'text' and message.text == "/start":
            send_welcome(message)

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
        bot.send_photo(message.chat.id, settings.get("image"), caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, settings.get("text"), reply_markup=markup, parse_mode='HTML')

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "claim_code":
        bot.answer_callback_query(call.id, "Checking...")
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye dono channels join karein.</b>\n\n"
            "📌 <b>Zaruri:</b> Dono channels ko Pin karke rakho, tabhi code milega!"
        )
        bot.send_message(call.message.chat.id, stylish_error, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
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

@bot.message_handler(commands=['start'])
def handle_start(message):
    send_welcome(message)

# --- 2. MAIN BROADCAST HANDLER (ISKO SABSE NICHE RAKHNA HAI) ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    users = get_users() 
    settings = load_settings()

    # Normal users ke liye maintenance check
    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai. Kripaya thodi der baad koshish karein.")
        return

    # Admin Broadcast logic (Bina kisi command ke forward kiya hua post)
    if message.from_user.id == ADMIN_ID:
        # Agar admin galti se koi text bhej raha hai jo '/' se shuru hota hai (jaise galat command), toh use broadcast mat karo
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
    if call.data == "claim_code":
        bot.answer_callback_query(call.id, "Checking...")
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye 4 channels join karein.</b>\n\n"
            "📌 <b>Zaruri:</b> 4 channels ko Pin karke rakho, tabhi code milega!"
        )
        bot.send_message(call.message.chat.id, stylish_error, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
    
