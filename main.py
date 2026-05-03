import telebot
from telebot import types
import json
import os
from flask import Flask
from threading import Thread

# --- RENDER PORT ERROR FIX ---
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
API_TOKEN = '8313028390:AAG7ehvUNwn8JYuGvCFfJTLFkHUGbTKTF6g'
ADMIN_ID = 6363381640 
START_IMAGE_URL = "https://t.me/TECH_FUNDS_2/113" 

bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"

def get_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

@bot.message_handler(commands=['start'])
def start(message):
    users = get_users()
    if message.chat.id not in users:
        users.append(message.chat.id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)
    
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

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "claim_code":
        stylish_error = (
            "<b>⚠️ Aapne Join Nahi Kiya!</b>\n\n"
            "<b>Kripaya upar diye gaye dono channels join karein.</b>\n\n"
            "<b>📌 Zaruri: Dono channel ko pin 📌 karke rakho, tabhi code milega!</b>"
        )
        bot.send_message(call.message.chat.id, stylish_error, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    print("Bot is Running!")
    bot.infinity_polling()
    
