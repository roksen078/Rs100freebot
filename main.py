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

# --- BOT SETTINGS ---
API_TOKEN = "8313028390:AAFBc5ELaeEg4LUi_oPzkOlmiCSKNdFDjzM"  # Yahan apna token dalein
ADMIN_ID = 1908832842
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

# --- ADMIN COMMANDS HANDLERS ---
@bot.message_handler(commands=['switchmode'])
def toggle_success_mode(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        if opt == 'on':
            settings["success_mode"] = True
            msg = "🟢 <b>Success Mode: ON</b> (Ab timer ke baad Photo + Promo Code + Register Button dikhega!)"
        else:
            settings["success_mode"] = False
            msg = "🔴 <b>Success Mode: OFF</b> (Ab timer ke baad purana Error text hi dikhega!)"
        save_settings(settings)
        bot.reply_to(message, msg, parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/switchmode [on/off]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setlink'])
def change_link(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_link = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["reg_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ <b>Naya Application Link add ho gaya!</b>\nURL: <code>{new_link}</code>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/setlink [Link]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setsuccessphoto'])
def change_success_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["success_image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, f"✅ <b>Success Mode ki Photo Link badal gayi!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/setsuccessphoto [URL]</code>", parse_mode='HTML')

@bot.message_handler(commands=['clickstats'])
def show_click_stats(message):
    if message.from_user.id != ADMIN_ID: return
    clicks = load_clicks()
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    
    report = "📊 <b>LIVE BUTTON CLICKS REPORT</b>\n\n"
    
    # 1. Welcome Screen Buttons Clicks
    for i, btn in enumerate(buttons):
        btn_id = f"btn_{i}"
        count = clicks.get(btn_id, 0)
        report += f"🔘 Button {i+1}: <b>{btn['text']}</b>\n🎯 Total Clicks: <code>{count}</code>\n\n"
        
    claim_count = clicks.get("claim_btn_click", 0)
    app_btn_count = clicks.get("app_btn_click", 0)
    
    report += f"🎉 Claim Button Clicks: <code>{claim_count}</code>\n"
    report += f"🔗 Success App Button Clicks: <code>{app_btn_count}</code>\n\n"
    
    # 2. Specific Broadcast Links Clicks (Message ID Wise)
    report += "📢 <b>BROADCAST MESSAGES LINKS REPORT:</b>\n"
    broadcast_keys = [k for k in clicks.keys() if k.startswith("bc_msg_")]
    
    if not broadcast_keys:
        report += "<i>Abhi tak kisi broadcast link par click nahi hua.</i>"
    else:
        for key in broadcast_keys:
            msg_id = key.split("_")[2]
            count = clicks[key]
            report += f"👉 Message ID <code>#{msg_id}</code> Link Clicks: <code>{count}</code>\n"
            
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    banned = get_banned_users()
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👥 Total Active Users: <code>{len(users)}</code>\n🚫 Total Banned Users: <code>{len(banned)}</code>", parse_mode='HTML')

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

@bot.message_handler(commands=['setpin'])
def toggle_pin(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        if opt == 'on':
            settings["auto_pin"] = True
            bot.reply_to(message, "📌 Auto-Pin Mode: ON 🟢")
        elif opt == 'off':
            settings["auto_pin"] = False
            bot.reply_to(message, "📌 Auto-Pin Mode: OFF 🔴")
        save_settings(settings)
    except: bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        ban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> BAN ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Use: `/ban ID`")

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        unban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> UNBAN ho gaya!", parse_mode='HTML')
    except: bot.reply_to(message, "❌ Use: `/unban ID`")

@bot.message_handler(commands=['addbutton'])
def add_button_command(message):
    if message.from_user.id != ADMIN_ID: return
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
        if 0 <= btn_index < len(buttons):
            buttons[btn_index] = new_btn
            msg = f"✅ Button {btn_index + 1} update ho gaya!"
        else:
            buttons.append(new_btn)
            msg = f"✅ Naya Button {len(buttons)} jodh diya gaya!"

        settings["dynamic_buttons"] = buttons
        save_settings(settings)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "❌ Format: `/addbutton [Number] [Naam] | [Link]`")

@bot.message_handler(commands=['delbutton'])
def del_button_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        btn_index = int(message.text.split()[1]) - 1
        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        if 0 <= btn_index < len(buttons):
            removed = buttons.pop(btn_index)
            settings["dynamic_buttons"] = buttons
            save_settings(settings)
            clicks = load_clicks()
            btn_id = f"btn_{btn_index}"
            if btn_id in clicks: clicks[btn_id] = 0
            save_clicks(clicks)
            bot.reply_to(message, f"✅ Button '{removed['text']}' ko delete kar diya gaya!")
        else: bot.reply_to(message, "❌ Is number ka koi button nahi hai.")
    except:
        bot.reply_to(message, "❌ Format: `/delbutton [Number]`")

@bot.message_handler(commands=['seterrortext'])
def change_error_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_err = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["error_text"] = new_err
        save_settings(settings)
        bot.reply_to(message, "✅ Error Alert Text badal gaya!")
    except:
        bot.reply_to(message, "❌ Format: `/seterrortext [text]`")

@bot.message_handler(commands=['setprocesstext'])
def change_process_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_proc = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["process_text"] = new_proc
        save_settings(settings)
        bot.reply_to(message, "✅ Processing Timer Text badal gaya!")
    except:
        bot.reply_to(message, "❌ Format: `/setprocesstext [text]`")

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
        new_code = message.text.split(maxsplit=1)[1].strip()
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
    banned = get_banned_users()
    if message.from_user.id in banned:
        bot.send_message(message.chat.id, "❌ Aapko is bot se permanent BAN kar diya gaya hai.")
        return
    # Note: Ensure you define send_welcome(message) elsewhere or handle start logic here.
    try:
        settings = load_settings()
        bot.send_message(message.chat.id, settings["text"], parse_mode='HTML')
    except: pass

# --- BROADCAST CANCEL HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    global cancel_broadcast_flag
    if call.from_user.id == ADMIN_ID:
        cancel_broadcast_flag = True
        bot.answer_callback_query(call.id, "Stopping process...")
        bot.edit_message_text("⚠️ <b>Broadcast Canceled by Admin!</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')

# --- SMART BROADCAST HANDLER ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    global cancel_broadcast_flag
    users = get_users() 
    settings = load_settings()
    banned = get_banned_users()

    if message.from_user.id in banned: return

    if (settings["maintenance"] and message.from_user.id != ADMIN_ID):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai.")
        return

    if message.from_user.id == ADMIN_ID:
        if message.text and message.text.startswith('/'): return

        text_to_scan = message.text if message.text else (message.caption if message.caption else "")
        urls = re.findall(r'(https?://\S+)', text_to_scan)
        
        # Ek unique link map banayenge jo message id ko link ke sath save rakhega
        msg_id_str = str(message.message_id)
        
        # Register button lagaya jiske callback me message id track hogi
        markup = types.InlineKeyboardMarkup()
        register_btn = types.InlineKeyboardButton("Register Link", callback_data=f"click_bc_{msg_id_str}")
        markup.add(register_btn)
        
        # Settings me is message id ke liye url maps lock kar do
        if urls:
            if "broadcast_links" not in settings: settings["broadcast_links"] = {}
            settings["broadcast_links"][msg_id_str] = urls[0]
            save_settings(settings)

        cancel_markup = types.InlineKeyboardMarkup()
        cancel_btn = types.InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast")
        cancel_markup.add(cancel_btn)

        bot.send_message(ADMIN_ID, f"🚀 <b>{len(users)} users ko broadcast shuru... (Message ID: #{msg_id_str})</b>", reply_markup=cancel_markup, parse_mode='HTML')
        
        count = 0
        blocked_count = 0
        failed_count = 0
        cancel_broadcast_flag = False
        
        active_users = list(users)
        last_pinned = settings.get("last_pinned_msgs", {})

        for user_id in active_users:
            if cancel_broadcast_flag: break
            try:
                if message.forward_from_chat or message.forward_from or message.forward_sender_name:
                    bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                else:
                    sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.messag
