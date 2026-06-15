import telebot
from telebot import types
import json
import os
import re
import time
from flask import Flask
from threading import Thread

# --- MINIMAL WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running safely!"

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT SETTINGS ---
API_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
ADMIN_ID = 1908832842  # Aapki Owner ID
CONNECTED_CHANNEL = -1002145879632

bot = telebot.TeleBot(API_TOKEN)

DB_FILE = "users.json"
SETTINGS_FILE = "settings.json"
MSG_LOG_FILE = "msg_log.json"
BAN_FILE = "banned_users.json"
CLICK_FILE = "clicks.json"

# FORCE RESET PURANI CRASHED FILES (Taaki koi data mismatch na ho)
if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, "r") as f:
            test_data = json.load(f)
            if "admins" in test_data:  # Agar purana admin kachra bacha hai, toh hatao
                os.remove(SETTINGS_FILE)
    except:
        os.remove(SETTINGS_FILE)

def init_file(name, default):
    if not os.path.exists(name) or os.stat(name).st_size == 0:
        with open(name, "w") as f:
            json.dump(default, f)

init_file(DB_FILE, [])
init_file(MSG_LOG_FILE, {})
init_file(BAN_FILE, [])
init_file(CLICK_FILE, {})

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
                return json.load(f)
        except: pass
    with open(SETTINGS_FILE, "w") as f:
        json.dump(default, f)
    return default

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)

def get_users():
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def save_users_list(users):
    with open(DB_FILE, "w") as f: json.dump(users, f)

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

# --- CHANNEL CHANNELS POST HANDLERS ---
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
        try:
            with open(MSG_LOG_FILE, "r") as f: logs = json.load(f)
        except: logs = {}
        logs[str(message.message_id)] = sent_msg_ids
        with open(MSG_LOG_FILE, "w") as f: json.dump(logs, f)

