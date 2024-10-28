from telegram.ext import Application, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import random
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Store last command timestamp
last_command_time = 0
COOLDOWN_SECONDS = 10

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

async def send_excerpt(update, context):
    global last_command_time
    current_time = time.time()
    
    if current_time - last_command_time < COOLDOWN_SECONDS:
        time_left = int(COOLDOWN_SECONDS - (current_time - last_command_time))
        await update.message.reply_text(f"Please wait {time_left} seconds before requesting another wisdom.")
        return

    last_command_time = current_time
    excerpt = get_random_excerpt()
    
    message = f"{excerpt['text']}\n\n_~ {excerpt['metadata']['title']}_\n\n_Type /wisdom again after 10 seconds for more wisdom._"
    
    keyboard = [
        [InlineKeyboardButton("📚 Buy on Amazon", url=excerpt['metadata']['amazonLink'])] if excerpt['metadata'].get('amazonLink') else [],
        [InlineKeyboardButton("☕ Buy Me a Coffee", url="https://buymeacoffee.com/botman1001")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    token = os.getenv('BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("wisdom", send_excerpt))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()