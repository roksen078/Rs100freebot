import telebot
from telebot import types
import json
import os

# --- SETTINGS ---
API_TOKEN = '8313028390:AAG7ehvUNwn8JYuGvCFfJTLFkHUGbTKTF6g'
ADMIN_ID = 1908832842 
START_IMAGE_URL = "https://t.me/TECH_FUNDS_2/113" 

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"

def get_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    users = get_users()
    if message.chat.id not in users:
        users.append(message.chat.id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)
    
    # HTML use karke bold kiya hai <b> tag se
    welcome_text = (
        "<b>🎉 Join Official Big Promo Code Channel</b>\n\n"
        "<b>📅 Daily FREE BIG CODE</b>\n\n"
        "<b>👇 Join our channels below and claim your code!</b>"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Join Channel 👇", url="https://t.me/+uLvuR0wfZ6c5Yzdl")
    btn2 = types.InlineKeyboardButton("Join Channel 👇", url="https://t.me/+tmxMobgZYe82ZmNl")
    claim_btn = types.InlineKeyboardButton("🎁 Claim Code", callback_data="claim_code")
    
    markup.row(btn1, btn2)
    markup.row(claim_btn)
    
    try:
        bot.send_photo(message.chat.id, START_IMAGE_URL, caption=welcome_text, reply_markup=markup, parse_mode='HTML')
    except:
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')

# --- UNIVERSAL BROADCAST ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_broadcast(message):
    if message.chat.id == ADMIN_ID:
        users = get_users()
        count = 0
        bot.send_message(ADMIN_ID, "<b>🚀 Broadcasting started...</b>", parse_mode='HTML')
        for user in users:
            try:
                bot.copy_message(chat_id=user, from_chat_id=ADMIN_ID, message_id=message.message_id)
                count += 1
            except:
                pass
        bot.send_message(ADMIN_ID, f"<b>✅ Done! {count} users ko bhej diya gaya.</b>", parse_mode='HTML')

# --- CLAIM BUTTON HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "claim_code":
        bot.answer_callback_query(call.id, text="Checking subscription...", show_alert=False)
        
        # HTML Stylish Error Message (Poora Bold)
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye dono channels join karein.</b>\n\n"
            "<b>📌 Zaruri: Dono channel ko pin 📌 karke rakho, tabhi code milega!</b>"
        )
        bot.send_message(call.message.chat.id, stylish_error, parse_mode='HTML')

print("Bot is Running with HTML Bold Mode!")
bot.infinity_polling()