@bot.edited_channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_edited_channel_post(message):
    if message.chat.id == CONNECTED_CHANNEL:
        try:
            with open(MSG_LOG_FILE, "r") as f: logs = json.load(f)
        except: return
        ch_msg_id = str(message.message_id)
        if ch_msg_id in logs:
            for target in logs[ch_msg_id]:
                try:
                    if message.text:
                        bot.edit_message_text(text=message.text, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                    elif message.caption:
                        bot.edit_message_caption(caption=message.caption, chat_id=target["user_id"], message_id=target["msg_id"], parse_mode='HTML')
                except: pass

# --- CONTROLS COMMANDS (OWNER ONLY) ---
@bot.message_handler(commands=['switchmode'])
def toggle_success_mode(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        settings["success_mode"] = (opt == 'on')
        save_settings(settings)
        bot.reply_to(message, f"🟢 Success Mode: {'ON' if opt=='on' else 'OFF'}")
    except: pass

@bot.message_handler(commands=['setlink'])
def change_link(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_link = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["reg_link"] = new_link
        save_settings(settings)
        bot.reply_to(message, "✅ App Link Updated.")
    except: pass

@bot.message_handler(commands=['setsuccessphoto'])
def change_success_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["success_image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Success Photo Saved.")
    except: pass

@bot.message_handler(commands=['clickstats'])
def show_click_stats(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        with open(CLICK_FILE, "r") as f: clicks = json.load(f)
    except: clicks = {}
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    report = "📊 <b>LIVE REPORT</b>\n\n"
    for i, btn in enumerate(buttons):
        report += f"🔘 {btn['text']}: <code>{clicks.get(f'btn_{i}', 0)} Clicks</code>\n"
    report += f"\n🎉 Claim Button: <code>{clicks.get('claim_btn_click', 0)}</code>\n"
    report += f"🔗 Success App Button: <code>{clicks.get('app_btn_click', 0)}</code>\n"
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, f"👥 Users: <code>{len(get_users())}</code>\n🚫 Banned: <code>{len(get_banned_users())}</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Backup.")
    os.remove("backup_users.txt")

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = True
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance: ON 🔴")

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings["maintenance"] = False
    save_settings(settings)
    bot.reply_to(message, "🛠 Maintenance: OFF 🟢")

@bot.message_handler(commands=['setpin'])
def toggle_pin(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        settings["auto_pin"] = (opt == 'on')
        save_settings(settings)
        bot.reply_to(message, f"📌 Auto-Pin: {opt.upper()}")
    except: pass

@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        ban_user_id(target_id)
        bot.reply_to(message, f"✅ User {target_id} Banned.")
    except: pass

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        unban_user_id(target_id)
        bot.reply_to(message, f"✅ User {target_id} Unbanned.")
    except: pass

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
        if 0 <= btn_index < len(buttons): buttons[btn_index] = new_btn
        else: buttons.append(new_btn)
        settings["dynamic_buttons"] = buttons
        save_settings(settings)
        bot.reply_to(message, "✅ Button Updated!")
    except: pass

@bot.message_handler(commands=['delbutton'])
def del_button_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        btn_index = int(message.text.split()[1]) - 1
        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        if 0 <= btn_index < len(buttons):
            buttons.pop(btn_index)
            settings["dynamic_buttons"] = buttons
            save_settings(settings)
            bot.reply_to(message, "✅ Button Deleted.")
    except: pass

@bot.message_handler(commands=['seterrortext'])
def change_error_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_err = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["error_text"] = new_err
        save_settings(settings)
        bot.reply_to(message, "✅ Error text saved.")
    except: pass

@bot.message_handler(commands=['setprocesstext'])
def change_process_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_proc = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["process_text"] = new_proc
        save_settings(settings)
        bot.reply_to(message, "✅ Process text saved.")
    except: pass

@bot.message_handler(commands=['settext'])
def change_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome text saved.")
    except: pass

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome photo saved.")
    except: pass

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_code = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"🎁 Code set to: <b>{new_code}</b>", parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL (OWNER ONLY)</b>\n\n"
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
    if message.from_user.id in get_banned_users(): return
    send_welcome(message)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    global cancel_broadcast_flag
    if call.from_user.id == ADMIN_ID:
        cancel_broadcast_flag = True
        bot.answer_callback_query(call.id, "Halting transmission...")
        bot.edit_message_text("⚠️ <b>Broadcast Canceled!</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')

# --- SMART BROADCAST ENGINE ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    global cancel_broadcast_flag
    users = get_users() 
    settings = load_settings()
    if message.from_user.id in get_banned_users(): return
    if settings["maintenance"] and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 System Under Maintenance.")
        return
    if message.from_user.id == ADMIN_ID:
        if message.text and message.text.startswith('/'): return
        text_to_scan = message.text if message.text else (message.caption if message.caption else "")
        urls = re.findall(r'(https?://\S+)', text_to_scan)
        msg_id_str = str(message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Register Link", callback_data=f"click_bc_{msg_id_str}"))
        if urls:
            if "broadcast_links" not in settings: settings["broadcast_links"] = {}
            settings["broadcast_links"][msg_id_str] = urls[0]
            save_settings(settings)
        cancel_markup = types.InlineKeyboardMarkup()
        cancel_markup.add(types.InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast"))
        bot.send_message(message.chat.id, f"🚀 <b>Broadcast Started... (ID: #{msg_id_str})</b>", reply_markup=cancel_markup, parse_mode='HTML')
        count, blocked_count = 0, 0
        cancel_broadcast_flag = False
        last_pinned = settings.get("last_pinned_msgs", {})
        for user_id in list(users):
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
            except: pass
        save_users_list(users)
        settings["last_pinned_msgs"] = last_pinned
        save_settings(settings)
        bot.send_message(message.chat.id, f"📢 <b>REPORT:</b>\n\n✅ Sent: {count}\n❌ Blocked: {blocked_count}", parse_mode='HTML')
    else:
        if message.content_type == 'text' and message.text == "/start": send_welcome(message)

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
    markup.row(types.InlineKeyboardButton("🎉 Get My Free Code", callback_data="claim_code"))
    try: bot.send_photo(message.chat.id, settings.get("image"), caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')
    except: bot.send_photo(message.chat.id, "https://t.me/TG_Looters/3", caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data != "cancel_broadcast")
def callback_query(call):
    settings = load_settings()
    user_id = call.message.chat.id
    try:
        with open(CLICK_FILE, "r") as f: clicks = json.load(f)
    except: clicks = {}
    
    if call.data == "claim_code":
        clicks["claim_btn_click"] = clicks.get("claim_btn_click", 0) + 1
        with open(CLICK_FILE, "w") as f: json.dump(clicks, f)
        bot.answer_callback_query(call.id, "⏳ Verifying...")
        proc_msg = bot.send_message(user_id, settings.get("process_text"), parse_mode='HTML')
        time.sleep(5)
        if settings.get("success_mode", False):
            success_markup = types.InlineKeyboardMarkup()
            success_markup.add(types.InlineKeyboardButton("🔗 Register/Claim Button", callback_data="click_success_app"))
            success_text = f"✅ <b>VERIFICATION SUCCESSFUL!</b>\n\n🎁 <b>Code: {settings.get('code')}</b>\n\n👇 <b>Click below to claim:</b>"
            try:
                bot.delete_message(chat_id=user_id, message_id=proc_msg.message_id)
                bot.send_photo(chat_id=user_id, photo=settings.get("success_image"), caption=success_text, reply_markup=success_markup, parse_mode='HTML')
            except: pass
        else:
            try: bot.edit_message_text(text=settings.get("error_text"), chat_id=user_id, message_id=proc_msg.message_id, parse_mode='HTML')
            except: pass
    elif call.data == "click_success_app":
        clicks["app_btn_click"] = clicks.get("app_btn_click", 0) + 1
        with open(CLICK_FILE, "w") as f: json.
