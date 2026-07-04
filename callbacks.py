from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def ask_btc_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for Flash BTC button"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    context.user_data['currency'] = "btc"
    context.user_data['step'] = "address"
    
    await query.edit_message_text(
        "*Enter your BTC Wallet Address*:\n\nMake sure you copy the address correctly.",
        parse_mode=ParseMode.MARKDOWN
    )

async def ask_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for Flash USDT button"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    context.user_data['currency'] = "usdt"
    context.user_data['step'] = "network"
    
    keyboard = [
        [InlineKeyboardButton("TRC20", callback_data="network_TRC20")],
        [InlineKeyboardButton("ERC20", callback_data="network_ERC20")],
        [InlineKeyboardButton("BEP20", callback_data="network_BEP20")]
    ]
    
    await query.edit_message_text(
        "*Select USDT Network*:\n\nWhich USDT network would you like to use?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback for network selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("network_"):
        network = query.data.split("_")[1]
        context.user_data['network'] = network
        context.user_data['step'] = "address"
        
        await query.edit_message_text(
            f"*Enter your USDT {network} wallet address*:",
            parse_mode=ParseMode.MARKDOWN
        )

async def confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm/cancel actions"""
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "confirm":
        from transaction_handlers import process_transaction
        await process_transaction(query, context)
    else:
        await query.edit_message_text(
            "❌  *Transaction Cancelled.*\n\nYou can start again with /start.",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data.clear()

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    query = update.callback_query
    await query.answer()
    
    help_msg = (
        "ℹ️ *Crypto Flasher Pro Help*\n\n"
        "1. Use /start and select BTC or USDT (choose USDT network).\n"
        "2. Enter your wallet address and amount (USD).\n"
        "3. Confirm your transaction.\n\n"
        "💡 _All transactions are private and safe._\n"
        "For assistance or questions, [Contact Support](https://t.me/acetary).\n"
    )
    
    await query.edit_message_text(
        help_msg,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )