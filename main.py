import telebot
from telebot import types
import json
import os
import re
import time
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

# --- BOT SETTINGS FROM ENVIRONMENT ---
API_TOKEN = os.environ.get('BOT_TOKEN', '') # Automatic Render se Token uthayega
ADMIN_ID = 1908832842  # Main Supreme Owner ID
CONNECTED_CHANNEL = -1002145879632

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"
MSG_LOG_FILE = "msg_log.json"
BAN_FILE = "banned_users.json"
CLICK_FILE = "clicks.json"

# --- INIT FILES ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

if not os.path.exists(MSG_LOG_FILE):
    with open(MSG_LOG_FILE, "w") as f: json.dump({}, f)

if not os.path.exists(BAN_FILE):
    with open(BAN_FILE, "w") as f: json.dump([], f)

if not os.path.exists(CLICK_FILE):
    with open(CLICK_FILE, "w") as f: json.dump({}, f)

cancel_broadcast_flag = False

def load_settings():
    default = {
        "maintenance": False,
        "auto_pin": True,
        "success_mode": False,
        "last_pinned_msgs": {},
        "admins": {str(ADMIN_ID): ["all"]},
        "text": "<b>🎉 Join Official Big Promo Code Channel</b>\n\n<b>📅 Daily FREE BIG CODE</b>\n\n<b>👇 Join our channels below and claim your code!</b>",
        "image": "https://t.me/TG_Looters/3",
        "success_image": "https://t.me/TG_Looters/3",
        "code": "LOOT200",  
        "reg_link": "https://share-rxapq9cajg.iw7.io/share/agent/SD08SPTT?data=eyJtljoxLCJsyW5kIjoxLCJpZCI6IjAifQ==",
        "error_text": "⚠️ <b>Aapne Join Nahi Kiya!</b>\n\n<b>Kripaya upar diye gaye 4 channels join karein.</b>\n\n📌 <b>Zaruri: 4 channels ko Pin karke rakho, tabhi code milega!</b>",
        "process_text": "⏳ <b>Verification in Progress...</b>\n\n🔍 <b>Checking if you pinned all 4 channels...</b>\n\n⏱️ <b>Please wait 5 seconds...</b>", 
        "dynamic_buttons": [
            {"text": "🚀 Claim ₹500", "url": "https://t.me/+tmxMobgZYe82ZmNl"},
            {"text": "🎁 Unlock Code", "url": "https://t.me/+uLvuR0wfZ6c5Yzdl"},
            {"text": "🎯 Claim bonus", "url": "https://t.me/TECHNO_FUNDS"},
            {"text": "💎 VIP GIFT", "url": "https://t.me/+MDQ7NXT1pN42NWU1"}
        ]
    }

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                current_data = json.load(f)
                for key, val in default.items():
                    if key not in current_data:
                        current_data[key] = val
                return current_data
        except: pass

    with open(SETTINGS_FILE, "w") as f: json.dump(default, f)
    return default

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)

def get_users():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def save_users_list(users):
    with open(DB_FILE, "w") as f: json.dump(users, f)

def save_user(user_id):
    users = get_users()
    if user_id not in users:
        users.append(user_id)
        save_users_list(users)

def get_banned_users():
    try:
        with open(BAN_FILE, "r") as f: return json.load(f)
    except: return []

def ban_user_id(user_id):
    banned = get_banned_users()
    if user_id not in banned:
        banned.append(user_id)
        with open(BAN_FILE, "w") as f: json.dump(banned, f)
    users = get_users()
    if user_id in users:
        users.remove(user_id)
        save_users_list(users)

def unban_user_id(user_id):
    banned = get_banned_users()
    if user_id in banned:
        banned.remove(user_id)
        with open(BAN_FILE, "w") as f: json.dump(banned, f)

def load_msg_log():
    try:
        with open(MSG_LOG_FILE, "r") as f: return json.load(f)
    except: return {}

def save_msg_log(data):
    with open(MSG_LOG_FILE, "w") as f: json.dump(data, f)

def load_clicks():
    try:
        with open(CLICK_FILE, "r") as f: return json.load(f)
    except: return {}

def save_clicks(data):
    with open(CLICK_FILE, "w") as f: json.dump(data, f)

# --- SECURITY PERMISSION CHECKER ---
def check_permission(user_id, required_perm):
    settings = load_settings()
    admins = settings.get("admins", {})
    u_id_str = str(user_id)
    if u_id_str in admins:
        perms = admins[u_id_str]
        if "all" in perms or required_perm in perms:
            return True
    return False

