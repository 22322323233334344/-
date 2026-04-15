import json
import os
import requests
import uuid
import hashlib
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

ADMIN_IDS = [8255207270, 8255207255]
BOT_TOKEN = "8690992959:AAFpGSgTWjWunRJhl5Y1l0harNYwz96Eeyc"
REQUIRED_CHANNEL = "@ugta_hacks"
REVIEWS_CHANNEL = -1003916047149

EMAILS_FILE = "emails.json"
BALANCES_FILE = "user_balances.json"
STATS_FILE = "user_stats.json"
REFERRALS_FILE = "referrals.json"
PAYMENTS_FILE = "pending_payments.json"
USED_TOKENS_FILE = "used_tokens.json"
TOKENS_FILE = "tokens.txt"
ORDERS_FILE = "orders.json"
REVIEWS_FILE = "reviews.json"

WAITING_TOKEN = 1
WITHDRAW_CARD = 2
WITHDRAW_AMOUNT = 3
WAITING_PAYMENT_SCREENSHOT = 4
WAITING_REVIEW_RATING = 5
WAITING_REVIEW_TEXT = 6
WAITING_REVIEW_PHOTO = 7

PRICES = {
    "nitro_3m_no_activation": {"name": "Discord Nitro 3 месяца без активации", "price_uah": 50, "price_usd": 1},
    "nitro_3m_with_activation": {"name": "Discord Nitro 3 месяца с активацией", "price_uah": 90, "price_usd": 2},
    "boost": {"name": "Discord Boost (1 шт)", "price_uah": 20, "price_usd": 0.5},
    "cheat": {"name": "Написание чита", "price_uah": 300, "price_usd": 5},
    "crmp": {"name": "CRMP проект", "price_uah": 100, "price_usd": 2.5},
    "mta": {"name": "MTA проект", "price_uah": 250, "price_usd": 4},
    "samp": {"name": "SAMP проект", "price_uah": 80, "price_usd": 2},
    "gta5": {"name": "GTA 5 проект", "price_uah": 1500, "price_usd": 33},
    "stars": {"name": "Telegram Stars (100 шт)", "price_uah": 60, "price_usd": 1.5},
}

def load_json(file, default=None):
    if not os.path.exists(file):
        return default if default is not None else {}
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_balance(user_id):
    b = load_json(BALANCES_FILE, {})
    return b.get(str(user_id), 0.0)

def set_balance(user_id, amount):
    b = load_json(BALANCES_FILE, {})
    b[str(user_id)] = amount
    save_json(BALANCES_FILE, b)

def add_balance(user_id, amount):
    b = get_balance(user_id)
    set_balance(user_id, b + amount)

def get_tokens_count(user_id):
    s = load_json(STATS_FILE, {})
    return s.get(str(user_id), 0)

def inc_tokens_count(user_id):
    s = load_json(STATS_FILE, {})
    uid = str(user_id)
    s[uid] = s.get(uid, 0) + 1
    save_json(STATS_FILE, s)

def get_referrer(user_id):
    refs = load_json(REFERRALS_FILE, {})
    return refs.get(str(user_id))

def set_referrer(user_id, referrer_id):
    refs = load_json(REFERRALS_FILE, {})
    if str(user_id) not in refs:
        refs[str(user_id)] = referrer_id
        save_json(REFERRALS_FILE, refs)
        return True
    return False

def load_emails():
    if not os.path.exists(EMAILS_FILE):
        return []
    with open(EMAILS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_emails(emails):
    with open(EMAILS_FILE, "w", encoding="utf-8") as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)

def pop_email():
    emails = load_emails()
    if not emails:
        return None
    first = emails.pop(0)
    save_emails(emails)
    return first

def save_token_log(token, user_info, user_id):
    with open(TOKENS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | User {user_id} | {token} | {user_info}\n")

def is_token_used(token):
    used = load_json(USED_TOKENS_FILE, {})
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token_hash in used

def mark_token_used(token, user_id):
    used = load_json(USED_TOKENS_FILE, {})
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    used[token_hash] = user_id
    save_json(USED_TOKENS_FILE, used)

def create_payment_request(user_id, card, amount):
    payments = load_json(PAYMENTS_FILE, {})
    pid = str(uuid.uuid4())[:8]
    payments[pid] = {
        "user_id": user_id,
        "card": card,
        "amount": float(amount),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    save_json(PAYMENTS_FILE, payments)
    return pid

def get_pending_payments():
    payments = load_json(PAYMENTS_FILE, {})
    return {pid: data for pid, data in payments.items() if data["status"] == "pending"}

def update_payment_status(pid, status):
    payments = load_json(PAYMENTS_FILE, {})
    if pid in payments:
        payments[pid]["status"] = status
        save_json(PAYMENTS_FILE, payments)
        return True
    return False

def create_order(user_id, product_key, comment):
    orders = load_json(ORDERS_FILE, {})
    order_id = len(orders) + 1
    orders[str(order_id)] = {
        "user_id": user_id,
        "product": PRICES[product_key]["name"],
        "product_key": product_key,
        "price_uah": PRICES[product_key]["price_uah"],
        "price_usd": PRICES[product_key]["price_usd"],
        "comment": comment,
        "status": "waiting_payment",
        "created_at": datetime.now().isoformat(),
        "screenshot": None,
        "delivered": False,
        "review": None
    }
    save_json(ORDERS_FILE, orders)
    return order_id

def get_order(order_id):
    orders = load_json(ORDERS_FILE, {})
    return orders.get(str(order_id))

def update_order_status(order_id, status):
    orders = load_json(ORDERS_FILE, {})
    if str(order_id) in orders:
        orders[str(order_id)]["status"] = status
        save_json(ORDERS_FILE, orders)
        return True
    return False

def set_order_screenshot(order_id, file_id):
    orders = load_json(ORDERS_FILE, {})
    if str(order_id) in orders:
        orders[str(order_id)]["screenshot"] = file_id
        save_json(ORDERS_FILE, orders)
        return True
    return False

def set_order_delivered(order_id):
    orders = load_json(ORDERS_FILE, {})
    if str(order_id) in orders:
        orders[str(order_id)]["delivered"] = True
        save_json(ORDERS_FILE, orders)
        return True
    return False

def save_review(order_id, rating, text, photo_id):
    reviews = load_json(REVIEWS_FILE, {})
    review_id = len(reviews) + 1
    order = get_order(order_id)
    reviews[str(review_id)] = {
        "order_id": order_id,
        "user_id": order["user_id"],
        "product": order["product"],
        "rating": rating,
        "text": text,
        "photo_id": photo_id,
        "created_at": datetime.now().isoformat()
    }
    save_json(REVIEWS_FILE, reviews)
    return review_id

def check_discord_token(token):
    url = "https://discord.com/api/v9/users/@me"
    headers = {"Authorization": token}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return True, data
        return False, None
    except Exception:
        return False, None