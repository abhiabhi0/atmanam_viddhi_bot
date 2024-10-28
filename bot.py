from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

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
    excerpt = get_random_excerpt()
    
    # Format message with italic book title
    message = f"{excerpt['text']}\n\n_~ {excerpt['metadata']['title']}_"
    
    # Create keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("🔄 Need more Wisdom", callback_data='new_quote')],
        [InlineKeyboardButton("📚 Buy on Amazon", url=excerpt['metadata']['amazonLink'])] if excerpt['metadata'].get('amazonLink') else [],
        [InlineKeyboardButton("☕ Buy Me a Coffee", url="https://buymeacoffee.com/botman1001")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update, context):
    query = update.callback_query
    if query.data == 'new_quote':
        await query.answer()
        await send_excerpt(query, context)

def main():
    token = os.getenv('BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("wisdom", send_excerpt))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()