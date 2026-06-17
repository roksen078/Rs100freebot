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
    except: return {}

def save_msg_log(data):
    with open(MSG_LOG_FILE, "w") as f: json.dump(data, f)

def load_clicks():
    try:
        with open(CLICK_FILE, "r") as f: return json.load(f)
    except: return {}

def save_clicks(data):
    with open(CLICK_FILE, "w") as f: json.dump(data, f)


# --- 🎯 DIRECT BOT & FORWARD BROADCAST SYSTEM (WITH AUTO LINK BUTTON) ---
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

    msg_text = message.text if message.text else message.caption
    urls = re.findall(r'(https?://\S+)', msg_text) if msg_text else []
    settings = load_settings()
    extracted_url = urls[0] if urls else settings.get("reg_link")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Register Link", url=extracted_url))

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

    for index, user_id in enumerate(users):
        if cancel_broadcast_flag:
            break
            
        try:
            if message.content_type == 'photo':
                sent_msg = bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=markup, parse_mode='HTML')
            elif message.content_type == 'text':
                sent_msg = bot.send_message(chat_id=user_id, text=message.text, reply_markup=markup, parse_mode='HTML')
            else:
                sent_msg = bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
                
            sent_msg_ids.append({"user_id": user_id, "msg_id": sent_msg.message_id})
            success_count += 1
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

    if cancel_broadcast_flag:
        report_text = "🛑 <b>Broadcast Cancelled by Admin!</b>\n\n" + report_text

    try:
        if status_msg:
            bot.delete_message(chat_id=ADMIN_ID, message_id=status_msg.message_id)
        bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode='HTML')
    except:
        bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode='HTML')

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
        bot.reply_to(message, f"✅ <b>Naya Application Link add ho gaya!</b>\n\nURL: <code>{new_link}</code>", parse_mode='HTML')
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
        bot.reply_to(message, "✅ <b>Success Mode ki Photo Link badal gayi!</b>", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format: <code>/setsuccessphoto [URL]</code>", parse_mode='HTML')

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
        report += f"🔘 Button {i+1}: <b>{btn['text']}</b>\nTotal Clicks: <code>{count}</code>\n\n"
        
    bc_count = clicks.get("broadcast_reg", 0)
    claim_count = clicks.get("claim_btn_click", 0)
    app_btn_count = clicks.get("app_btn_click", 0)
    
    report += f"📢 Broadcast Register Link Clicks: <code>{bc_count}</code>\n"
    report += f"🎉 Claim Button Clicks: <code>{claim_count}</code>\n"
    report += f"🔗 Success App Button Clicks: <code>{app_btn_count}</code>"
    
    bot.reply_to(message, report, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    banned = get_banned_users()
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👥 Total Active Users: <code>{len(users)}</code>\n🚫 Total Banned: <code>{len(banned)}</code>", parse_mode='HTML')

@bot.message_handler(commands=['export'])
def export_database(message):
    if message.from_user.id != ADMIN_ID: return
    users = get_users()
    with open("backup_users.txt", "w") as f:
        for u_id in users: f.write(f"{u_id}\n")
    with open("backup_users.txt", "rb") as doc:
        bot.send_document(message.chat.id, doc, caption="💾 <b>Aapka Users Database Backup File.</b>", parse_mode='HTML')
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
    except:
        bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['ban'])
def ban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        ban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> BAN ho gaya!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/ban ID`")

@bot.message_handler(commands=['unban'])
def unban_user_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        unban_user_id(target_id)
        bot.reply_to(message, f"✅ User <code>{target_id}</code> UNBAN ho gaya!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Use: `/unban ID`")
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
            msg = f"➕ Naya Button {len(buttons)} jodh diya gaya!"
            
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
        else:
            bot.reply_to(message, "❌ Is number ka koi button nahi hai.")
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
    except:
        bot.reply_to(message, "❌ Format galat hai.")

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
        bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['setcode'])
def change_code(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_code = message.text.split(maxsplit=1)[1].strip()
        settings = load_settings()
        settings["code"] = new_code
        save_settings(settings)
        bot.reply_to(message, f"✅ Code badal kar <b>{new_code}</b> ho gaya!", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ Format galat hai.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    panel_text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "📊 <code>/stats</code> | 📈 <code>/clickstats</code>\n"
        "📥 <code>/export</code> | 🛠 <code>/maintenance_on</code>\n"
        "🟢 <code>/maintenance_off</code> | 📌 <code>/setpin [on/off]</code>\n"
        "🚫 <code>/ban [ID]</code> | 🟢 <code>/unban [ID]</code>\n\n"
        "⚙️ <b>Smart Mode Switch:</b>\n"
        "🎛 <code>/switchmode [on/off]</code> - Toggle Code Mode\n"
        "🔗 <code>/setlink [URL]</code> - App Button Link\n"
        "🖼 <code>/setsuccessphoto [URL]</code> - Success Mode Photo\n\n"
        "🎛 <b>Buttons Control:</b>\n"
        "➕ <code>/addbutton [Num] [Naam] | [Link]</code>\n"
        "➖ <code>/delbutton [Num]</code>\n\n"
        "📝 <b>Texts Control:</b>\n"
        "⏳ <code>/setprocesstext [Text]</code>\n"
        "⚠️ <code>/seterrortext [Text]</code>\n"
        "📝 <code>/settext [Text]</code> | 🖼 <code>/setphoto [URL]</code>\n"
        "🎁 <code>/setcode [Code]</code>"
    )
    bot.send_message(message.chat.id, panel_text, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def handle_start(message):
    banned = get_banned_users()
    if message.from_user.id in banned:
        bot.send_message(message.chat.id, "❌ Aapko is bot se permanent BAN kar diya gaya hai.")
        return
    send_welcome(message)

def send_welcome(message):
    save_user(message.chat.id)
    settings = load_settings()
    buttons = settings.get("dynamic_buttons", [])
    
    markup = types.InlineKeyboardMarkup()
    row_btns = []
    
    for i, btn in enumerate(buttons):
        row_btns.append(types.InlineKeyboardButton(btn["text"], url=btn["url"]))
        if len(row_btns) == 2:
            markup.row(row_btns[0], row_btns[1])
            row_btns = []
    if row_btns: markup.row(row_btns[0])
    
    claim_btn = types.InlineKeyboardButton("🎁 Get My Free Code", callback_data="claim_code")
    markup.row(claim_btn)
    
    try: bot.send_photo(message.chat.id, settings.get("image"), caption=settings.get("text"), reply_markup=markup, parse_mode='HTML')
    except: bot.send_message(message.chat.id, settings.get("text"), reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global cancel_broadcast_flag
    settings = load_settings()
    clicks = load_clicks()
    user_id = call.message.chat.id
    
    if call.data == "cancel_broadcast":
        if call.from_user.id == ADMIN_ID:
            cancel_broadcast_flag = True
            bot.answer_callback_query(call.id, "🔴 Cancelling Broadcast...")
        else:
            bot.answer_callback_query(call.id, "❌ Aap admin nahi hain!", show_alert=True)
        return
        
    if call.data == "claim_code":
        clicks["claim_btn_click"] = clicks.get("claim_btn_click", 0) + 1
        save_clicks(clicks)
        
        bot.answer_callback_query(call.id, "⏳ Verifying your channels...")
        proc_msg = bot.send_message(user_id, settings.get("process_text"), parse_mode='HTML')
        
        time.sleep(5)
        
        if settings.get("success_mode", False):
            success_markup = types.InlineKeyboardMarkup()
            success_markup.add(types.InlineKeyboardButton("🔗 Register/Claim Button", url=settings.get("reg_link")))
            
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
            try:
                bot.edit_message_text(text=settings.get("error_text"), chat_id=user_id, message_id=proc_msg.message_id, parse_mode='HTML')
            except: pass
            
    elif call.data == "click_success_app":
        clicks["app_btn_click"] = clicks.get("app_btn_click", 0) + 1
        save_clicks(clicks)
        bot.answer_callback_query(call.id, url=settings.get("reg_link"))
        
    elif call.data == "click_bc_reg":
        clicks["broadcast_reg"] = clicks.get("broadcast_reg", 0) + 1
        save_clicks(clicks)
        bot.answer_callback_query(call.id, url=settings.get("reg_link"))

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
                                                                                                                                       
