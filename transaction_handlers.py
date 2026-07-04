from decimal import Decimal
from datetime import datetime
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from utils import validate_btc_address, validate_usdt_address, mask_address, random_tx_hash

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validate and store wallet address"""
    address = update.message.text.strip()
    currency = context.user_data.get('currency', None)
    
    if not currency:
        await update.message.reply_text("Please start with /start first.")
        return
    
    if currency == "btc":
        valid = validate_btc_address(address)
        if valid:
            context.user_data['address'] = address
            await update.message.reply_text(
                f"✅  BTC address recognized as *{valid.upper()}* format.\n\n"
                f"Please enter the *amount in USD* you wish to flash.",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['step'] = "amount"
        else:
            await update.message.reply_text(
                "❌  *Invalid BTC address!*\n\nPlease enter a valid BTC wallet address.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif currency == "usdt":
        network = context.user_data.get('network')
        if not network:
            await update.message.reply_text("Please select USDT network first.")
            return
        
        if validate_usdt_address(address, network):
            context.user_data['address'] = address
            await update.message.reply_text(
                f"✅  USDT address is *valid* for {network}.\n\n"
                f"Please enter the *amount in USD* you wish to flash.",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['step'] = "amount"
        else:
            await update.message.reply_text(
                f"❌  *Invalid USDT address!*\n\n"
                f"Please enter a valid wallet address for {network}.",
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        await update.message.reply_text("Unexpected step. Please start again with /start.")

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validate amount and show confirmation"""
    try:
        amount = Decimal(update.message.text.replace(",", ""))
        assert amount > 0
        context.user_data['amount'] = str(amount)
    except Exception:
        await update.message.reply_text(
            "❌  *Invalid amount!* Please enter a numeric amount in USD.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    currency = context.user_data['currency'].upper()
    address = context.user_data['address']
    network = context.user_data.get('network', 'N/A')
    masked_addr = mask_address(address)
    
    keyboard = [
        [InlineKeyboardButton("✅  Confirm", callback_data="confirm")],
        [InlineKeyboardButton("❌  Cancel", callback_data="cancel")]
    ]
    
    confirmation_text = (
        f"🔒 *Transaction Details*\n\n"
        f"*Currency*: {currency}\n"
        f"*Network*: {network}\n"
        f"*Address*: `{masked_addr}`\n"
        f"*Amount*: `${amount}`\n\n"
        f"_Review your details then confirm to proceed._"
    )
    
    await update.message.reply_text(
        confirmation_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data['step'] = "confirm"

async def process_transaction(query, context: ContextTypes.DEFAULT_TYPE):
    """Process confirmed transaction"""
    currency = context.user_data.get('currency', '').lower()
    network = context.user_data.get('network', '').upper()
    address = context.user_data.get('address', '')
    amount = context.user_data.get('amount', '0')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    tx_hash = random_tx_hash()
    
    # Generate explorer link based on currency/network
    if currency == "btc":
        tx_link = f"https://blockchair.com/bitcoin/transaction/{tx_hash}"
    elif currency == "usdt":
        if network == "TRC20":
            tx_link = f"https://tronscan.org/#/transaction/{tx_hash}"
        elif network == "ERC20":
            tx_link = f"https://etherscan.io/tx/{tx_hash}"
        elif network == "BEP20":
            tx_link = f"https://bscscan.com/tx/{tx_hash}"
        else:
            tx_link = "(unknown network)"
    else:
        tx_link = "(unknown currency)"
    
    confirmation_msg = (
        f"✅  *Transaction Successful!*\n\n"
        f"💸 *Amount*: ${amount}\n"
        f"🔗 *Transaction Hash*: `{tx_hash}`\n"
        f"🗂️ *Track*: [View on Explorer]({tx_link})\n"
        f"⏰  *Date*: {timestamp}\n\n"
        f"Your funds will reflect shortly. If not, please contact support!"
    )
    
    await query.edit_message_text(
        confirmation_msg,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
    context.user_data.clear()