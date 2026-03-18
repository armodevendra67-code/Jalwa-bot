import telebot
import requests
import time
import threading
import os
from flask import Flask

# आपका टेलीग्राम टोकन
API_TOKEN = '8697332622:AAGDEbHpeoJIkT3lPks0PiuThWvLwF1PHN4'
bot = telebot.TeleBot(API_TOKEN)
USER_FILE = "users.txt"

# आपकी चैट आईडी
ADMIN_IDS = ['6816515814']

def save_user(user_id):
    user_id = str(user_id)
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f: pass
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if user_id not in users:
        with open(USER_FILE, "a") as f:
            f.write(user_id + "\n")

def get_all_users():
    users = set(ADMIN_IDS)
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            users.update(f.read().splitlines())
    return list(users)

def get_game_data():
    try:
        # नया वर्किंग API URL
        url = "https://api.91clubapi.com/api/webapi/GetNoaverageEmerdList"
        payload = {
            "typeId": 1,
            "customerrId": 20000,
            "isFirst": 0,
            "pageNo": 1,
            "pageSize": 10
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*"
        }
        res = requests.post(url, json=payload, headers=headers, timeout=10).json()
        if res and res.get('data') and res['data'].get('list'):
            item = res['data']['list'][0]
            return {
                'issueNumber': item['issueNumber'],
                'number': item['number']
            }
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    bot.reply_to(message, "🚀 *Jalwa Game Bot* अब एक्टिव है!\n\nअब आपको हर मिनट प्रेडिक्शन मिलता रहेगा।", parse_mode="Markdown")

def start_auto_prediction():
    last_processed_period = ""
    while True:
        try:
            data = get_game_data()
            if data and data['issueNumber'] != last_processed_period:
                next_p = str(int(data['issueNumber']) + 1)
                last_n = int(data['number'])
                pred = "BIG 🟡" if last_n >= 5 else "SMALL 🔵"
                
                msg = f"🚀 *AUTO PREDICTION*\n\n📅 Next Period: `{next_p}`\n🔮 Forecast: *{pred}*\n📊 Last Result: {last_n}\n\n⚡ @AlphaDexterFF"
                
                users = get_all_users()
                for user_id in users:
                    try:
                        bot.send_message(user_id, msg, parse_mode="Markdown")
                    except:
                        continue
                last_processed_period = data['issueNumber']
            time.sleep(15) # 15 सेकंड बाद फिर चेक करेगा
        except:
            time.sleep(5)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=start_auto_prediction, daemon=True).start()
    threading.Thread(target=run_web, daemon=True).start()
    bot.infinity_polling()
    