# --- MANAGING ADMINS COMMANDS (OWNER ONLY) ---
@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_id = parts[1].strip()
        perm = parts[2].strip().lower()
        
        valid_perms = ["broadcast", "buttons", "settings", "users", "mode", "all"]
        if perm not in valid_perms:
            bot.reply_to(message, "❌ Use: broadcast, buttons, settings, users, mode, all")
            return
            
        settings = load_settings()
        if "admins" not in settings: settings["admins"] = {}
        if target_id not in settings["admins"]: settings["admins"][target_id] = []
        if perm not in settings["admins"][target_id]:
            settings["admins"][target_id].append(perm)
            
        save_settings(settings)
        bot.reply_to(message, f"✅ User {target_id} ko {perm} permission mili!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/addadmin [ID] [permission]`")

@bot.message_handler(commands=['removeadmin'])
def remove_admin_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = message.text.split()[1].strip()
        if target_id == str(ADMIN_ID):
            bot.reply_to(message, "❌ Owner ko nahi hata sakte!")
            return
            
        settings = load_settings()
        if "admins" in settings and target_id in settings["admins"]:
            del settings["admins"][target_id]
            save_settings(settings)
            bot.reply_to(message, f"✅ Admin {target_id} removed.")
        else:
            bot.reply_to(message, "❌ ID admin list mein nahi hai.")
    except:
        bot.reply_to(message, "❌ Use: `/removeadmin [ID]`")

@bot.message_handler(commands=['adminlist'])
def view_admin_list(message):
    if not check_permission(message.from_user.id, "users"): return
    settings = load_settings()
    admins = settings.get("admins", {})
    msg = "👑 <b>BOT ADMINS & PERMISSIONS:</b>\n\n"
    for u_id, perms in admins.items():
        perm_str = ", ".join(perms)
        msg += f"👤 ID: <code>{u_id}</code>\n🛡 Perms: <code>{perm_str}</code>\n\n"
    bot.reply_to(message, msg, parse_mode='HTML')

# --- CHANNEL POST HANDLERS ---
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        users = get_users()
        sent_msg_ids = []
        for user_id in users:
            try:
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

# --- CONTROLLABLE ADMIN COMMANDS ---
@bot.message_handler(commands=['switchmode'])
def toggle_success_mode(message):
    if not check_permission(message.from_user.id, "mode"): return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        settings["success_mode"] = (opt == 'on')
        save_settings(settings)
        status = "ON 🟢" if opt == 'on' else "OFF 🔴"
        bot.reply_to(message, f"<b>Success Mode: {status}</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/switchmode [on/off]`")

@bot.message_handler(commands=['setlink'])
def change_link(message):
    if not check_permission(message.from_user.id, "mode"): return
    try:
        new_link = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["reg_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ App Link: <code>{new_link}</code>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/setlink [Link]`")

@bot.message_handler(commands=['setsuccessphoto'])
def change_success_photo(message):
    if not check_permission(message.from_user.id, "mode"): return
    try:
        new_photo = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["success_image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Success Photo badal gayi!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/setsuccessphoto [URL]`")

@bot.message_handler(commands=['clickstats'])
def show_click_stats(message):
    if not check_permission(message.from_user.id, "users"): return
    clicks = load_clicks()
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    
    report = "📊 <b>LIVE BUTTON CLICKS REPORT</b>\n\n"
    for i, btn in enumerate(buttons):
        btn_id = f"btn_{i}"
        report += f"🔘 {btn['text']}: <code>{clicks.get(btn_id, 0)} Clicks</code>\n"
        
    report += f"\n🎉 Claim Button: <code>{clicks.get('claim_btn_click', 0)}</code>\n"
    report += f"🔗 Success App Button: <code>{clicks.get('app_btn_click', 0)}</code>\n\n"
    report += "📢 <b>BROADCAST MESSAGES LINKS:</b>\n"
    
    bc_keys = [k for k in clicks.keys() if k.startswith("bc_msg_")]
    if not bc_keys:
        report += "<i>Koi click nahi hua hai abhi.</i>"
    else:
        for key in bc_keys:
            report += f"👉 ID #{key.split('_')[2]}: <code>{clicks[key]} Clicks</code>\n"
            
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if not check_permission(message.from_user.id, "users"): return
    bot.reply_to(message, f"👥 Active Users: <code>{len(get_users())}</code>\n🚫 Banned: <code>{len(get_banned_users())}</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if not check_permission(message.from_user.id, "users"): return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Database Backup.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if not check_permission(message.from_user.id, "settings"): return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance: ON 🔴")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if not check_permission(message.from_user.id, "settings"): return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance: OFF 🟢")

@bot.message_handler(commands=['setpin'])
def toggle_pin(message):
    if not check_permission(message.from_user.id, "broadcast"): return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        settings["auto_pin"] = (opt == 'on')
        save_settings(settings)
        bot.reply_to(message, f"📌 Auto-Pin: {opt.upper()}")
    except: bot.reply_to(message, "❌ Use: `/setpin [on/off]`")

