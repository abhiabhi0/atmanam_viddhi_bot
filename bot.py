from telegram.ext import Application, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import random
import json
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import pytz
import pathlib

load_dotenv()

# Store last command timestamps for individual users
user_last_command = {}
COOLDOWN_SECONDS = 10

async def start(update, context):
    welcome_message = "Welcome, Seeker! 🌱 You've entered a space dedicated to exploring the essence of truth and self-understanding. 💫 Use /enlighten to receive a dose of timeless wisdom curated for seekers like you."
    await update.message.reply_text(welcome_message)

def create_log_entry(user_info):
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    
    # Create logs directory if it doesn't exist
    log_dir = pathlib.Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with today's date
    log_file = log_dir / f"{current_time.strftime('%Y-%m-%d')}.log"
    
    log_entry = f"[{current_time.strftime('%Y-%m-%d %H:%M:%S IST')}] User: {user_info['username']}, ID: {user_info['user_id']}, Chat ID: {user_info['chat_id']}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)

def get_random_excerpt():
    repo_url = "https://raw.githubusercontent.com/atmanamviddhi/atmanamviddhi.github.io"
    files_url = f"{repo_url}/main/excerpts/files.json"
    
    response = requests.get(files_url)
    files = response.json()
    
    random_file = random.choice(files)
    excerpt_url = f"{repo_url}/main/excerpts/{random_file}"
    
    excerpt_response = requests.get(excerpt_url)
    excerpt_data = excerpt_response.json()
    
    random_index = random.randrange(len(excerpt_data['excerpts']))
    random_excerpt = excerpt_data['excerpts'][random_index]
    random_excerpt['metadata'] = excerpt_data['metadata']
    
    return random_excerpt

BOT_USERNAME = "@wisdom\\_whisperer\\_bot"
channel_name = "atmanam\\_viddhi"
insta_url = "https://www.instagram.com/atmanam.viddhi"
fb_url = "https://www.facebook.com/atmanam.viddhi"

async def send_excerpt(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Unknown"
    chat_id = update.message.chat_id
    
    user_info = {
        'username': username,
        'user_id': user_id,
        'chat_id': chat_id
    }
    create_log_entry(user_info)
    
    current_time = time.time()
    
    if user_id in user_last_command:
        time_passed = current_time - user_last_command[user_id]
        if time_passed < COOLDOWN_SECONDS:
            time_left = int(COOLDOWN_SECONDS - time_passed)
            await update.message.reply_text(f"Please wait {time_left} seconds before requesting another wisdom.")
            return

    user_last_command[user_id] = current_time
    excerpt = get_random_excerpt()
    
    # First message with the excerpt
    message = f"{excerpt['text']}\n\n_~ {excerpt['metadata']['title']}_\n\n{BOT_USERNAME}"
    await update.message.reply_text(
        text=message,
        parse_mode='Markdown'
    )    # Second message with the buttons
    keyboard = [
        [InlineKeyboardButton("📚 Buy on Amazon", url=excerpt['metadata']['amazonLink'])] if excerpt['metadata'].get('amazonLink') else [],
        [InlineKeyboardButton("☕ Buy Me a Coffee", url="https://buymeacoffee.com/botman1001")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
    text=f"_Type /enlighten again after 10 seconds for more wisdom._\n\nJoin our channel: @{channel_name}\nFollow us on [Instagram]({insta_url}) and [Facebook]({fb_url})",
    reply_markup=reply_markup,
    parse_mode='Markdown'
)

    
def main():
    token = os.getenv('BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("enlighten", send_excerpt))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()