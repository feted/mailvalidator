import re
import logging
import eth_utils

def load_users():
    """Load authorized users from file"""
    try:
        with open("user.txt", "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logging.error(f"Error loading users: {e}")
        return []

def is_allowed(user_id):
    """Check if user is authorized"""
    return str(user_id) in load_users()

def validate_btc_address(address):
    """Validate Bitcoin address format"""
    segwit_pattern = r'^[3][a-km-zA-HJ-NP-Z1-9]{25,39}$'
    non_segwit_pattern = r'^[1][a-km-zA-HJ-NP-Z1-9]{25,34}$'
    bech32_pattern = r'^(bc1)[a-zA-HJ-NP-Z0-9]{25,39}$'
    
    if re.match(bech32_pattern, address):
        return "bech32"
    elif re.match(segwit_pattern, address):
        return "segwit"
    elif re.match(non_segwit_pattern, address):
        return "non-segwit"
    return False

def validate_trc20_address(address):
    """Validate TRON (TRC20) address format"""
    trc20_pattern = r'^T[a-zA-Z0-9]{33}$'
    return bool(re.match(trc20_pattern, address))

def validate_usdt_address(address, network):
    """Validate USDT address for specified network"""
    try:
        if network == "TRC20":
            return validate_trc20_address(address)
        if network in {"ERC20", "BEP20"}:
            return eth_utils.is_address(address)
    except Exception as e:
        logging.error(f"USDT address validation failed: {e}")
    return False

def mask_address(addr):
    """Mask address for display (show first and last 6 chars)"""
    if len(addr) > 12:
        return f"{addr[:6]}...{addr[-6:]}"
    return addr

def random_tx_hash():
    """Generate random transaction hash"""
    import random
    return ''.join(random.choices('0123456789abcdef', k=64))