@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if not check_permission(message.from_user.id, "users"): return
    try:
        target_id = int(message.text.split()[1])
        ban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> BAN ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Use: `/ban ID`")

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if not check_permission(message.from_user.id, "users"): return
    try:
        target_id = int(message.text.split()[1])
        unban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> UNBAN ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Use: `/unban ID`")

@bot.message_handler(commands=['addbutton'])
def add_button_command(message):
    if not check_permission(message.from_user.id, "buttons"): return
    try:
        content = message.text.split(maxsplit=1)[1]
        parts = content.split(maxsplit=1)
        btn_index = int(parts[0]) - 1
        details = parts[1].split('|')
        btn_name = details[0].strip()
        btn_url = details[1].strip()

        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        new_btn = {"text": btn_name, "url": btn_url}
        if 0 <= btn_index < len(buttons): buttons[btn_index] = new_btn
        else: buttons.append(new_btn)
        settings["dynamic_buttons"] = buttons
        save_settings(settings)
        bot.reply_to(message, "✅ Button successfully updated!")
    except: bot.reply_to(message, "❌ Use: `/addbutton [Num] [Naam] | [Link]`")

@bot.message_handler(commands=['delbutton'])
def del_button_command(message):
    if not check_permission(message.from_user.id, "buttons"): return
    try:
        btn_index = int(message.text.split()[1]) - 1
        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        if 0 <= btn_index < len(buttons):
            removed = buttons.pop(btn_index)
            settings["dynamic_buttons"] = buttons
            save_settings(settings)
            bot.reply_to(message, f"✅ Button '{removed['text']}' deleted!")
        else: bot.reply_to(message, "❌ Button not found.")
    except:
        bot.reply_to(message, "❌ Use: `/delbutton [Number]`")

@bot.message_handler(commands=['seterrortext'])
def change_error_text_command(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_err = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["error_text"] = new_err
        save_settings(settings)
        bot.reply_to(message, "✅ Error Text updated!")
    except: bot.reply_to(message, "❌ Use: `/seterrortext [text]`")

@bot.message_handler(commands=['setprocesstext'])
def change_process_text_command(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_proc = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["process_text"] = new_proc
        save_settings(settings)
        bot.reply_to(message, "✅ Process Text updated!")
    except: bot.reply_to(message, "❌ Use: `/setprocesstext [text]`")

@bot.message_handler(commands=['settext'])
def change_text(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Text updated!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Photo updated!")
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_code = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Code badal kar <b>{new_code}</b> ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not check_permission(message.from_user.id, "broadcast") and not check_permission(message.from_user.id, "buttons") and not check_permission(message.from_user.id, "settings") and not check_permission(message.from_user.id, "users") and not check_permission(message.from_user.id, "mode"): return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "👑 <b>Admin Management:</b>\n"
        "➕ <code>/addadmin [ID] [permission]</code>\n"
        "➖ <code>/removeadmin [ID]</code>\n"
        "📋 <code>/adminlist</code>\n\n"
        "📊 <code>/stats</code> | 📈 <code>/clickstats</code>\n"
        "💾 <code>/export</code> | 🔴 <code>/maintenance_on</code>\n"
        "🟢 <code>/maintenance_off</code> | 📌 <code>/setpin [on/off]</code>\n"
        "🚫 <code>/ban [ID]</code> | ✅ <code>/unban [ID]</code>\n\n"
        "🎛 <b>Smart Mode Switch:</b>\n"
        "🔀 <code>/switchmode [on/off]</code>\n"
        "🔗 <code>/setlink [URL]</code> | 🖼 <code>/setsuccessphoto [URL]</code>\n\n"
        "🔘 <b>Buttons Control:</b>\n"
        "➕ <code>/addbutton [Num] [Naam] | [Link]</code>\n"
        "➖ <code>/delbutton [Num]</code>\n\n"
        "📝 <b>Texts Control:</b>\n"
        "⏳ <code>/setprocesstext [text]</code>\n"
        "⚠️ <code>/seterrortext [text]</code>\n"
        "📝 <code>/settext [text]</code> | 🖼 <code>/setphoto [url]</code>\n"
        "🎁 <code>/setcode [code]</code>"
    )
    bot.send_message(message.chat.id, panel_text, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id in get_banned_users():
        bot.send_message(message.chat.id, "❌ Aapko ban kar diya gaya hai.")
        return
    send_welcome(message)

# --- BROADCAST CANCEL HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    global cancel_broadcast_flag
    if check_permission(call.from_user.id, "broadcast"):
        cancel_broadcast_flag = True
        bot.answer_callback_query(call.id, "Stopping process...")
        bot.edit_message_text("⚠️ <b>Broadcast Canceled!</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')

# --- SMART BROADCAST HANDLER ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    global cancel_broadcast_flag
    users = get_users() 
    settings = load_settings()

    if message.from_user.id in get_banned_users(): return
    if (settings["maintenance"] and not check_permission(message.from_user.id, "settings")):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai.")
        return

    if check_permission(message.from_user.id, "
