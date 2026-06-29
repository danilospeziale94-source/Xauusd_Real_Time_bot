import os
import telebot
import yfinance as yf
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

timeframes = {
    "M5": "5m", "M15": "15m", "M30": "30m",
    "H1": "60m", "H4": "240m", "Daily": "1d"
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=3)
    for tf in timeframes.keys():
        markup.add(InlineKeyboardButton(tf, callback_data=tf))
    bot.send_message(message.chat.id, "Seleziona timeframe per analizzare XAUUSD:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def analyze(call):
    tf = call.data
    interval = timeframes[tf]
    
    data = yf.download("GC=F", period="5d", interval=interval, progress=False)
    if data.empty:
        bot.edit_message_text("❌ Errore dati", call.message.chat.id, call.message.message_id)
        return

    last = data.iloc[-1]
    price = last['Close']

    text = f"""
<b>📊 XAUUSD - {tf}</b>
🕒 Ultimo aggiornamento: {data.index[-1]}

<b>Prezzo:</b> <b>{price:.2f} $</b>

<b>Analisi semplice:</b>
- Ultimo massimo: {data['High'].max():.2f}
- Ultimo minimo: {data['Low'].min():.2f}
- Variazione 24h: {((price / data.iloc[-2]['Close'] - 1) * 100):+.2f}%

Prossima analisi in arrivo...
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML')

print("🚀 XAUUSD Bot avviato!")
bot.infinity_polling()