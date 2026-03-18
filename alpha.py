import telebot
import requests
import time
import threading
import os

# आपका टोकन
API_TOKEN = '8697332622:AAGDEbHpeoJIkT3lPks0PiuThWvLwF1PHN4'
bot = telebot.TeleBot(API_TOKEN)
USER_FILE = "users.txt"

# यूजर आईडी सेव करने का फंक्शन
def save_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, "w").close()
    
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

# सभी यूजर्स को प्रेडिक्शन भेजने का फंक्शन
def get_all_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return f.read().splitlines()
    return []

def get_game_data():
    try:
        ts = int(time.time() * 1000)
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts={ts}"
        res = requests.get(url, timeout=10).json()
        return res['data']['list'][0] if res and 'data' in res else None
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    bot.reply_to(message, "🚀 स्वागत है! अब आपको हर मिनट 'Jalwa Game' का ऑटोमैटिक प्रेडिक्शन मिलेगा।")

def start_auto_prediction():
    last_processed_period = ""
    while True:
        data = get_game_data()
        if data and data['issueNumber'] != last_processed_period:
            next_p = str(int(data['issueNumber']) + 1)
            last_n = int(data['number'])
            pred = "BIG 🟡" if last_n < 5 else "SMALL 🔵"
            msg = f"🚀 *AUTO PREDICTION*\n\n📅 Next Period: `{next_p[-5:]}`\n🔮 Forecast: *{pred}*\n📊 Last Result: {last_n}\n\n⚡ @AlphaDexterFF"
            
            users = get_all_users()
            for user_id in users:
                try:
                    bot.send_message(user_id, msg, parse_mode="Markdown")
                except:
                    pass # अगर किसी ने बॉट ब्लॉक किया हो
            
            last_processed_period = data['issueNumber']
        time.sleep(10)

threading.Thread(target=start_auto_prediction, daemon=True).start()

# Render के लिए एक छोटा सा वेब सर्वर (ताकि पोर्ट एरर न आए)
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

threading.Thread(target=run_web).start()

print("Multi-User Bot is running...")
bot.infinity_polling()
