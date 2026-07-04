import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

from handlers import start, handle_text
from callbacks import (
    ask_btc_address, ask_network, ask_address, 
    confirm_cancel, help
)

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    token = os.getenv('a')
    if not token:
        print("Error: BOT_TOKEN environment variable not set.")
        return
    
    application = Application.builder().token(token).build()
    
    # Command Handlers
    application.add_handler(CommandHandler('start', start))
    
    # Callback Query Handlers
    application.add_handler(CallbackQueryHandler(ask_btc_address, pattern='flash_btc'))
    application.add_handler(CallbackQueryHandler(ask_network, pattern='flash_usdt'))
    application.add_handler(CallbackQueryHandler(ask_address, pattern='network_.*'))
    application.add_handler(CallbackQueryHandler(confirm_cancel, pattern='confirm|cancel'))
    application.add_handler(CallbackQueryHandler(help, pattern='help'))
    
    # Message Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == '__main__':
    main()