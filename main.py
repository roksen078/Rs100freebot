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
API_TOKEN = "8313028390:AAE-eD9JNnpXjxpFa8xxY_FvMUZDB_aoBj0"  # <--- Iske andar aapna BotFather wala Token paste kar dijiye!
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
            msg = "🟢 <b>Success Mode: ON</b>"
        else:
            settings["success_mode"] = False
            msg = "🔴 <b>Success Mode: OFF</b>"
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
        bot.reply_to(message, f"✅ <b>Link updated!</b>", parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['setsuccessphoto'])
def change_success_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["success_image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, f"✅ <b>Photo Link Updated!</b>", parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['clickstats'])
def show_click_stats(message):
    if message.from_user.id != ADMIN_ID: return
    clicks = load_clicks()
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    report = "📊 <b>LIVE BUTTON CLICKS REPORT</b>\n\n"
    for i, btn in enumerate(buttons):
        btn_id = f"btn_{i}"
        count = clicks.get(btn_id, 0)
        report += f"🔘 Button {i+1}: <b>{btn['text']}</b>\n🎯 Clicks: <code>{count}</code>\n\n"
    report += f"🎉 Claim Button Clicks: <code>{clicks.get('claim_btn_click', 0)}</code>\n"
    report += f"🔗 Success App Button Clicks: <code>{clicks.get('app_btn_click', 0)}</code>\n\n"
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, f"📊 <b>Bot Stats:</b>\n👥 Total Users: <code>{len(get_users())}</code>\n🚫 Banned: <code>{len(get_banned_users())}</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 Backup Database.")
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
        settings["auto_pin"] = (opt == 'on')
        save_settings(settings)
        bot.reply_to(message, f"📌 Auto-Pin Mode: {opt.upper()}")
    except: pass

@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        ban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> BAN ho gaya!", parse_mode='HTML')
    except: pass

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        unban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> UNBAN ho gaya!", parse_mode='HTML')
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
        bot.reply_to(message, "✅ Button updated!")
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
            bot.reply_to(message, "✅ Button deleted!")
    except: pass

@bot.message_handler(commands=['seterrortext'])
def change_error_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_err = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["error_text"] = new_err
        save_settings(settings)
        bot.reply_to(message, "✅ Error Text saved!")
    except: pass

@bot.message_handler(commands=['setprocesstext'])
def change_process_text_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_proc = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["process_text"] = new_proc
        save_settings(settings)
        bot.reply_to(message, "✅ Process Text saved!")
    except: pass

@bot.message_handler(commands=['settext'])
def change_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_text = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["text"] = new_text
        save_settings(settings)
        bot.reply_to(message, "✅ Welcome Text saved!")
    except: pass

@bot.message_handler(commands=['setphoto'])
def change_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1]
        settings = load_settings()
        settings["image"] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ Main Photo saved!")
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
    if message.from_user.id in get_banned_users():
        bot.send_message(message.chat.id, "❌ Banned.")
        return
    send_welcome(message)

# --- BROADCAST CANCEL HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast_callback(call):
    global cancel_broadcast_flag
    if call.from_user.id == ADMIN_ID:
        cancel_broadcast_flag = True
        bot.answer_callback_query(call.id, "Stopping process...")
        bot.edit_message_text("⚠️ <b>Broadcast Canceled!</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')

# --- SMART BROADCAST HANDLER ---
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_messages(message):
    global cancel_broadcast_flag
    users = get_users() 
    settings = load_settings()

    if message.from_user.id in get_banned_users(): return
    if settings["maintenance"] and message.from_user.id != ADMIN_ID: return

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
        bot.send_message(ADMIN_ID, f"🚀 <b>Broadcast started...</b>", reply_markup=cancel_markup, parse_mode='HTML')
        
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
        bot.send_message(ADMIN_ID, f"📢 <b>Dispatched Report:</b>\nSent: {count}\nBlocked: {blocked_count}", parse_mode='HTML')
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
    clicks = load_clicks()
    user_id = call.message.chat.id
    if call.data == "claim_code":
        clicks["claim_btn_click"] = clicks.get("claim_btn_click", 0) + 1
        save_clicks(clicks)
        bot.answer_callback_query(call.id, "⏳ Verifying...")
        proc_msg = bot.send_message(user_id, settings.get("process_text"), parse_mode='HTML')
        time.sleep(5)
        if settings.get("success_mode", False):
            success_markup = types.InlineKeyboardMarkup()
            success_markup.add(types.InlineKeyboardButton("🔗 Register/Claim Button", callback_data="click_success_app"))
            success_text = f"✅ <b>VERIFICATION SUCCESSFUL!</b>\n\n🎁 <b>Code: {settings.get('code')}</b>\n\n👇 <b>Click below to claim:</b>"
            try:
                bot.delete_message(
