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
    t.daemon = True
    t.start()

# --- BOT SETTINGS ---
API_TOKEN = "8313028390:AAFBc5ELaeEg4LUi_oPzkOlmiCSKNdFDjzM"  # <-- Apna Bot Token yahan quotes ke andar daalein
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
        "admins": {str(ADMIN_ID): ["all"]},  # Admin permission database
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
            bot.reply_to(message, "❌ Galat permission type! Use: broadcast, buttons, settings, users, mode, all")
            return
        settings = load_settings()
        if "admins" not in settings: settings["admins"] = {}
        if target_id not in settings["admins"]: settings["admins"][target_id] = []
        if perm not in settings["admins"][target_id]:
            settings["admins"][target_id].append(perm)
        save_settings(settings)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> ko <b>{perm}</b> permission ke sath admin banaya gaya!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/addadmin [ID] [permission]`")

@bot.message_handler(commands=['removeadmin'])
def remove_admin_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = message.text.split()[1].strip()
        if target_id == str(ADMIN_ID):
            bot.reply_to(message, "❌ Aap khud ko admin se nahi hata sakte!")
            return
        settings = load_settings()
        if "admins" in settings and target_id in settings["admins"]:
            del settings["admins"][target_id]
            save_settings(settings)
            bot.reply_to(message, f"✅ User <code>{target_id}</code> ko admin pad se hata diya gaya.", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ Yeh ID admin list mein nahi hai.")
    except:
        bot.reply_to(message, "❌ Use: `/removeadmin [ID]`")

@bot.message_handler(commands=['adminlist'])
def view_admin_list(message):
    if not check_permission(message.from_user.id, "users"): return
    settings = load_settings()
    admins = settings.get("admins", {})
    msg = "👑 <b>BOT ADMINS & PERMISSIONS LIST:</b>\n\n"
    for u_id, perms in admins.items():
        perm_str = ", ".join(perms)
        is_owner = " (Supreme Owner)" if int(u_id) == ADMIN_ID else ""
        msg += f"👤 ID: <code>{u_id}</code>{is_owner}\n🛡 Permissions: <code>{perm_str}</code>\n\n"
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
        # --- CONTROLLABLE ADMIN COMMANDS WITH PERMISSION CHECK ---
@bot.message_handler(commands=['switchmode'])
def toggle_success_mode(message):
    if not check_permission(message.from_user.id, "mode"): return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        if opt == 'on':
            settings["success_mode"] = True
            msg = "🟢 <b>Success Mode: ON</b> (Ab photo + promo code dikhega!)"
        else:
            settings["success_mode"] = False
            msg = "🔴 <b>Success Mode: OFF</b> (Ab purana Error text hi dikhega!)"
        save_settings(settings)
        bot.reply_to(message, msg, parse_mode='HTML')
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
        bot.reply_to(message, f"✅ <b>App Link add ho gaya!</b>\nURL: <code>{new_link}</code>", parse_mode='HTML')
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
        bot.reply_to(message, f"✅ <b>Success Mode ki Photo Link badal gayi!</b>", parse_mode='HTML')
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
        count = clicks.get(btn_id, 0)
        report += f"🔘 Button {i+1}: <b>{btn['text']}</b>\n🎯 Total Clicks: <code>{count}</code>\n\n"
    report += f"🎉 Claim Button Clicks: <code>{clicks.get('claim_btn_click', 0)}</code>\n"
    report += f"🔗 Success App Button Clicks: <code>{clicks.get('app_btn_click', 0)}</code>\n\n"
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if not check_permission(message.from_user.id, "users"): return
    users = get_users()
    banned = get_banned_users()
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👥 Total Active Users: <code>{len(users)}</code>\n🚫 Total Banned Users: <code>{len(banned)}</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if not check_permission(message.from_user.id, "users"): return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Aapka Users Database Backup File.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if not check_permission(message.from_user.id, "settings"): return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: ON 🔴")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if not check_permission(message.from_user.id, "settings"): return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance Mode: OFF 🟢")
    @bot.message_handler(commands=['setpin'])
def toggle_pin(message):
    if not check_permission(message.from_user.id, "broadcast"): return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        settings["auto_pin"] = (opt == 'on')
        save_settings(settings)
        bot.reply_to(message, f"📌 Auto-Pin Mode: {opt.upper()}")
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
        bot.reply_to(message, "✅ Button successfully set/updated!")
    except: bot.reply_to(message, "❌ Use: `/addbutton [Number] [Naam] | [Link]`")

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
            clicks = load_clicks()
            if f"btn_{btn_index}" in clicks: clicks[f"btn_{btn_index}"] = 0
            save_clicks(clicks)
            bot.reply_to(message, f"✅ Button '{removed['text']}' deleted!")
        else: bot.reply_to(message, "❌ Button not found.")
    except: bot.reply_to(message, "❌ Use: `/delbutton [Number]`")

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
    except: pass

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Photo updated!")
    except: pass

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if not check_permission(message.from_user.id, "settings"): return
    try:
        new_code = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Code badal kar <b>{new_code}</b> ho gaya!", parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not check_permission(message.from_user.id, "broadcast") and not check_permission(message.from_user.id, "buttons") and not check_permission(message.from_user.id, "settings") and not check_permission(message.from_user.id, "users") and not check_permission(message.from_user.id, "mode"): return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "👑 <b>Admin Management (Owner Only):</b>\n"
        "➕ <code>/addadmin [ID] [permission]</code>\n"
        "➖ <code>/removeadmin [ID]</code>\n"
        "📋 <code>/adminlist</code> - View current admins\n\n"
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
    send_welcome(message)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    global cancel_broadcast_flag
    if check_permission(call.from_user.id, "broadcast"):
        cancel_broadcast_flag = True
        bot.answer_callback_query(call.id, "Stopping process...")
        bot.edit_message_text("⚠️ <b>Broadcast Canceled by Admin!</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    global cancel_broadcast_flag
    users = get_users() 
    settings = load_settings()
    banned = get_banned_users()
    if message.from_user.id in banned: return
    if (settings["maintenance"] and not check_permission(message.from_user.id, "settings")):
        bot.send_message(message.chat.id, "🛠 Bot Maintenance Mode Me Hai.")
        return
    if check_permission(message.from_user.id, "broadcast"):
        if message.text and message.text.startswith('/'): return
        text_to_scan = message.text if message.text else (message.caption if message.caption else "")
        urls = re.findall(r'(https?://\S+)', text_to_scan)
        msg_id_str = str(message.message_id)
        markup = types.InlineKeyboardMarkup()
        register_btn = types.InlineKeyboardButton("Register Link", callback_data=f"click_bc_{msg_id_str}")
        markup.add(register_btn)
        if urls:
            if "broadcast_links" not in settings: settings["broadcast_links"] = {}
            settings["broadcast_links"][msg_id_str] = urls[0]
            save_settings(settings)
        cancel_markup = types.InlineKeyboardMarkup()
        cancel_btn = types.InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast")
        cancel_markup.add(cancel_btn)
        bot.send_message(message.chat.id, f"🚀 <b>{len(users)} users ko broadcast shuru... (Message ID: #{msg_id_str})</b>", reply_markup=cancel_markup, parse_mode='HTML')
        count, blocked_count, failed_count = 0, 0, 0
        cancel_broadcast_flag = False
        active_users = list(users)
        last_pinned = settings.get("last_pinned_msgs", {})
        for user_id in active_users:
            if cancel_broadcast_flag: break
            try:
                if message.forward_from_chat or message.forward_from or message.forward_sender_name:
                    bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                else:
                    sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
                    if settings.get("auto_pin", True):
                        if str(user_id) in last_pinned:
                            try: bot.unpin_chat_message(chat_id=user_id, message_id=last_pinned[str(user_id)])
                            except: pass
                        try:
                            bot.pin_chat_message(chat_id=user_id, message_id=sent_msg.message_id, disable_notification=True)
                            last_pinned[str(user_id)] = sent_msg.message_id
                        except: pass
                count += 1
            except telebot.api_helper.ApiTelegramException as ex:
                if ex.error_code == 403:
                    blocked_count += 1
                    if user_id in users: users.remove(user_id)
                else: failed_count += 1
            except: failed_count += 1
        save_users_list(users)
        settings["last_pinned_msgs"] = last_pinned
        save_settings(settings)
        report_text = (
            "📢 <b>BROADCAST DELIVERY REPORT</b>\n\n"
            f"✅ Successfully Sent: <code>{count}</code> users\n"
            f"❌ Blocked/Kicked: <code>{blocked_count}</code> users\n"
            f"⚠️ Failed/Error: <code>{failed_count}</code> users\n\n"
            f"📊 Remaining Active Users: <code>{len(users)}</code>"
        )
        if cancel_broadcast_flag: report_text = "⚠️ <b>Broadcast Canceled Midway!</b>\n\n" + report_text
        bot.send_message(message.chat.id, report_text, parse_mode='HTML')
    else:
        if message.content_type == 'text' and message.text == "/start":
            send_welcome(message)

def send_welcome(message):
    save_user(message.chat.id)
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    markup = types.InlineKeyboardMarkup()
    row_btns = []
    for i, btn in enumerate(buttons):
        row_btns.append(types.InlineKeyboardButton(btn["text"], callback_data=f"track_click_{i}"))
        if len(row_btns) == 2:
            markup.row(row_btns[0], row_btns[1])
            row_btns = []
    if row_btns: markup.row(row_btns[0])
    claim_btn = types.InlineKeyboardButton("🎉 Get My Free Code", callback_data="claim_code")
    markup.row(claim_btn)
    try: bot.send_photo(message.chat.id, settings.get("image"), caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')
    except: bot.send_message(message.chat.id, settings.get("text"), reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data != "cancel_broadcast")
def callback_query(call):
    settings = load_settings()
    clicks = load_clicks()
    user_id = call.message.chat.id
    if call.data == "claim_code":
        clicks["claim_btn_click"] = clicks.get("claim_btn_click", 0) + 1
        save_clicks(clicks)
        bot.answer_callback_query(call.id, "⏳ Verifying your channels...")
        proc_msg = bot.send_message(user_id, settings.get("process_text"), parse_mode='HTML')
        time.sleep(5)
        if settings.get("success_mode", False):
            success_markup = types.InlineKeyboardMarkup()
            success_markup.add(types.InlineKeyboardButton("🔗 Register/Claim Button", callback_data="click_success_app"))
            success_text = (
                "✅ <b>VERIFICATION SUCCESSFUL!</b>\n\n"
                f"🎁 <b>Code: {settings.get('code')}</b>\n\n"
                "👇 <b>Click below to claim:</b>"
            )
            try:
                bot.delete_message(chat_id=user_id, message_id=proc_msg.message_id)
                bot.send_photo(chat_id=user_id, photo=settings.get("success_image"), caption=success_text, reply_markup=success_markup, parse_mode='HTML')
            except: pass
        else:
            try: bot.edit_message_text(text=settings.get("error_text"), chat_id=user_id, message_id=proc_msg.message_id, parse_mode='HTML')
            except: pass
    elif call.data == "click_success_app":
        clicks["app_btn_click"] = clicks.get("app_btn_click", 0) + 1
        save_clicks(clicks)
        bot.answer_callback_query(call.id, url=settings.get("reg_link"))
    elif call.data.startswith("click_bc_"):
        msg_id_str = call.data.split("_")[2]
        click_key = f"bc_msg_{msg_id_str}"
        clicks[click_key] = clicks.get(click_key, 0) + 1
        save_clicks(clicks)
        bc_links = settings.get("broadcast_links", {})
        target_url = bc_links.get(msg_id_str, settings.get("reg_link"))
        bot.answer_callback_query(call.id, url=target_url)
    elif call.data.startswith("track_click_"):
        btn_index = int(call.data.split("_")[2])
        buttons = settings.get("dynamic_buttons", [])
        if 0 <= btn_index < len(buttons):
            btn_id = f"btn_{btn_index}"
            clicks[btn_id] = clicks.get(btn_id, 0) + 1
            save_clicks(clicks)
            bot.answer_callback_query(call.id, url=buttons[btn_index]["url"])

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
