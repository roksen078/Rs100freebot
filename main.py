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
API_TOKEN = "8313028390:AAF_6FaXiLndJSvAmSt8Zhc1v1R_Wilssp0"
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
# --- 🎯 DIRECT BOT & FORWARD BROADCAST SYSTEM (WITH CONDITIONAL BUTTON & AUTO-PIN) ---
@bot.message_handler(func=lambda msg: msg.chat.id == ADMIN_ID and (not msg.text.startswith('/') if msg.text else True), content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_bot_direct_broadcast(message):
    global cancel_broadcast_flag
    users = get_users()
    total_users = len(users)
    sent_msg_ids = []
    success_count = 0
    blocked_count = 0
    failed_count = 0
    cancel_broadcast_flag = False
    # Check if the post has any links
    msg_text = message.text if message.text else message.caption
    urls = re.findall(r'(https?://\S+)', msg_text) if msg_text else []
    
    markup = None
    # Register button sirf tabhi aayega jab message mein link milega
    if urls:
        first_url = urls[0]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔗 Register Link", url=first_url))

    status_markup = types.InlineKeyboardMarkup()
    status_markup.add(types.InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast"))
    
    try:
        status_msg = bot.send_message(
            chat_id=ADMIN_ID, 
            text=f"🚀 <b>{total_users} users ko broadcast shuru...</b>", 
            reply_markup=status_markup, 
            parse_mode='HTML'
        )
    except:
        status_msg = None

    # Determine if it's a forwarded message
    is_forwarded = message.forward_from or message.forward_from_chat or message.forward_date

    for index, user_id in enumerate(users):
        if cancel_broadcast_flag:
            break
            
        try:
            # Agar message forward kiya hua hai, toh forward hi jayega header ke sath
            if is_forwarded:
                sent_msg = bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                if markup:
                    try: bot.delete_message(chat_id=user_id, message_id=sent_msg.message_id)
                    except: pass
                    sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
            else:
                # Agar normal message hai bina forward ke
                if message.content_type == 'photo':
                    sent_msg = bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=markup, parse_mode='HTML')
                elif message.content_type == 'text':
                    sent_msg = bot.send_message(chat_id=user_id, text=message.text, reply_markup=markup, parse_mode='HTML')
                else:
                    sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
                
            sent_msg_ids.append({"user_id": user_id, "msg_id": sent_msg.message_id})
            success_count += 1
            
            # --- 📌 AUTO UNPIN PURANA & PIN NAYA SYSTEM ---
            settings = load_settings()
            if settings.get("auto_pin", True):
                try: bot.unpin_chat_message(chat_id=user_id, message_id=None)
                except: pass
                try: bot.pin_chat_message(chat_id=user_id, message_id=sent_msg.message_id, disable_notification=True)
                except: pass
                
        except telebot.api_helper.ApiTelegramException as e:
            if e.error_code == 403:
                blocked_count += 1
                if user_id in users:
                    users.remove(user_id)
            else:
                failed_count += 1
        except:
            failed_count += 1

        if status_msg and index % 10 == 0:
            try:
                bot.edit_message_text(
                    chat_id=ADMIN_ID,
                    message_id=status_msg.message_id,
                    text=f"🚀 <b>Broadcast in progress... ({success_count}/{total_users})</b>",
                    reply_markup=status_markup,
                    parse_mode='HTML'
                )
            except: pass

    if blocked_count > 0:
        save_users_list(users)

    remaining_users = total_users - (success_count + blocked_count + failed_count)
    
    report_text = (
        "📢 <b>BROADCAST DELIVERY REPORT</b>\n\n"
        f"✅ Successfully Sent: {success_count} users\n"
        f"❌ Blocked/Kicked: {blocked_count} users (Database cleaned)\n"
        f"⚠️ Failed/Error: {failed_count} users\n\n"
        f"📊 Remaining Active Users: {remaining_users}"
    )
    logs = load_msg_log()
    logs[str(message.message_id)] = sent_msg_ids
    save_msg_log(logs)
# --- ADMIN COMMANDS HANDLERS ---
@bot.message_handler(commands=['switchmode'])
def toggle_success_mode(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        if opt == 'on':
            settings['success_mode'] = True
            msg = "🟢 <b>Success Mode: ON</b> (Ab timer ke baad Photo + Promo Code + Register Button dikhega!)"
        else:
            settings['success_mode'] = False
            msg = "🔴 <b>Success Mode: OFF</b> (Ab timer ke baad purana Error text hi dikhega!)"
        save_settings(settings)
        bot.reply_to(message, msg, parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/switchmode [on/off]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setlink'])
def change_link(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_link = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['reg_link'] = new_link
        save_settings(settings)
        bot.reply_to(message, f"✅ <b>Naya Application Link add ho gaya!</b>\n\n🔗 <code>{new_link}</code>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setlink [Link]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setsuccessphoto'])
def change_success_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_photo = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['success_image'] = new_photo
        save_settings(settings)
        bot.reply_to(message, "✅ <b>Success Mode ki Photo Link badal gayi!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setsuccessphoto [URL]</code>", parse_mode='HTML')
        @bot.message_handler(commands=['clickstats'])
def show_click_stats(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    clicks = load_clicks()
    report = "📊 <b>LIVE BUTTON CLICKS REPORT</b>\n\n"
    for i, btn in enumerate(buttons):
        btn_id = f"btn_{i}"
        count = clicks.get(btn_id, 0)
        report += f"🔘 <b>{btn['text' PJ]}</b>\nTotal Clicks: <code>{count}</code>\n\n"
    bc_count = clicks.get('broadcast_reg', 0)
    claim_count = clicks.get('claim_btn_click', 0)
    app_btn_count = clicks.get('app_btn_click', 0)
    report += f"🚀 Broadcast Register Link Clicks: <code>{bc_count}</code>\n"
    report += f"🎁 Claim Button Clicks: <code>{claim_count}</code>\n"
    report += f"📲 Success App Button Clicks: <code>{app_btn_count}</code>"
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    banned = get_banned_users()
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👥 Total Active Users: <code>{len(users)}</code>\n🚫 Total Banned: <code>{len(banned)}</code>", parse_mode='HTML')

@bot.message_handler(commands=['maintenance_on'])
def maintenance_on(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings['maintenance'] = True
    save_settings(settings)
    bot.reply_to(message, "⚙️ <b>Maintenance Mode turned ON!</b>", parse_mode='HTML')

@bot.message_handler(commands=['maintenance_off'])
def maintenance_off(message):
    if message.from_user.id != ADMIN_ID: return
    settings = load_settings()
    settings['maintenance'] = False
    save_settings(settings)
    bot.reply_to(message, "✅ <b>Maintenance Mode turned OFF!</b>", parse_mode='HTML')

@bot.message_handler(commands=['setpin'])
def set_pin_config(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        opt = message.text.split(maxsplit=1)[1].strip().lower()
        settings = load_settings()
        if opt == 'on':
            settings['auto_pin'] = True
            msg = "📌 <b>Auto-Pin feature turned ON!</b>"
        else:
            settings['auto_pin'] = False
            msg = "📌 <b>Auto-Pin feature turned OFF!</b>"
        save_settings(settings)
        bot.reply_to(message, msg, parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setpin [on/off]</code>", parse_mode='HTML')
        @bot.message_handler(commands=['ban'])
def ban_user_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        user_id = int(message.text.split(maxsplit=1)[1].strip())
        ban_user_id(user_id)
        bot.reply_to(message, f"🚫 User <code>{user_id}</code> has been banned.")
    except:
        bot.reply_to(message, "⚠️ Format: <code>/ban [ID]</code>", parse_mode='HTML')

@bot.message_handler(commands=['unban'])
def unban_user_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        user_id = int(message.text.split(maxsplit=1)[1].strip())
        unban_user_id(user_id)
        bot.reply_to(message, f"🟢 User <code>{user_id}</code> has been unbanned.")
    except:
        bot.reply_to(message, "⚠️ Format: <code>/unban [ID]</code>", parse_mode='HTML')

@bot.message_handler(commands=['addbutton'])
def add_custom_button(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split(maxsplit=3)
        num = int(parts[1])
        name = parts[2]
        link = parts[3]
        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        new_btn = {"text": name, "url": link}
        if num <= len(buttons):
            buttons[num-1] = new_btn
        else:
            buttons.append(new_btn)
        settings["dynamic_buttons"] = buttons
        save_settings(settings)
        bot.reply_to(message, f"➕ Button {num} added: <b>{name}</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/addbutton [Num] [Naam] [Link]</code>", parse_mode='HTML')

@bot.message_handler(commands=['delbutton'])
def del_custom_button(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        num = int(message.text.split(maxsplit=1)[1].strip())
        settings = load_settings()
        buttons = settings.get("dynamic_buttons", [])
        if 0 < num <= len(buttons):
            removed = buttons.pop(num-1)
            settings["dynamic_buttons"] = buttons
            save_settings(settings)
            bot.reply_to(message, f"➖ Button deleted: <b>{removed['text']}</b>", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ Invalid Button number!")
    except:
        bot.reply_to(message, "⚠️ Format: <code>/delbutton [Num]</code>", parse_mode='HTML')
        @bot.message_handler(commands=['setprocesstext'])
def set_process_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        text = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['process_text'] = text
        save_settings(settings)
        bot.reply_to(message, "📝 <b>Process text updated!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setprocesstext [Text]</code>", parse_mode='HTML')

@bot.message_handler(commands=['seterrortext'])
def set_error_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        text = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['error_text'] = text
        save_settings(settings)
        bot.reply_to(message, "⚠️ <b>Error text updated!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/seterrortext [Text]</code>", parse_mode='HTML')

@bot.message_handler(commands=['settext'])
def set_main_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        text = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['text'] = text
        save_settings(settings)
        bot.reply_to(message, "📝 <b>Main Text updated!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/settext [Text]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setphoto'])
def set_main_photo(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        url = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['image'] = url
        save_settings(settings)
        bot.reply_to(message, "🖼️ <b>Main Photo URL updated!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setphoto [URL]</code>", parse_mode='HTML')

@bot.message_handler(commands=['setcode'])
def set_promo_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        code = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings['code'] = code
        save_settings(settings)
        bot.reply_to(message, f"🎁 <b>Promo Code updated to:</b> <code>{code}</code>", parse_mode='HTML')
    except:
        bot.reply_to(message, "⚠️ Format: <code>/setcode [Code]</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        users = get_users()
        with open("users_export.txt", "w") as f:
            for u in users:
                f.write(f"{u}\n")
        with open("users_export.txt", "rb") as f:
            bot.send_document(message.chat.id, f, caption="📊 <b>Total Active Users Export Database</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Export failed!")
        
