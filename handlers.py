from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from utils import is_allowed
from config import FLASH_OPTIONS, PURCHASE_IMAGE_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show main menu or purchase flow"""
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await show_purchase_flow(update, context)
        return
    
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("⚡  Flash BTC", callback_data="flash_btc")],
        [InlineKeyboardButton("⚡  Flash USDT", callback_data="flash_usdt")],
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data="help")]
    ]
    await update.message.reply_text(
        "👋 *Welcome to Ace Crypto Flasher Bot!*\n\nSelect one of the options below.",
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode=ParseMode.MARKDOWN
    )

async def show_purchase_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display purchase image with flash package options"""
    keyboard = [
        [InlineKeyboardButton(FLASH_OPTIONS["1x"]["name"], url=FLASH_OPTIONS["1x"]["url"])],
        [InlineKeyboardButton(FLASH_OPTIONS["5x"]["name"], url=FLASH_OPTIONS["5x"]["url"])],
        [InlineKeyboardButton(FLASH_OPTIONS["10x"]["name"], url=FLASH_OPTIONS["10x"]["url"])],
        [InlineKeyboardButton(FLASH_OPTIONS["15x"]["name"], url=FLASH_OPTIONS["15x"]["url"])],
        [InlineKeyboardButton(FLASH_OPTIONS["20x"]["name"], url=FLASH_OPTIONS["20x"]["url"])],
        [InlineKeyboardButton(FLASH_OPTIONS["25x"]["name"], url=FLASH_OPTIONS["25x"]["url"])],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_photo(
        photo=PURCHASE_IMAGE_URL,
        caption="💎 *How many flash do you need?*\n\nSelect your desired flash package below:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input based on current step"""
    step = context.user_data.get('step')
    
    if step == "address":
        from transaction_handlers import get_address
        await get_address(update, context)
    elif step == "amount":
        from transaction_handlers import get_amount
        await get_amount(update, context)
    else:
        await update.message.reply_text("Please start with /start.")