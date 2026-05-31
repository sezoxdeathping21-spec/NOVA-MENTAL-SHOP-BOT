#!/usr/bin/env python3
"""
MENTAL CHEAT SHOP - Telegram Bot
Version: 5.0.0 - Railway Production Ready
Author: MENTAL CHEAT Team
License: Proprietary
Deployment: Railway
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
import hashlib
import hmac
import time
import re
import random
import string
import shutil
import subprocess
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
from functools import wraps
from collections import defaultdict
import io
import qrcode
from PIL import Image
import requests

# Try to import psutil with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed. Process management will be limited.")

# ============================================
# TELEGRAM IMPORTS - CORRECT IMPORT (NO ParseMode from telegram)
# ============================================
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, 
    InputFile, User, Chat, Message, CallbackQuery, 
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes, PreCheckoutQueryHandler
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError, NetworkError, BadRequest

# ============================================
# CONFIGURATION
# ============================================

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8983677514:AAHPkGA-lo6eurpxGLUm9FqBqW5rQ46wOnk")
BOT_USERNAME = "@NOVA_MENTAL_SHOP_OFFICIAL_BOT"
BOT_NAME = "Mental Cheat Shop"

# Railway Persistent Storage Paths
DATA_DIR = "/data"
DB_DIR = os.path.join(DATA_DIR, "database")
UPLOAD_DIR = os.path.join(DATA_DIR, "upload_bots")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# Create directories if not exist
for dir_path in [DATA_DIR, DB_DIR, UPLOAD_DIR, LOGS_DIR, BACKUP_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Database Configuration
DATABASE_PATH = os.path.join(DB_DIR, "mental_cheat_bot.db")

# User Limits
FREE_USER_LIMIT = 2
PREMIUM_USER_LIMIT = 15
RESELLER_USER_LIMIT = 50
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

# File Configuration
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.py', '.js', '.zip'}

# Contact Channel Links
CONTACT_CHANNELS = [
    {"name": "📢 Main Channel", "url": "https://t.me/mentalcheatofficial", "username": "@mentalcheatofficial"},
    {"name": "📢 Updates Channel", "url": "https://t.me/mentalcheatupdates", "username": "@mentalcheatupdates"},
    {"name": "👥 Support Group", "url": "https://t.me/mentalcheatsupport", "username": "@mentalcheatsupport"},
    {"name": "📸 Purchase Details", "url": "https://t.me/MENTALPURCHASEDETAIL", "username": "@MENTALPURCHASEDETAIL"}
]

# Owner Configuration
OWNER_IDS = [8420590053, 6650888707, 8033555435]
ADMIN_IDS = [8420590053, 6650888707, 8033555435]

SUPPORT_CONTACTS = ["@TylerDurden21", "@SegsyToxic", "@MentalOfficial69"]

# Payment Configuration
UPI_ID = "msuhasvardhan@fam"

# Setup Video
SETUP_VIDEO_LINK = "https://youtu.be/EihjAoje3z8"

# Bot Lock Status
BOT_LOCKED = False

# Loader Data with working links
LOADERS = {
    "ZTrax Bypass": {
        "link": "http://hc1.checker.in/file2link/documents/file_528896.apk/ZTrax_Bypass_1.0.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "Tapatap Loader": {
        "link": "http://hc1.checker.in/file2link/documents/file_528898.apk/Tapatap_Loader_1.0.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "PHANTOM SERVER": {
        "link": "http://hc1.checker.in/file2link/documents/file_528900.apk/PHANTOM_SERVER_4.4.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "TRX Premium Loader": {
        "link": "http://hc1.checker.in/file2link/documents/file_528901.apk/TRX_Premium_Loader_4.4_.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "INFINITE OFFICIAL MOD": {
        "link": "http://hc1.checker.in/file2link/documents/file_528902.apk/INFINITE_OFFICAL_MOD_4.4.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "GPS ELITE": {
        "link": "http://hc1.checker.in/file2link/documents/file_528904.apk/GPS_ELITE_4.4.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "Mars Hide Esp + Bt": {
        "link": "http://hc1.checker.in/file2link/documents/file_528906.apk/Mars_Hide_Esp_Bt_4.4.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "OG CHEATS": {
        "link": "https://ne7-40d68f82e4f2.herokuapp.com/stream/2406170?hash=7db53b&d=true",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    },
    "OG CHEATS LOADER": {
        "link": "http://hc1.checker.in/file2link/documents/file_528909.apk/OG_CHEATS_LOADER_4.4.1.apk",
        "features": "🔥BRUTAL LOADER v4.0🔥\n━━━━━━━━━━━━━━\n🎯FEATURES(15)\n━━━━━━━━━━━━━━\n1.ESP VISION BYPASS\n2.AUTO HEADLOCK\n3.NO RECOIL MATRIX\n4.MAGIC BULLET\n5.SPEED HACK\n6.FLY MODE\n7.GRASS/CACTUS REMOVER\n8.AUTO LOOT+FILTER\n9.ANTI-BAN SHIELD\n10.WEAPON COLOR CHANGER\n11.VOICE CHANGER\n12.ENEMY HEALTH VIEWER\n13.VEHICLE GOD MODE\n14.SERVER TIME FREEZE\n15.MEMORY WALKER"
    }
}

# Price Plans (in credits)
PRICE_PLANS = {
    "1 Day": 80,
    "3 Days": 150,
    "7 Days": 300,
    "15 Days": 500,
    "30 Days": 650,
    "2 Months": 800
}

# Credit Purchase Plans (₹ to credits)
CREDIT_PLANS = {
    50: 50,
    100: 100,
    200: 200,
    500: 500,
    1000: 1000,
    2000: 2000
}

# Reseller Panel Prices
RESELLER_PRICES = {
    "MARS": 2000,
    "ZETRAX": 1800,
    "TAPATAP": 2500,
    "FIRE X": 1600,
    "WAR": 1800,
    "DEFEND": 1750,
    "INFINITY": 2000,
    "TRX PREMIUM": 1800
}

# Referral Rewards (in credits)
REFERRAL_REWARDS = {
    10: {"reward": "50 credits", "credits": 50},
    30: {"reward": "150 credits", "credits": 150},
    70: {"reward": "350 credits", "credits": 350}
}

# Conversation States
(
    AWAITING_PAYMENT_SCREENSHOT,
    AWAITING_CREDIT_PAYMENT_SCREENSHOT,
    AWAITING_RESELLER_PAYMENT,
    AWAITING_BROADCAST_MESSAGE,
    AWAITING_EDIT_PRICE,
    AWAITING_NEW_LOADER_NAME,
    AWAITING_NEW_LOADER_LINK,
    AWAITING_NEW_LOADER_FEATURES,
    AWAITING_FILE_UPLOAD,
    AWAITING_ADD_CREDITS_USER,
    AWAITING_ADD_CREDITS_AMOUNT,
    AWAITING_REMOVE_CREDITS_USER,
    AWAITING_REMOVE_CREDITS_AMOUNT,
) = range(13)

# Rate Limiting
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_PERIOD = 60
user_requests = defaultdict(list)

# Process Management - Store running processes
running_processes = {}

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'bot_operations.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# DATABASE MANAGER
# ============================================

class DatabaseManager:
    """Complete database management system with credit system support"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table with credit balance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                referrals_count INTEGER DEFAULT 0,
                referred_by INTEGER,
                is_verified BOOLEAN DEFAULT 1,
                verification_date TIMESTAMP,
                is_banned BOOLEAN DEFAULT 0,
                ban_reason TEXT,
                total_spent INTEGER DEFAULT 0,
                credits_balance INTEGER DEFAULT 0,
                subscription_expiry TIMESTAMP,
                user_type TEXT DEFAULT 'free',
                last_active TIMESTAMP,
                language_code TEXT,
                phone_number TEXT
            )
        ''')
        
        # Credit transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credits_transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                transaction_type TEXT,
                status TEXT DEFAULT 'pending',
                payment_screenshot TEXT,
                payment_amount INTEGER,
                timestamp TIMESTAMP,
                verified_by INTEGER,
                verification_time TIMESTAMP,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Purchases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                loader_name TEXT,
                duration TEXT,
                credits_cost INTEGER,
                payment_screenshot TEXT,
                status TEXT DEFAULT 'pending',
                key_issued TEXT,
                purchase_date TIMESTAMP,
                verified_by INTEGER,
                verification_date TIMESTAMP,
                transaction_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_code TEXT UNIQUE,
                loader_name TEXT,
                duration TEXT,
                is_used BOOLEAN DEFAULT 0,
                used_by INTEGER,
                expiry_date TIMESTAMP,
                created_date TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (used_by) REFERENCES users (user_id)
            )
        ''')
        
        # Pending verifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                loader_name TEXT,
                duration TEXT,
                credits_cost INTEGER,
                screenshot_file_id TEXT,
                timestamp TIMESTAMP,
                message_id INTEGER,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Resellers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resellers (
                user_id INTEGER PRIMARY KEY,
                reseller_type TEXT,
                purchase_date TIMESTAMP,
                expiry_date TIMESTAMP,
                amount_paid INTEGER,
                status TEXT DEFAULT 'pending',
                total_sales INTEGER DEFAULT 0,
                total_revenue INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Broadcasts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                broadcast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                media_file_id TEXT,
                media_type TEXT,
                sent_count INTEGER,
                delivered_count INTEGER,
                failed_count INTEGER,
                created_by INTEGER,
                created_date TIMESTAMP
            )
        ''')
        
        # Referrals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                referral_date TIMESTAMP,
                reward_claimed BOOLEAN DEFAULT 0,
                reward_given TEXT,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # File approvals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                review_time TIMESTAMP,
                file_type TEXT,
                uploaded_time TIMESTAMP,
                message_id INTEGER,
                review_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Loaders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loaders (
                loader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                loader_name TEXT UNIQUE,
                loader_link TEXT,
                features TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_by INTEGER,
                created_date TIMESTAMP,
                updated_by INTEGER,
                updated_date TIMESTAMP
            )
        ''')
        
        # Price plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration TEXT UNIQUE,
                credits INTEGER,
                updated_by INTEGER,
                updated_date TIMESTAMP
            )
        ''')
        
        # Credit plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_rs INTEGER UNIQUE,
                credits INTEGER,
                updated_by INTEGER,
                updated_date TIMESTAMP
            )
        ''')
        
        # Insert default price plans
        for duration, credits in PRICE_PLANS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO price_plans (duration, credits, updated_date)
                VALUES (?, ?, ?)
            ''', (duration, credits, datetime.now()))
        
        # Insert default credit plans
        for amount_rs, credits in CREDIT_PLANS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO credit_plans (amount_rs, credits, updated_date)
                VALUES (?, ?, ?)
            ''', (amount_rs, credits, datetime.now()))
        
        # Insert default loaders
        for loader_name, loader_data in LOADERS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO loaders (loader_name, loader_link, features, created_date)
                VALUES (?, ?, ?, ?)
            ''', (loader_name, loader_data["link"], loader_data["features"], datetime.now()))
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized successfully at {self.db_path}")
    
    def add_user(self, user_id: int, username: str, first_name: str, 
                 last_name: str = None, referred_by: int = None) -> bool:
        """Add new user to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, join_date, referred_by, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, datetime.now(), 
                  referred_by, datetime.now()))
            
            if cursor.rowcount > 0 and referred_by:
                cursor.execute('''
                    UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?
                ''', (referred_by,))
                
                cursor.execute('''
                    INSERT INTO referrals (referrer_id, referred_id, referral_date)
                    VALUES (?, ?, ?)
                ''', (referred_by, user_id, datetime.now()))
                
                cursor.execute('SELECT referrals_count FROM users WHERE user_id = ?', (referred_by,))
                result = cursor.fetchone()
                if result:
                    count = result['referrals_count']
                    for threshold in REFERRAL_REWARDS:
                        if count >= threshold:
                            reward = REFERRAL_REWARDS[threshold]
                            self.add_credits(referred_by, reward['credits'], "referral_reward", None)
                            cursor.execute('''
                                UPDATE referrals SET reward_claimed = 1, reward_given = ?
                                WHERE referrer_id = ? AND referred_id = ?
                            ''', (reward['reward'], referred_by, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
        finally:
            conn.close()
    
    def add_credits(self, user_id: int, amount: int, description: str, admin_id: int = None) -> bool:
        """Add credits to user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET credits_balance = credits_balance + ? WHERE user_id = ?', (amount, user_id))
            
            cursor.execute('''
                INSERT INTO credits_transactions (user_id, amount, transaction_type, status, timestamp, description, verified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, amount, 'credit', 'completed', datetime.now(), description, admin_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return False
        finally:
            conn.close()
    
    def remove_credits(self, user_id: int, amount: int, description: str, admin_id: int = None) -> bool:
        """Remove credits from user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT credits_balance FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result or result['credits_balance'] < amount:
                return False
            
            cursor.execute('UPDATE users SET credits_balance = credits_balance - ? WHERE user_id = ?', (amount, user_id))
            
            cursor.execute('''
                INSERT INTO credits_transactions (user_id, amount, transaction_type, status, timestamp, description, verified_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, -amount, 'debit', 'completed', datetime.now(), description, admin_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing credits: {e}")
            return False
        finally:
            conn.close()
    
    def deduct_credits(self, user_id: int, amount: int) -> bool:
        """Deduct credits for purchase"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT credits_balance FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result or result['credits_balance'] < amount:
                return False
            
            cursor.execute('UPDATE users SET credits_balance = credits_balance - ? WHERE user_id = ?', (amount, user_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            return False
        finally:
            conn.close()
    
    def add_credit_purchase_request(self, user_id: int, amount_rs: int, credits: int, screenshot_file_id: str) -> Optional[int]:
        """Add credit purchase request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO credits_transactions (user_id, amount, transaction_type, status, payment_screenshot, payment_amount, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, credits, 'credit_purchase', 'pending', screenshot_file_id, amount_rs, datetime.now()))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            return transaction_id
        except Exception as e:
            logger.error(f"Error adding credit purchase request: {e}")
            return None
        finally:
            conn.close()
    
    def verify_credit_purchase(self, transaction_id: int, verified_by: int) -> bool:
        """Verify credit purchase and add credits to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM credits_transactions WHERE transaction_id = ? AND status = "pending"', (transaction_id,))
            transaction = cursor.fetchone()
            
            if not transaction:
                return False
            
            cursor.execute('''
                UPDATE credits_transactions 
                SET status = 'completed', verified_by = ?, verification_time = ?
                WHERE transaction_id = ?
            ''', (verified_by, datetime.now(), transaction_id))
            
            cursor.execute('''
                UPDATE users SET credits_balance = credits_balance + ? WHERE user_id = ?
            ''', (transaction['amount'], transaction['user_id']))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error verifying credit purchase: {e}")
            return False
        finally:
            conn.close()
    
    def get_pending_credit_purchases(self) -> List[Dict]:
        """Get all pending credit purchase requests"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT t.*, u.username, u.first_name 
                FROM credits_transactions t
                JOIN users u ON t.user_id = u.user_id
                WHERE t.transaction_type = 'credit_purchase' AND t.status = 'pending'
                ORDER BY t.timestamp DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending credit purchases: {e}")
            return []
        finally:
            conn.close()
    
    def generate_key(self, loader_name: str, duration: str, user_id: int) -> str:
        """Generate unique key for loader access"""
        key_code = f"MC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=16))}"
        expiry_date = datetime.now() + timedelta(days=self.get_duration_days(duration))
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO keys (key_code, loader_name, duration, expiry_date, created_date, used_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key_code, loader_name, duration, expiry_date, datetime.now(), user_id))
            conn.commit()
            return key_code
        except Exception as e:
            logger.error(f"Error generating key: {e}")
            return None
        finally:
            conn.close()
    
    def get_duration_days(self, duration: str) -> int:
        """Convert duration string to days"""
        duration_map = {
            "1 Day": 1, "3 Days": 3, "7 Days": 7,
            "15 Days": 15, "30 Days": 30, "2 Months": 60
        }
        return duration_map.get(duration, 1)
    
    def add_purchase(self, user_id: int, loader_name: str, duration: str, 
                     credits_cost: int) -> Optional[int]:
        """Add new purchase record using credits"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO purchases (user_id, loader_name, duration, credits_cost, purchase_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, loader_name, duration, credits_cost, datetime.now(), 'completed'))
            
            purchase_id = cursor.lastrowid
            conn.commit()
            return purchase_id
        except Exception as e:
            logger.error(f"Error adding purchase: {e}")
            return None
        finally:
            conn.close()
    
    def check_user_verification(self, user_id: int) -> bool:
        """Check if user is verified (always true now)"""
        return True
    
    def verify_user(self, user_id: int) -> bool:
        """Mark user as verified"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET is_verified = 1, verification_date = ? WHERE user_id = ?', (datetime.now(), user_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics including credits"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                return {}
            
            cursor.execute('''
                SELECT COUNT(*) as total_purchases, SUM(credits_cost) as total_spent
                FROM purchases WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            purchases = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as active_keys FROM keys WHERE used_by = ? AND expiry_date > ?', (user_id, datetime.now()))
            active_keys = cursor.fetchone()
            
            return {
                'username': user['username'],
                'first_name': user['first_name'],
                'join_date': user['join_date'],
                'referrals_count': user['referrals_count'],
                'total_spent': purchases['total_spent'] or 0,
                'total_purchases': purchases['total_purchases'] or 0,
                'active_keys': active_keys['active_keys'] or 0,
                'credits_balance': user['credits_balance'] or 0,
                'user_type': user['user_type']
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
        finally:
            conn.close()
    
    def get_referral_link(self, user_id: int) -> str:
        """Generate referral link for user"""
        return f"https://t.me/{BOT_USERNAME[1:]}?start=ref_{user_id}"
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT user_id, username, first_name, join_date, credits_balance, user_type FROM users')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
        finally:
            conn.close()
    
    def add_broadcast(self, message: str, media_file_id: str, media_type: str, created_by: int) -> Optional[int]:
        """Add broadcast record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO broadcasts (message, media_file_id, media_type, created_by, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (message, media_file_id, media_type, created_by, datetime.now()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding broadcast: {e}")
            return None
        finally:
            conn.close()
    
    def update_broadcast_stats(self, broadcast_id: int, sent: int, delivered: int, failed: int):
        """Update broadcast statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE broadcasts SET sent_count = ?, delivered_count = ?, failed_count = ? WHERE broadcast_id = ?', (sent, delivered, failed, broadcast_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating broadcast stats: {e}")
        finally:
            conn.close()
    
    def add_reseller_request(self, user_id: int, reseller_type: str, amount: int) -> bool:
        """Add reseller request to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO resellers (user_id, reseller_type, purchase_date, amount_paid, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, reseller_type, datetime.now(), amount, 'pending'))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding reseller request: {e}")
            return False
        finally:
            conn.close()
    
    def approve_reseller(self, user_id: int, approved_by: int) -> bool:
        """Approve reseller request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            expiry_date = datetime.now() + timedelta(days=30)
            cursor.execute('UPDATE resellers SET status = "active", expiry_date = ? WHERE user_id = ? AND status = "pending"', (expiry_date, user_id))
            cursor.execute('UPDATE users SET user_type = "reseller" WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error approving reseller: {e}")
            return False
        finally:
            conn.close()
    
    def get_reseller_status(self, user_id: int) -> Optional[Dict]:
        """Get reseller status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM resellers WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting reseller status: {e}")
            return None
        finally:
            conn.close()
    
    def get_pending_resellers(self) -> List[Dict]:
        """Get all pending reseller requests"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT r.*, u.username, u.first_name FROM resellers r JOIN users u ON r.user_id = u.user_id WHERE r.status = "pending"')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending resellers: {e}")
            return []
        finally:
            conn.close()
    
    def add_file_approval(self, user_id: int, file_name: str, file_path: str, file_type: str, message_id: int) -> Optional[int]:
        """Add file for approval"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO file_approvals (user_id, file_name, file_path, file_type, uploaded_time, message_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, file_name, file_path, file_type, datetime.now(), message_id, 'pending'))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding file approval: {e}")
            return None
        finally:
            conn.close()
    
    def get_pending_files(self) -> List[Dict]:
        """Get all pending file approvals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT f.*, u.username, u.first_name 
                FROM file_approvals f
                JOIN users u ON f.user_id = u.user_id
                WHERE f.status = 'pending'
                ORDER BY f.uploaded_time DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending files: {e}")
            return []
        finally:
            conn.close()
    
    def approve_file(self, file_id: int, reviewed_by: int, reason: str = None) -> bool:
        """Approve a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE file_approvals 
                SET status = 'approved', reviewed_by = ?, review_time = ?, review_reason = ?
                WHERE id = ?
            ''', (reviewed_by, datetime.now(), reason, file_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error approving file: {e}")
            return False
        finally:
            conn.close()
    
    def reject_file(self, file_id: int, reviewed_by: int, reason: str) -> bool:
        """Reject a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE file_approvals 
                SET status = 'rejected', reviewed_by = ?, review_time = ?, review_reason = ?
                WHERE id = ?
            ''', (reviewed_by, datetime.now(), reason, file_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error rejecting file: {e}")
            return False
        finally:
            conn.close()
    
    def get_approved_files(self, user_id: int) -> List[Dict]:
        """Get approved files for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM file_approvals 
                WHERE user_id = ? AND status = 'approved'
                ORDER BY uploaded_time DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting approved files: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_loaders(self) -> List[Dict]:
        """Get all loaders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM loaders WHERE is_active = 1 ORDER BY loader_name')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting loaders: {e}")
            return []
        finally:
            conn.close()
    
    def get_price_plans(self) -> List[Dict]:
        """Get all price plans"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM price_plans ORDER BY credits')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting price plans: {e}")
            return []
        finally:
            conn.close()
    
    def get_credit_plans(self) -> List[Dict]:
        """Get all credit purchase plans"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM credit_plans ORDER BY amount_rs')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting credit plans: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_limit(self, user_id: int) -> int:
        """Get user's file upload limit based on user type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_type FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return FREE_USER_LIMIT
        
        user_type = result['user_type']
        if user_id in OWNER_IDS:
            return OWNER_LIMIT
        elif user_id in ADMIN_IDS:
            return ADMIN_LIMIT
        elif user_type == 'reseller':
            return RESELLER_USER_LIMIT
        elif user_type == 'premium':
            return PREMIUM_USER_LIMIT
        return FREE_USER_LIMIT
    
    def get_user_upload_count(self, user_id: int) -> int:
        """Get number of files uploaded by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) as count FROM file_approvals WHERE user_id = ? AND status != "rejected"', (user_id,))
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting user upload count: {e}")
            return 0
        finally:
            conn.close()
    
    def add_loader(self, loader_name: str, loader_link: str, features: str, created_by: int) -> bool:
        """Add new loader"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO loaders (loader_name, loader_link, features, created_by, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (loader_name, loader_link, features, created_by, datetime.now()))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding loader: {e}")
            return False
        finally:
            conn.close()
    
    def update_price(self, duration: str, credits: int, updated_by: int) -> bool:
        """Update price plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE price_plans 
                SET credits = ?, updated_by = ?, updated_date = ?
                WHERE duration = ?
            ''', (credits, updated_by, datetime.now(), duration))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating price: {e}")
            return False
        finally:
            conn.close()
    
    def get_credit_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get credit transaction history for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM credits_transactions 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting credit transactions: {e}")
            return []
        finally:
            conn.close()

# ============================================
# SCRIPT EXECUTION MANAGER
# ============================================

class ScriptManager:
    """Manage execution of approved Python and JavaScript scripts"""
    
    def __init__(self):
        self.processes = running_processes
        self.upload_dir = UPLOAD_DIR
        self.logs_dir = LOGS_DIR
    
    def run_script(self, user_id: int, file_path: str, file_name: str):
        """Run a script as subprocess"""
        try:
            process_id = f"{user_id}_{file_name}"
            
            if process_id in self.processes:
                process = self.processes[process_id]
                if process.poll() is None:
                    return False, "Script already running"
            
            if file_name.endswith('.py'):
                cmd = ['python3', file_path]
            elif file_name.endswith('.js'):
                cmd = ['node', file_path]
            else:
                return False, "Unsupported file type"
            
            log_file = os.path.join(self.logs_dir, f"{user_id}_{file_name}.log")
            with open(log_file, 'w') as f:
                f.write(f"Started at: {datetime.now()}\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write("=" * 50 + "\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=open(log_file, 'a'),
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(file_path),
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.processes[process_id] = process
            return True, f"Started with PID: {process.pid}"
        except Exception as e:
            logger.error(f"Error running script: {e}")
            return False, str(e)
    
    def stop_script(self, user_id: int, file_name: str):
        """Stop a running script"""
        try:
            process_id = f"{user_id}_{file_name}"
            
            if process_id not in self.processes:
                return False, "Script not running"
            
            process = self.processes[process_id]
            
            if process.poll() is None:
                if PSUTIL_AVAILABLE:
                    try:
                        parent = psutil.Process(process.pid)
                        for child in parent.children(recursive=True):
                            child.terminate()
                        parent.terminate()
                        parent.wait(timeout=5)
                    except:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                    process.wait(timeout=5)
                
                del self.processes[process_id]
                return True, "Script stopped"
            else:
                del self.processes[process_id]
                return False, "Script already stopped"
        except Exception as e:
            logger.error(f"Error stopping script: {e}")
            return False, str(e)
    
    def restart_script(self, user_id: int, file_path: str, file_name: str):
        """Restart a script"""
        self.stop_script(user_id, file_name)
        return self.run_script(user_id, file_path, file_name)
    
    def get_logs(self, user_id: int, file_name: str, lines: int = 100) -> str:
        """Get script logs"""
        try:
            log_file = os.path.join(self.logs_dir, f"{user_id}_{file_name}.log")
            if not os.path.exists(log_file):
                return "No logs found"
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(last_lines)
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return f"Error reading logs: {e}"
    
    def delete_script_files(self, user_id: int, file_name: str):
        """Delete script and related files"""
        try:
            user_dir = os.path.join(self.upload_dir, str(user_id))
            file_path = os.path.join(user_dir, file_name)
            log_file = os.path.join(self.logs_dir, f"{user_id}_{file_name}.log")
            
            self.stop_script(user_id, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(log_file):
                os.remove(log_file)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting script files: {e}")
            return False

# ============================================
# UTILITY FUNCTIONS AND DECORATORS
# ============================================

def rate_limit(func):
    """Rate limiting decorator"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        now = time.time()
        
        user_requests[user_id] = [req_time for req_time in user_requests[user_id] if now - req_time < RATE_LIMIT_PERIOD]
        
        if len(user_requests[user_id]) >= RATE_LIMIT_REQUESTS:
            await update.message.reply_text(
                "⚠️ *Rate Limit Exceeded*\n\nPlease wait before sending more messages.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        user_requests[user_id].append(now)
        return await func(update, context, *args, **kwargs)
    return wrapper

def owner_only(func):
    """Decorator to restrict commands to owners only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in OWNER_IDS:
            await update.message.reply_text(
                "⛔ *Access Denied*\n\nThis command is only available for bot owners.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def admin_only(func):
    """Decorator to restrict commands to admins only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(
                "⛔ *Access Denied*\n\nThis command is only available for bot admins.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def verified_only(func):
    """Decorator to restrict commands to verified users only (always passes now)"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        global BOT_LOCKED
        
        if BOT_LOCKED:
            await update.message.reply_text(
                "🔒 *Bot is Under Maintenance*\n\nPlease try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def generate_upi_qr(upi_id: str, amount: int = None, note: str = None) -> io.BytesIO:
    """Generate UPI QR code for payment"""
    upi_string = f"pay?pa={upi_id}&pn=Mental%20Cheat&cu=INR"
    if amount:
        upi_string += f"&am={amount}"
    if note:
        upi_string += f"&tn={note}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard with contact channel button"""
    keyboard = [
        [KeyboardButton("🏠 Home"), KeyboardButton("📦 Loaders")],
        [KeyboardButton("💰 Buy Credits"), KeyboardButton("👥 Referral")],
        [KeyboardButton("💳 Purchase"), KeyboardButton("👑 Reseller Panel")],
        [KeyboardButton("📤 Upload File"), KeyboardButton("📁 My Scripts")],
        [KeyboardButton("📢 Broadcast"), KeyboardButton("❓ Support")],
        [KeyboardButton("📸 Purchase Details"), KeyboardButton("🎥 Setup Video")],
        [KeyboardButton("📢 Contact Channel")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def create_loader_keyboard(loaders: List[Dict]) -> InlineKeyboardMarkup:
    """Create loader selection keyboard"""
    keyboard = []
    for loader in loaders:
        keyboard.append([InlineKeyboardButton(loader['loader_name'], callback_data=f"loader_{loader['loader_name']}")])
    return InlineKeyboardMarkup(keyboard)

def create_duration_keyboard(loader_name: str, price_plans: List[Dict]) -> InlineKeyboardMarkup:
    """Create duration selection keyboard with credit prices"""
    keyboard = []
    for plan in price_plans:
        keyboard.append([InlineKeyboardButton(
            f"{plan['duration']} - {plan['credits']} credits", 
            callback_data=f"duration_{loader_name}_{plan['duration']}_{plan['credits']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_loaders")])
    return InlineKeyboardMarkup(keyboard)

def create_credit_plans_keyboard(credit_plans: List[Dict]) -> InlineKeyboardMarkup:
    """Create credit purchase plans keyboard"""
    keyboard = []
    for plan in credit_plans:
        keyboard.append([InlineKeyboardButton(
            f"₹{plan['amount_rs']} → {plan['credits']} Credits", 
            callback_data=f"credit_plan_{plan['amount_rs']}_{plan['credits']}"
        )])
    return InlineKeyboardMarkup(keyboard)

def create_script_control_keyboard(user_id: int, file_name: str, is_running: bool) -> InlineKeyboardMarkup:
    """Create script control keyboard"""
    keyboard = []
    
    if is_running:
        keyboard.append([InlineKeyboardButton("⏹ Stop", callback_data=f"stop_script_{user_id}_{file_name}")])
        keyboard.append([InlineKeyboardButton("🔄 Restart", callback_data=f"restart_script_{user_id}_{file_name}")])
    else:
        keyboard.append([InlineKeyboardButton("▶️ Start", callback_data=f"start_script_{user_id}_{file_name}")])
    
    keyboard.append([InlineKeyboardButton("📋 View Logs", callback_data=f"logs_script_{user_id}_{file_name}")])
    keyboard.append([InlineKeyboardButton("🗑 Delete", callback_data=f"delete_script_{user_id}_{file_name}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_my_scripts")])
    
    return InlineKeyboardMarkup(keyboard)

def create_contact_channels_keyboard() -> InlineKeyboardMarkup:
    """Create contact channels keyboard"""
    keyboard = []
    for channel in CONTACT_CHANNELS:
        keyboard.append([InlineKeyboardButton(channel['name'], url=channel['url'])])
    return InlineKeyboardMarkup(keyboard)

# ============================================
# BOT HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - direct access, no verification"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    first_name = user.first_name
    last_name = user.last_name
    
    referred_by = None
    if context.args and context.args[0].startswith('ref_'):
        try:
            referred_by = int(context.args[0].split('_')[1])
            if referred_by == user_id:
                referred_by = None
        except:
            pass
    
    db = DatabaseManager()
    db.add_user(user_id, username, first_name, last_name, referred_by)
    
    await send_welcome_message(update, context)

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message to user"""
    user = update.effective_user
    user_id = user.id
    
    profile_photos = await context.bot.get_user_profile_photos(user_id, limit=1)
    profile_photo = None
    
    if profile_photos.total_count > 0:
        file_id = profile_photos.photos[0][-1].file_id
        profile_photo = file_id
    
    db = DatabaseManager()
    stats = db.get_user_stats(user_id)
    
    join_date = datetime.now().strftime("%d %B %Y")
    
    welcome_text = (
        f"🎉 *WELCOME TO MENTAL CHEAT* 🎉\n\n"
        f"👋 Hello {user.first_name}!\n"
        f"📝 @{user.username or 'No username'}\n"
        f"📅 Joined: {join_date}\n\n"
        f"🔓 *ACCESS GRANTED*\n"
        f"You now have full access to all features!\n\n"
        f"📊 *Your Stats:*\n"
        f"┃ 👥 Referrals: {stats.get('referrals_count', 0)}\n"
        f"┃ 💰 Credits Balance: {stats.get('credits_balance', 0)} credits\n"
        f"┃ 💳 Total Spent: {stats.get('total_spent', 0)} credits\n"
        f"┃ 🎫 Active Keys: {stats.get('active_keys', 0)}\n"
        f"┃ 📁 Upload Limit: {db.get_user_limit(user_id)} files\n\n"
        f"⚡ Use the menu below to get started!\n\n"
        f"💡 *Tip:* Buy credits using '💰 Buy Credits' button!"
    )
    
    reply_markup = create_main_menu_keyboard()
    
    if profile_photo:
        await update.message.reply_photo(photo=profile_photo, caption=welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Home button"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    stats = db.get_user_stats(user_id)
    
    home_text = (
        "🏠 *MENTAL CHEAT - HOME*\n\n"
        f"👤 *User:* {update.effective_user.first_name}\n"
        f"📊 *Referrals:* {stats.get('referrals_count', 0)}\n"
        f"💰 *Credits Balance:* {stats.get('credits_balance', 0)} credits\n"
        f"💳 *Total Spent:* {stats.get('total_spent', 0)} credits\n"
        f"🎫 *Active Keys:* {stats.get('active_keys', 0)}\n"
        f"📁 *Upload Limit:* {db.get_user_limit(user_id)} files\n\n"
        "📌 *Quick Links:*\n"
        "• /loaders - View all loaders\n"
        "• /buy_credits - Purchase credits\n"
        "• /purchase - Buy loaders with credits\n"
        "• /referral - Get referral link\n"
        "• /support - Contact support\n"
        "• /upload - Upload your script\n\n"
        "⚡ Select an option from the menu below!"
    )
    
    reply_markup = create_main_menu_keyboard()
    await update.message.reply_text(home_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# ============================================
# CREDIT SYSTEM HANDLERS
# ============================================

async def buy_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Buy Credits button"""
    db = DatabaseManager()
    credit_plans = db.get_credit_plans()
    
    message = (
        "💰 *BUY CREDITS*\n\n"
        f"💡 *Exchange Rate:* ₹1 = 1 Credit\n\n"
        "Select a plan below to add credits to your account:\n\n"
    )
    
    for plan in credit_plans:
        message += f"┃ ₹{plan['amount_rs']} → {plan['credits']} credits\n"
    
    message += "\n📸 *How it works:*\n"
    message += "1. Select a plan\n"
    message += "2. Send payment to UPI ID\n"
    message += "3. Upload payment screenshot\n"
    message += "4. Credits added after verification\n\n"
    message += f"🏦 *UPI ID:* `{UPI_ID}`"
    
    keyboard = create_credit_plans_keyboard(credit_plans)
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def credit_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle credit plan selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("credit_plan_", "").split("_")
    amount_rs = int(data[0])
    credits = int(data[1])
    
    context.user_data['credit_purchase'] = {
        'amount_rs': amount_rs,
        'credits': credits
    }
    
    qr_buffer = generate_upi_qr(UPI_ID, amount_rs, f"Purchase {credits} credits")
    
    message = (
        f"💰 *Credit Purchase*\n\n"
        f"💵 Amount: ₹{amount_rs}\n"
        f"✨ Credits: {credits} credits\n\n"
        f"🏦 *UPI ID:* `{UPI_ID}`\n\n"
        "Scan QR code or send payment to above UPI ID\n\n"
        "📸 *After payment:*\n"
        "1. Take screenshot of payment confirmation\n"
        "2. Send the screenshot here\n"
        "3. Credits will be added after verification\n\n"
        "⚠️ *Important:* Send ONLY the screenshot of payment confirmation!"
    )
    
    keyboard = [[InlineKeyboardButton("📸 Upload Screenshot", callback_data="upload_credit_screenshot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    await query.message.reply_photo(photo=qr_buffer, caption="🔍 *Scan to pay*", parse_mode=ParseMode.MARKDOWN)

async def upload_credit_screenshot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upload credit screenshot callback"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📸 *Upload Payment Screenshot*\n\n"
        "Please send a screenshot of the payment confirmation.\n\n"
        "The screenshot should clearly show:\n"
        "• Transaction ID\n"
        "• Amount paid\n"
        "• Payment status (Success/Completed)\n\n"
        "Send the screenshot as a photo message.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return AWAITING_CREDIT_PAYMENT_SCREENSHOT

async def handle_credit_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle credit payment screenshot upload"""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = photo.file_id
    
    credit_purchase = context.user_data.get('credit_purchase')
    if not credit_purchase:
        await update.message.reply_text(
            "❌ *Session Expired*\n\nPlease start the purchase process again using /buy_credits.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    db = DatabaseManager()
    transaction_id = db.add_credit_purchase_request(
        user_id, 
        credit_purchase['amount_rs'], 
        credit_purchase['credits'], 
        file_id
    )
    
    if transaction_id:
        for owner_id in OWNER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"💰 *New Credit Purchase Pending*\n\n"
                         f"👤 User: {update.effective_user.first_name}\n"
                         f"🆔 ID: {user_id}\n"
                         f"💰 Amount: ₹{credit_purchase['amount_rs']}\n"
                         f"✨ Credits: {credit_purchase['credits']}\n"
                         f"🆔 Transaction ID: {transaction_id}\n\n"
                         f"Use /pending_credits to verify.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await update.message.reply_text(
            "✅ *Screenshot Received!*\n\n"
            "Your credit purchase is now pending verification.\n\n"
            "📌 *Next Steps:*\n"
            "• Admin will verify your payment\n"
            "• Credits will be added to your account\n"
            "• This usually takes 5-30 minutes\n\n"
            "🔔 You'll be notified once verified.\n\n"
            f"For urgent support, contact: {', '.join(SUPPORT_CONTACTS)}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ *Error Processing Request*\n\nPlease try again or contact support.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    return ConversationHandler.END

async def my_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's credit balance and transaction history"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    stats = db.get_user_stats(user_id)
    transactions = db.get_credit_transactions(user_id, 10)
    
    message = (
        f"💰 *MY CREDITS*\n\n"
        f"📊 *Current Balance:* {stats.get('credits_balance', 0)} credits\n"
        f"💳 *Total Spent:* {stats.get('total_spent', 0)} credits\n\n"
        f"📜 *Recent Transactions:*\n"
    )
    
    for tx in transactions:
        if tx['transaction_type'] == 'credit_purchase':
            message += f"┃ +{tx['amount']} credits - Purchase\n"
        elif tx['transaction_type'] == 'credit':
            message += f"┃ +{tx['amount']} credits - {tx['description']}\n"
        elif tx['transaction_type'] == 'debit':
            message += f"┃ {tx['amount']} credits - {tx['description']}\n"
    
    if not transactions:
        message += "┃ No transactions yet\n"
    
    message += f"\n💡 *Need more credits?* Use /buy_credits"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=create_main_menu_keyboard())

# ============================================
# LOADER HANDLERS WITH CREDIT SYSTEM
# ============================================

async def show_loaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Loaders button"""
    db = DatabaseManager()
    loaders = db.get_all_loaders()
    
    if not loaders:
        await update.message.reply_text("❌ *No Loaders Available*\n\nPlease check back later.", parse_mode=ParseMode.MARKDOWN)
        return
    
    message = "📦 *AVAILABLE LOADERS*\n\nSelect a loader to view features and purchase:\n"
    keyboard = create_loader_keyboard(loaders)
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def loader_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle loader selection callback"""
    query = update.callback_query
    await query.answer()
    
    loader_name = query.data.replace("loader_", "")
    
    db = DatabaseManager()
    loaders = db.get_all_loaders()
    
    selected_loader = None
    for loader in loaders:
        if loader['loader_name'] == loader_name:
            selected_loader = loader
            break
    
    if not selected_loader:
        await query.edit_message_text("❌ Loader not found!")
        return
    
    message = f"📱 *{selected_loader['loader_name']}*\n\n```\n{selected_loader['features']}\n```\n\nSelect duration to continue:"
    price_plans = db.get_price_plans()
    keyboard = create_duration_keyboard(loader_name, price_plans)
    
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle duration selection callback with credit check"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("duration_", "").split("_")
    loader_name = data[0]
    duration = data[1]
    credits_cost = int(data[2])
    
    user_id = query.from_user.id
    
    db = DatabaseManager()
    stats = db.get_user_stats(user_id)
    current_credits = stats.get('credits_balance', 0)
    
    if current_credits < credits_cost:
        insufficient_msg = (
            f"❌ *Insufficient Credits*\n\n"
            f"📦 Loader: {loader_name}\n"
            f"⏱ Duration: {duration}\n"
            f"💰 Cost: {credits_cost} credits\n"
            f"💳 Your Balance: {current_credits} credits\n\n"
            f"⚠️ You need {credits_cost - current_credits} more credits!\n\n"
            f"💡 Use /buy_credits to add credits to your account."
        )
        await query.edit_message_text(insufficient_msg, parse_mode=ParseMode.MARKDOWN)
        return
    
    context.user_data['selected_loader'] = loader_name
    context.user_data['selected_duration'] = duration
    context.user_data['credits_cost'] = credits_cost
    
    confirm_msg = (
        f"💳 *Confirm Purchase*\n\n"
        f"📦 Loader: {loader_name}\n"
        f"⏱ Duration: {duration}\n"
        f"💰 Cost: {credits_cost} credits\n"
        f"💳 Your Balance: {current_credits} credits\n\n"
        f"After purchase, your balance will be: {current_credits - credits_cost} credits\n\n"
        f"Click 'Confirm' to proceed with the purchase."
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"confirm_purchase_{loader_name}_{duration}_{credits_cost}")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="back_to_loaders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(confirm_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def confirm_purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle purchase confirmation and deduct credits"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("confirm_purchase_", "").split("_")
    loader_name = data[0]
    duration = data[1]
    credits_cost = int(data[2])
    
    user_id = query.from_user.id
    
    db = DatabaseManager()
    
    # Check balance again before deducting
    stats = db.get_user_stats(user_id)
    if stats.get('credits_balance', 0) < credits_cost:
        await query.edit_message_text(
            "❌ *Insufficient Credits*\n\nYour balance has changed. Please try again.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Deduct credits
    if db.deduct_credits(user_id, credits_cost):
        # Generate key
        key_code = db.generate_key(loader_name, duration, user_id)
        
        # Record purchase
        db.add_purchase(user_id, loader_name, duration, credits_cost)
        
        # Get loader link
        loaders = db.get_all_loaders()
        loader_link = None
        for loader in loaders:
            if loader['loader_name'] == loader_name:
                loader_link = loader['loader_link']
                break
        
        success_msg = (
            f"✅ *Purchase Successful!*\n\n"
            f"📦 Loader: {loader_name}\n"
            f"⏱ Duration: {duration}\n"
            f"💰 Credits Spent: {credits_cost}\n"
            f"💳 Remaining Balance: {stats.get('credits_balance', 0) - credits_cost} credits\n\n"
            f"🔑 *Your Key:*\n`{key_code}`\n\n"
            f"📥 *Download Link:*\n{loader_link}\n\n"
            f"📌 *How to use:*\n"
            f"1. Download the loader from the link above\n"
            f"2. Install the APK\n"
            f"3. Enter your key when prompted\n"
            f"4. Enjoy!\n\n"
            f"⚠️ *Note:* Key expires in {duration}\n"
            f"Support: {', '.join(SUPPORT_CONTACTS)}"
        )
        
        await query.edit_message_text(success_msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        await query.edit_message_text(
            "❌ *Purchase Failed*\n\nPlease try again or contact support.",
            parse_mode=ParseMode.MARKDOWN
        )

# ============================================
# CONTACT CHANNEL HANDLER
# ============================================

async def contact_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Contact Channel button"""
    message = (
        "📢 *CONTACT & CHANNELS*\n\n"
        "Join our official channels for updates and support:\n\n"
    )
    
    for channel in CONTACT_CHANNELS:
        message += f"{channel['name']}: {channel['url']}\n\n"
    
    message += f"👨‍💼 *Support Team:*\n"
    for contact in SUPPORT_CONTACTS:
        message += f"• {contact}\n"
    
    keyboard = create_contact_channels_keyboard()
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=keyboard)

# ============================================
# FILE UPLOAD HANDLERS
# ============================================

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file upload"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    current_count = db.get_user_upload_count(user_id)
    user_limit = db.get_user_limit(user_id)
    
    if user_limit != float('inf') and current_count >= user_limit:
        await update.message.reply_text(
            f"❌ *Upload Limit Reached*\n\nYou have reached your upload limit of {user_limit} files.\n\nTo upload more files, please:\n• Buy credits to become premium\n• Become a reseller\n• Contact support\n\nSupport: {', '.join(SUPPORT_CONTACTS)}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    context.user_data['awaiting_file'] = True
    
    await update.message.reply_text(
        "📤 *Upload Your Script*\n\nPlease upload your Python (.py), JavaScript (.js), or ZIP (.zip) file.\n\n📋 *Requirements:*\n• Max file size: 20MB\n• File will be reviewed by admin\n• Approved scripts will be executable\n• You can run/stop scripts from 'My Scripts' menu\n\n⚠️ *Note:* Malicious code will lead to ban!\n\nSend your file now:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return AWAITING_FILE_UPLOAD

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process uploaded file"""
    user_id = update.effective_user.id
    document = update.message.document
    
    if not document:
        await update.message.reply_text("❌ Please send a valid file.", parse_mode=ParseMode.MARKDOWN)
        return AWAITING_FILE_UPLOAD
    
    if document.file_size > MAX_FILE_SIZE:
        await update.message.reply_text(f"❌ *File Too Large*\n\nMax size: 20MB\nYour file: {document.file_size / (1024*1024):.2f}MB", parse_mode=ParseMode.MARKDOWN)
        return AWAITING_FILE_UPLOAD
    
    file_name = document.file_name
    ext = os.path.splitext(file_name)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        await update.message.reply_text(f"❌ *Invalid File Type*\n\nAllowed: .py, .js, .zip\nYour file: {ext}", parse_mode=ParseMode.MARKDOWN)
        return AWAITING_FILE_UPLOAD
    
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    file = await context.bot.get_file(document.file_id)
    file_path = os.path.join(user_dir, file_name)
    await file.download_to_drive(file_path)
    
    db = DatabaseManager()
    approval_id = db.add_file_approval(user_id, file_name, file_path, ext[1:], update.message.message_id)
    
    if approval_id:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_file_{approval_id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_file_{approval_id}")]
        ])
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📁 *New File Approval Required*\n\n👤 User: {update.effective_user.first_name}\n🆔 ID: {user_id}\n📄 File: {file_name}\n📂 Type: {ext[1].upper()}\n🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nUse buttons below to approve/reject:",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            except:
                pass
        
        await update.message.reply_text(
            f"✅ *File Uploaded Successfully!*\n\n📄 File: {file_name}\n📂 Size: {document.file_size / 1024:.2f} KB\n\nYour file is now pending admin approval.\nYou will be notified once reviewed.\n\nApproved scripts will appear in 'My Scripts' menu.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_main_menu_keyboard()
        )
    else:
        await update.message.reply_text("❌ *Error Uploading File*\n\nPlease try again or contact support.", parse_mode=ParseMode.MARKDOWN)
    
    return ConversationHandler.END

async def my_scripts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's approved scripts"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    scripts = db.get_approved_files(user_id)
    
    if not scripts:
        await update.message.reply_text(
            "📁 *My Scripts*\n\nYou have no approved scripts yet.\n\nTo upload a script:\n1. Click '📤 Upload File' button\n2. Send your .py or .js file\n3. Wait for admin approval\n\nOnce approved, you can run your scripts here.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_main_menu_keyboard()
        )
        return
    
    message = "📁 *YOUR APPROVED SCRIPTS*\n\n"
    
    for script in scripts:
        file_name = script['file_name']
        process_id = f"{user_id}_{file_name}"
        is_running = process_id in running_processes and running_processes[process_id].poll() is None
        status_icon = "🟢 Running" if is_running else "⚪ Stopped"
        
        message += f"┃ *{file_name}*\n"
        message += f"┃ Status: {status_icon}\n"
        message += f"┃ Uploaded: {script['uploaded_time'][:16]}\n"
        message += f"┃ ━━━━━━━━━━━━━━━━━━━━\n"
    
    message += "\nSelect a script from below to control it:"
    
    keyboard = []
    for script in scripts:
        file_name = script['file_name']
        process_id = f"{user_id}_{file_name}"
        is_running = process_id in running_processes and running_processes[process_id].poll() is None
        status_icon = "🟢" if is_running else "⚪"
        keyboard.append([InlineKeyboardButton(f"{status_icon} {file_name}", callback_data=f"script_control_{user_id}_{file_name}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# ============================================
# SCRIPT CONTROL CALLBACKS
# ============================================

async def script_control_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle script control callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("script_control_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM file_approvals WHERE user_id = ? AND file_name = ? AND status = "approved"', (user_id, file_name))
    script = cursor.fetchone()
    conn.close()
    
    if not script:
        await query.edit_message_text("❌ Script not found!")
        return
    
    file_path = script['file_path']
    process_id = f"{user_id}_{file_name}"
    is_running = process_id in running_processes and running_processes[process_id].poll() is None
    
    message = f"📄 *Script Control*\n\n📁 File: {file_name}\n📂 Path: {file_path}\n🟢 Status: {'Running' if is_running else 'Stopped'}\n\nSelect an action:"
    
    keyboard = create_script_control_keyboard(user_id, file_name, is_running)
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def start_script_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start script callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("start_script_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM file_approvals WHERE user_id = ? AND file_name = ? AND status = "approved"', (user_id, file_name))
    script = cursor.fetchone()
    conn.close()
    
    if not script:
        await query.edit_message_text("❌ Script not found!")
        return
    
    script_manager = ScriptManager()
    success, message = script_manager.run_script(user_id, script['file_path'], file_name)
    
    if success:
        await query.edit_message_text(f"✅ *Script Started*\n\n📄 File: {file_name}\n📊 {message}\n\nUse 'My Scripts' to manage running scripts.", parse_mode=ParseMode.MARKDOWN)
    else:
        await query.edit_message_text(f"❌ *Failed to Start Script*\n\nError: {message}", parse_mode=ParseMode.MARKDOWN)

async def stop_script_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stop script callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("stop_script_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    script_manager = ScriptManager()
    success, message = script_manager.stop_script(user_id, file_name)
    
    if success:
        await query.edit_message_text(f"✅ *Script Stopped*\n\n📄 File: {file_name}\n📊 {message}", parse_mode=ParseMode.MARKDOWN)
    else:
        await query.edit_message_text(f"❌ *Failed to Stop Script*\n\nError: {message}", parse_mode=ParseMode.MARKDOWN)

async def restart_script_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle restart script callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("restart_script_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM file_approvals WHERE user_id = ? AND file_name = ? AND status = "approved"', (user_id, file_name))
    script = cursor.fetchone()
    conn.close()
    
    if not script:
        await query.edit_message_text("❌ Script not found!")
        return
    
    script_manager = ScriptManager()
    success, message = script_manager.restart_script(user_id, script['file_path'], file_name)
    
    if success:
        await query.edit_message_text(f"✅ *Script Restarted*\n\n📄 File: {file_name}\n📊 {message}", parse_mode=ParseMode.MARKDOWN)
    else:
        await query.edit_message_text(f"❌ *Failed to Restart Script*\n\nError: {message}", parse_mode=ParseMode.MARKDOWN)

async def logs_script_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view logs callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("logs_script_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    script_manager = ScriptManager()
    logs = script_manager.get_logs(user_id, file_name, 100)
    
    if len(logs) > 4000:
        logs = logs[-4000:] + "\n\n... (truncated)"
    
    await query.edit_message_text(f"📋 *Logs for {file_name}*\n\n```\n{logs}\n```", parse_mode=ParseMode.MARKDOWN)

async def delete_script_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete script callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("delete_script_", "").split("_")
    user_id = int(data[0])
    file_name = '_'.join(data[1:])
    
    script_manager = ScriptManager()
    success = script_manager.delete_script_files(user_id, file_name)
    
    if success:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM file_approvals WHERE user_id = ? AND file_name = ?', (user_id, file_name))
        conn.commit()
        conn.close()
        
        await query.edit_message_text(f"✅ *Script Deleted*\n\n📄 File: {file_name}\n\nThe script and its logs have been removed.", parse_mode=ParseMode.MARKDOWN)
    else:
        await query.edit_message_text(f"❌ *Failed to Delete Script*\n\nPlease try again.", parse_mode=ParseMode.MARKDOWN)

# ============================================
# OTHER USER HANDLERS
# ============================================

async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Referral button"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    referral_link = db.get_referral_link(user_id)
    stats = db.get_user_stats(user_id)
    
    message = (
        "👥 *REFERRAL PROGRAM*\n\nInvite friends and earn credits!\n\n"
        f"🔗 *Your Referral Link:*\n`{referral_link}`\n\n"
        f"📊 *Your Stats:*\n┃ 👥 Referrals: {stats.get('referrals_count', 0)}\n\n"
        "🎁 *Rewards (in credits):*\n"
        "• 10 referrals → 50 credits\n"
        "• 30 referrals → 150 credits\n"
        "• 70 referrals → 350 credits\n\n"
        "💡 *How it works:*\n"
        "1. Share your referral link\n"
        "2. Friends join using your link\n"
        "3. Both get access automatically\n"
        "4. Earn credits at milestones\n\n"
        "⚠️ *Note:* Only new users count\n"
        "Share your link now!"
    )
    
    keyboard = [[InlineKeyboardButton("📤 Share Link", switch_inline_query=referral_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def show_free_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Free Trial button"""
    message = (
        "🎁 *FREE TRIAL OFFER*\n\n"
        "Get a taste of our premium loaders!\n\n"
        "✨ *Trial Details:*\n"
        "• Duration: 2 Hours\n"
        "• Features: Basic features only\n"
        "• Limited availability\n\n"
        "📋 *Requirements:*\n"
        "• New users only\n"
        "• One trial per user\n\n"
        "🔧 *How to get trial:*\n"
        "1. Contact support\n"
        "2. Request trial access\n"
        "3. Get temporary key\n\n"
        f"⚠️ *Note:* Trial keys are limited\n\n"
        f"Contact support for trial:\n" + "\n".join(SUPPORT_CONTACTS)
    )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=create_main_menu_keyboard())

async def show_reseller_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Reseller Panel button"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    reseller_status = db.get_reseller_status(user_id)
    
    if reseller_status and reseller_status['status'] == 'active':
        expiry_date = datetime.strptime(reseller_status['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
        days_left = (expiry_date - datetime.now()).days
        
        message = (
            "👑 *RESELLER PANEL*\n\n"
            f"📊 *Your Status:*\n"
            f"┃ Type: {reseller_status['reseller_type']}\n"
            f"┃ Status: Active ✅\n"
            f"┃ Days Left: {days_left}\n"
            f"┃ Total Sales: {reseller_status['total_sales']}\n"
            f"┃ Revenue: ₹{reseller_status['total_revenue']}\n\n"
            "🔧 *Reseller Tools:*\n"
            "• Generate keys\n"
            "• View sales\n"
            "• Withdraw earnings\n"
            "• Stock management\n\n"
            "Contact admin for more info."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔑 Generate Key", callback_data="reseller_gen_key")],
            [InlineKeyboardButton("📊 Sales Stats", callback_data="reseller_stats")],
            [InlineKeyboardButton("💰 Withdraw", callback_data="reseller_withdraw")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        message = "👑 *BECOME A RESELLER*\n\nSell our loaders and earn commission!\n\n💰 *Reseller Packages:*\n"
        
        for package, price in RESELLER_PRICES.items():
            message += f"┃ {package:<12} → ₹{price}\n"
        
        message += (
            "\n✨ *Benefits:*\n"
            "• 30% discount on all loaders\n"
            "• Generate unlimited keys\n"
            "• Dedicated support\n"
            "• Weekly commission\n"
            "• Marketing materials\n\n"
            "📌 *How to become reseller:*\n"
            "1. Select package\n"
            "2. Make payment\n"
            "3. Wait for admin approval\n\n"
            "Select a package to proceed:"
        )
        
        keyboard = []
        for package, price in RESELLER_PRICES.items():
            keyboard.append([InlineKeyboardButton(f"{package} - ₹{price}", callback_data=f"reseller_{package}_{price}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def reseller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reseller package selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    package = data[1]
    price = int(data[2])
    
    context.user_data['reseller_package'] = package
    context.user_data['reseller_amount'] = price
    
    qr_buffer = generate_upi_qr(UPI_ID, price, f"Reseller Package - {package}")
    
    message = (
        f"👑 *Reseller Package*\n\n"
        f"📦 Package: {package}\n"
        f"💰 Amount: ₹{price}\n\n"
        f"🏦 *UPI ID:* `{UPI_ID}`\n\n"
        "Scan QR code or send payment to above UPI ID\n\n"
        "📸 *After payment:*\n"
        "1. Take screenshot\n"
        "2. Send screenshot\n"
        "3. Wait for approval\n\n"
        "Send payment screenshot to activate:"
    )
    
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
    await query.message.reply_photo(photo=qr_buffer, caption="🔍 *Scan to pay for reseller package*", parse_mode=ParseMode.MARKDOWN)
    
    return AWAITING_RESELLER_PAYMENT

async def handle_reseller_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reseller payment screenshot"""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = photo.file_id
    
    package = context.user_data.get('reseller_package')
    amount = context.user_data.get('reseller_amount')
    
    db = DatabaseManager()
    db.add_reseller_request(user_id, package, amount)
    
    for owner_id in OWNER_IDS:
        try:
            await context.bot.send_photo(
                chat_id=owner_id,
                photo=file_id,
                caption=f"👑 *New Reseller Request*\n\n👤 User: {update.effective_user.first_name}\n📦 Package: {package}\n💰 Amount: ₹{amount}\n\nUse /pending_resellers to approve",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
    
    await update.message.reply_text(
        "✅ *Reseller Request Received!*\n\nYour request is pending approval.\nYou will be notified once activated.\n\nThis usually takes 5-30 minutes.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_main_menu_keyboard()
    )
    
    return ConversationHandler.END

async def show_purchase_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Purchase Details button"""
    message = (
        "📸 *PURCHASE DETAILS*\n\n"
        "All purchase records are maintained in our system.\n\n"
        f"💰 *Price Plans:*\n"
    )
    
    db = DatabaseManager()
    price_plans = db.get_price_plans()
    
    for plan in price_plans:
        message += f"┃ {plan['duration']:<10} → {plan['credits']} credits\n"
    
    message += (
        f"\n🏦 *UPI ID:* `{UPI_ID}`\n\n"
        f"📢 *Purchase Channel:* [MENTAL PURCHASE DETAIL](https://t.me/MENTALPURCHASEDETAIL)\n\n"
        "⚠️ *Note:* Keep your payment screenshot for reference"
    )
    
    keyboard = [[InlineKeyboardButton("📱 Join Channel", url="https://t.me/MENTALPURCHASEDETAIL")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=reply_markup)

async def show_setup_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Setup Video button"""
    message = (
        "🎥 *LOADER SETUP VIDEO*\n\n"
        "Watch this video to learn how to:\n"
        "• Download and install loaders\n"
        "• Activate your key\n"
        "• Configure settings\n"
        "• Troubleshoot common issues\n\n"
        f"📹 [Watch Setup Video]({SETUP_VIDEO_LINK})\n\n"
        "⚠️ *Important:*\n"
        "• Follow steps exactly\n"
        "• Use VPN if needed\n"
        "• Disable Google Play Protect\n\n"
        "Need help? Contact support."
    )
    
    keyboard = [[InlineKeyboardButton("🎬 Watch Video", url=SETUP_VIDEO_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=reply_markup)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Support button"""
    message = (
        "❓ *SUPPORT CENTER*\n\n"
        "Need help? Contact our support team:\n\n"
        "👨‍💼 *Support Team:*\n" + 
        "\n".join([f"• {contact}" for contact in SUPPORT_CONTACTS]) +
        "\n\n📌 *Common Issues:*\n"
        "• Loader not working\n"
        "• Key activation failed\n"
        "• Payment issues\n"
        "• Technical problems\n\n"
        "⚡ *Response Time:* 5-30 minutes\n\n"
        "💡 *Tips:*\n"
        "• Provide screenshots\n"
        "• Describe your issue clearly\n"
        "• Be patient\n\n"
        "Click below to contact support:"
    )
    
    keyboard = [[InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_CONTACTS[0][1:]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# ============================================
# ADMIN/OWNER COMMANDS
# ============================================

@owner_only
async def add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add credits to user (owner only)"""
    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ *Usage:* `/add_credits [user_id] [amount]`\n\n"
            "Example: `/add_credits 123456789 100`\n\n"
            "Use `/add_credits` without arguments for interactive mode.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        
        db = DatabaseManager()
        if db.add_credits(user_id, amount, f"Admin added {amount} credits", update.effective_user.id):
            await update.message.reply_text(
                f"✅ *Credits Added!*\n\n"
                f"User: {user_id}\n"
                f"Amount: {amount} credits\n\n"
                f"Credits have been added to user's account.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ *{amount} Credits Added!*\n\n"
                         f"{amount} credits have been added to your account.\n"
                         f"Use /my_credits to check your balance.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to add credits!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid format! Use: `/add_credits [user_id] [amount]`", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def remove_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove credits from user (owner only)"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Usage:* `/remove_credits [user_id] [amount]`\n\n"
            "Example: `/remove_credits 123456789 50`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
        
        db = DatabaseManager()
        if db.remove_credits(user_id, amount, f"Admin removed {amount} credits", update.effective_user.id):
            await update.message.reply_text(
                f"✅ *Credits Removed!*\n\n"
                f"User: {user_id}\n"
                f"Amount: {amount} credits\n\n"
                f"Credits have been removed from user's account.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ *{amount} Credits Removed*\n\n"
                         f"{amount} credits have been removed from your account.\n"
                         f"Contact support if you have questions.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ Failed to remove credits! User may have insufficient balance.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Invalid format! Use: `/remove_credits [user_id] [amount]`", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def pending_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending credit purchases (owner only)"""
    db = DatabaseManager()
    pending = db.get_pending_credit_purchases()
    
    if not pending:
        await update.message.reply_text("✅ *No Pending Credit Purchases*", parse_mode=ParseMode.MARKDOWN)
        return
    
    for pend in pending[:10]:
        message = (
            f"💰 *Pending Credit Purchase #{pend['transaction_id']}*\n\n"
            f"👤 User: {pend['first_name']}\n"
            f"🆔 ID: {pend['user_id']}\n"
            f"💰 Amount: ₹{pend['payment_amount']}\n"
            f"✨ Credits: {pend['amount']}\n"
            f"🕐 Time: {pend['timestamp']}\n\n"
            f"Use:\n"
            f"/verify_credit {pend['transaction_id']} - to verify\n"
            f"/reject_credit {pend['transaction_id']} - to reject"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Verify", callback_data=f"admin_verify_credit_{pend['transaction_id']}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_credit_{pend['transaction_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if pend['payment_screenshot']:
            try:
                await update.message.reply_photo(
                    photo=pend['payment_screenshot'],
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except:
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

@owner_only
async def verify_credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify credit purchase (owner only)"""
    if not context.args:
        await update.message.reply_text(
            "❌ *Usage:* `/verify_credit [transaction_id]`\n\n"
            "Use /pending_credits to see pending transactions.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        transaction_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid transaction ID!")
        return
    
    db = DatabaseManager()
    success = db.verify_credit_purchase(transaction_id, update.effective_user.id)
    
    if success:
        # Get transaction details to notify user
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM credits_transactions WHERE transaction_id = ?', (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()
        
        if transaction:
            try:
                await context.bot.send_message(
                    chat_id=transaction['user_id'],
                    text=f"✅ *Credits Added!*\n\n"
                         f"Your credit purchase of {transaction['amount']} credits has been verified!\n"
                         f"💰 Your balance has been updated.\n\n"
                         f"Use /my_credits to check your balance.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await update.message.reply_text(f"✅ Credit purchase #{transaction_id} verified successfully!", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ Failed to verify credit purchase!", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def reject_credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject credit purchase (owner only)"""
    if not context.args:
        await update.message.reply_text(
            "❌ *Usage:* `/reject_credit [transaction_id]`\n\n"
            "Use /pending_credits to see pending transactions.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        transaction_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid transaction ID!")
        return
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM credits_transactions WHERE transaction_id = ? AND status = "pending"', (transaction_id,))
        transaction = cursor.fetchone()
        
        if transaction:
            cursor.execute('UPDATE credits_transactions SET status = "rejected" WHERE transaction_id = ?', (transaction_id,))
            conn.commit()
            
            try:
                await context.bot.send_message(
                    chat_id=transaction['user_id'],
                    text="❌ *Credit Purchase Rejected*\n\n"
                         "Your credit purchase has been rejected.\n\n"
                         "Possible reasons:\n"
                         "• Wrong amount\n"
                         "• Invalid screenshot\n"
                         "• Payment not received\n\n"
                         f"Contact support: {', '.join(SUPPORT_CONTACTS)}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
            
            await update.message.reply_text(f"✅ Credit purchase #{transaction_id} rejected!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Transaction not found!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error rejecting credit: {e}")
        await update.message.reply_text("❌ Failed to reject credit purchase!", parse_mode=ParseMode.MARKDOWN)
    finally:
        conn.close()

@owner_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics (owner only)"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total_users FROM users')
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute('SELECT SUM(credits_balance) as total_credits FROM users')
    total_credits = cursor.fetchone()['total_credits'] or 0
    
    cursor.execute('SELECT SUM(credits_cost) as total_revenue FROM purchases WHERE status = "completed"')
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    
    cursor.execute('SELECT COUNT(*) as total_purchases FROM purchases WHERE status = "completed"')
    total_purchases = cursor.fetchone()['total_purchases']
    
    cursor.execute('SELECT SUM(amount) as total_credits_sold FROM credits_transactions WHERE transaction_type = "credit_purchase" AND status = "completed"')
    total_credits_sold = cursor.fetchone()['total_credits_sold'] or 0
    
    cursor.execute('SELECT COUNT(*) as active_resellers FROM resellers WHERE status = "active" AND expiry_date > ?', (datetime.now(),))
    active_resellers = cursor.fetchone()['active_resellers']
    
    cursor.execute('SELECT COUNT(*) as pending_files FROM file_approvals WHERE status = "pending"')
    pending_files = cursor.fetchone()['pending_files']
    
    cursor.execute('SELECT COUNT(*) as approved_files FROM file_approvals WHERE status = "approved"')
    approved_files = cursor.fetchone()['approved_files']
    
    cursor.execute('SELECT COUNT(*) as pending_credits FROM credits_transactions WHERE transaction_type = "credit_purchase" AND status = "pending"')
    pending_credits = cursor.fetchone()['pending_credits']
    
    running_scripts = len([p for p in running_processes.values() if p.poll() is None])
    
    conn.close()
    
    message = (
        "📊 *BOT STATISTICS*\n\n"
        f"👥 *Users:*\n"
        f"┃ Total: {total_users}\n\n"
        f"💰 *Credits System:*\n"
        f"┃ Total Credits in Circulation: {total_credits:,}\n"
        f"┃ Total Credits Sold: {total_credits_sold:,}\n"
        f"┃ Total Revenue: {total_revenue:,} credits\n"
        f"┃ Total Purchases: {total_purchases}\n"
        f"┃ Pending Credit Purchases: {pending_credits}\n\n"
        f"👑 *Resellers:*\n"
        f"┃ Active: {active_resellers}\n\n"
        f"📁 *Files:*\n"
        f"┃ Pending: {pending_files}\n"
        f"┃ Approved: {approved_files}\n"
        f"┃ Running Scripts: {running_scripts}\n\n"
        f"📈 *System:*\n"
        f"┃ Database: SQLite3\n"
        f"┃ Status: Online ✅\n"
        f"┃ Uptime: Active\n\n"
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@owner_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast (owner only)"""
    if not context.args:
        await update.message.reply_text(
            "❌ *Usage:* `/broadcast [message]`\n\n"
            "Or send a photo/video with caption as broadcast.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    message = ' '.join(context.args)
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Send", callback_data="confirm_broadcast")],
        [InlineKeyboardButton("❌ No, Cancel", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ *Confirm Broadcast*\n\nMessage:\n{message}\n\nSend to all users?\nThis action cannot be undone!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    
    context.user_data['broadcast_message'] = message
    context.user_data['broadcast_media'] = None
    context.user_data['broadcast_media_type'] = 'text'

async def broadcast_with_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast with media"""
    if update.effective_user.id not in OWNER_IDS:
        return
    
    media_file_id = None
    media_type = None
    caption = update.message.caption or ""
    
    if update.message.photo:
        media_file_id = update.message.photo[-1].file_id
        media_type = "photo"
    elif update.message.video:
        media_file_id = update.message.video.file_id
        media_type = "video"
    elif update.message.document:
        media_file_id = update.message.document.file_id
        media_type = "document"
    else:
        await broadcast_command(update, context)
        return
    
    context.user_data['broadcast_message'] = caption
    context.user_data['broadcast_media'] = media_file_id
    context.user_data['broadcast_media_type'] = media_type
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Send", callback_data="confirm_broadcast")],
        [InlineKeyboardButton("❌ No, Cancel", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ *Confirm Broadcast*\n\nMedia Type: {media_type}\nCaption: {caption}\n\nSend to all users?\nThis action cannot be undone!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def confirm_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute broadcast"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in OWNER_IDS:
        await query.edit_message_text("⛔ Access Denied!")
        return
    
    db = DatabaseManager()
    users = db.get_all_users()
    
    if not users:
        await query.edit_message_text("❌ No users found in database!")
        return
    
    await query.edit_message_text("📢 *Starting Broadcast...*\n\nProcessing...", parse_mode=ParseMode.MARKDOWN)
    
    message = context.user_data.get('broadcast_message', '')
    media_file_id = context.user_data.get('broadcast_media')
    media_type = context.user_data.get('broadcast_media_type', 'text')
    
    broadcast_id = db.add_broadcast(message, media_file_id, media_type, user_id)
    
    sent = 0
    delivered = 0
    failed = 0
    status_msg = await query.message.edit_text(
        f"📢 *Broadcast in Progress...*\n\n👥 Total: {len(users)}\n✅ Sent: 0\n📨 Delivered: 0\n❌ Failed: 0",
        parse_mode=ParseMode.MARKDOWN
    )
    
    for user in users:
        try:
            if media_type == "photo":
                await context.bot.send_photo(chat_id=user['user_id'], photo=media_file_id, caption=message, parse_mode=ParseMode.MARKDOWN)
            elif media_type == "video":
                await context.bot.send_video(chat_id=user['user_id'], video=media_file_id, caption=message, parse_mode=ParseMode.MARKDOWN)
            elif media_type == "document":
                await context.bot.send_document(chat_id=user['user_id'], document=media_file_id, caption=message, parse_mode=ParseMode.MARKDOWN)
            else:
                await context.bot.send_message(chat_id=user['user_id'], text=message, parse_mode=ParseMode.MARKDOWN)
            delivered += 1
            sent += 1
        except:
            failed += 1
            sent += 1
        
        if sent % 50 == 0:
            await status_msg.edit_text(
                f"📢 *Broadcast in Progress...*\n\n👥 Total: {len(users)}\n✅ Sent: {sent}\n📨 Delivered: {delivered}\n❌ Failed: {failed}\n📊 Progress: {(sent/len(users))*100:.1f}%",
                parse_mode=ParseMode.MARKDOWN
            )
        
        await asyncio.sleep(0.05)
    
    db.update_broadcast_stats(broadcast_id, sent, delivered, failed)
    
    await status_msg.edit_text(
        f"✅ *Broadcast Complete!*\n\n👥 Total Users: {len(users)}\n📨 Delivered: {delivered}\n❌ Failed: {failed}\n\n📊 Success Rate: {(delivered/len(users))*100:.1f}%",
        parse_mode=ParseMode.MARKDOWN
    )
    
    for key in ['broadcast_message', 'broadcast_media', 'broadcast_media_type']:
        if key in context.user_data:
            del context.user_data[key]

@owner_only
async def add_loader_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new loader (owner only)"""
    await update.message.reply_text("➕ *Add New Loader*\n\nSend the loader name:", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_NEW_LOADER_NAME

async def add_loader_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get loader name"""
    context.user_data['new_loader_name'] = update.message.text
    await update.message.reply_text("📎 *Send Loader Link:*\n\nSend the download link for this loader:", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_NEW_LOADER_LINK

async def add_loader_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get loader link"""
    context.user_data['new_loader_link'] = update.message.text
    await update.message.reply_text("📝 *Send Loader Features:*\n\nSend the features list for this loader\n(You can send as text):", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_NEW_LOADER_FEATURES

async def add_loader_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get loader features and save"""
    features = update.message.text
    
    db = DatabaseManager()
    success = db.add_loader(context.user_data['new_loader_name'], context.user_data['new_loader_link'], features, update.effective_user.id)
    
    if success:
        await update.message.reply_text(f"✅ *Loader Added!*\n\nName: {context.user_data['new_loader_name']}\n\nUsers can now purchase this loader.", parse_mode=ParseMode.MARKDOWN, reply_markup=create_main_menu_keyboard())
    else:
        await update.message.reply_text("❌ *Failed to Add Loader*\n\nLoader may already exist or database error.", parse_mode=ParseMode.MARKDOWN)
    
    for key in ['new_loader_name', 'new_loader_link']:
        if key in context.user_data:
            del context.user_data[key]
    
    return ConversationHandler.END

@owner_only
async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup database (owner only)"""
    await update.message.reply_text("📤 *Creating Database Backup...*\n\nPlease wait...", parse_mode=ParseMode.MARKDOWN)
    
    backup_file = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy(DATABASE_PATH, backup_file)
    
    with open(backup_file, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=os.path.basename(backup_file),
            caption=f"✅ *Database Backup*\n\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nSize: {os.path.getsize(backup_file) / 1024:.2f} KB",
            parse_mode=ParseMode.MARKDOWN
        )
    
    os.remove(backup_file)

@owner_only
async def lock_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lock bot for maintenance (owner only)"""
    global BOT_LOCKED
    BOT_LOCKED = True
    await update.message.reply_text("🔒 *Bot Locked*\n\nBot is now in maintenance mode. Only owners can access.", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def unlock_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unlock bot (owner only)"""
    global BOT_LOCKED
    BOT_LOCKED = False
    await update.message.reply_text("🔓 *Bot Unlocked*\n\nBot is now accessible to all users.", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def run_all_scripts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run all approved scripts for all users (owner only)"""
    await update.message.reply_text("🚀 *Starting All Scripts*\n\nThis may take a while...", parse_mode=ParseMode.MARKDOWN)
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, file_path, file_name FROM file_approvals WHERE status = "approved"')
    scripts = cursor.fetchall()
    conn.close()
    
    script_manager = ScriptManager()
    started = 0
    failed = 0
    
    for script in scripts:
        success, _ = script_manager.run_script(script['user_id'], script['file_path'], script['file_name'])
        if success:
            started += 1
        else:
            failed += 1
        await asyncio.sleep(0.5)
    
    await update.message.reply_text(f"✅ *Script Execution Complete*\n\nStarted: {started}\nFailed: {failed}", parse_mode=ParseMode.MARKDOWN)

@owner_only
async def pending_resellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending reseller requests (owner only)"""
    db = DatabaseManager()
    pending = db.get_pending_resellers()
    
    if not pending:
        await update.message.reply_text("✅ *No Pending Reseller Requests*", parse_mode=ParseMode.MARKDOWN)
        return
    
    for pend in pending:
        message = (
            f"👑 *Pending Reseller*\n\n"
            f"👤 User: {pend['first_name']}\n"
            f"🆔 ID: {pend['user_id']}\n"
            f"📦 Package: {pend['reseller_type']}\n"
            f"💰 Amount: ₹{pend['amount_paid']}\n"
            f"🕐 Time: {pend['purchase_date']}\n\n"
            f"Use /approve_reseller {pend['user_id']} to approve"
        )
        
        keyboard = [[InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_reseller_{pend['user_id']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

@owner_only
async def approve_reseller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve reseller request (owner only)"""
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/approve_reseller [user_id]`\n\nUse /pending_resellers to see pending requests.", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user ID!")
        return
    
    db = DatabaseManager()
    success = db.approve_reseller(user_id, update.effective_user.id)
    
    if success:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ *Reseller Status Approved!*\n\nCongratulations! You are now an official reseller.\nAccess your reseller panel from the main menu.",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
        
        await update.message.reply_text(f"✅ User {user_id} is now a reseller!")
    else:
        await update.message.reply_text("❌ Failed to approve reseller!")

@owner_only
async def pending_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending file approvals (owner only)"""
    db = DatabaseManager()
    pending = db.get_pending_files()
    
    if not pending:
        await update.message.reply_text("✅ *No Pending File Approvals*\n\nAll files have been reviewed.", parse_mode=ParseMode.MARKDOWN)
        return
    
    for pend in pending[:10]:
        message = (
            f"📁 *Pending File #{pend['id']}*\n\n"
            f"👤 User: {pend['first_name']}\n"
            f"🆔 ID: {pend['user_id']}\n"
            f"📄 File: {pend['file_name']}\n"
            f"📂 Type: {pend['file_type']}\n"
            f"🕐 Time: {pend['uploaded_time']}\n\n"
            f"Use:\n/approve_file {pend['id']} - to approve\n/reject_file {pend['id']} [reason] - to reject"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_file_{pend['id']}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_file_{pend['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

@owner_only
async def approve_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a file (owner only)"""
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/approve_file [file_id]`\n\nUse /pending_files to see pending file IDs.", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        file_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid file ID!")
        return
    
    db = DatabaseManager()
    success = db.approve_file(file_id, update.effective_user.id, "Approved by owner")
    
    if success:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM file_approvals WHERE id = ?', (file_id,))
        file_info = cursor.fetchone()
        conn.close()
        
        if file_info:
            try:
                await context.bot.send_message(
                    chat_id=file_info['user_id'],
                    text=f"✅ *File Approved!*\n\n📄 File: {file_info['file_name']}\n\nYour script has been approved!\nYou can now run it from 'My Scripts' menu.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await update.message.reply_text(f"✅ File #{file_id} approved successfully!")
    else:
        await update.message.reply_text("❌ Failed to approve file!")

@owner_only
async def reject_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a file (owner only)"""
    if len(context.args) < 1:
        await update.message.reply_text("❌ *Usage:* `/reject_file [file_id] [reason]`\n\nUse /pending_files to see pending file IDs.", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        file_id = int(context.args[0])
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
    except:
        await update.message.reply_text("❌ Invalid file ID!")
        return
    
    db = DatabaseManager()
    success = db.reject_file(file_id, update.effective_user.id, reason)
    
    if success:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM file_approvals WHERE id = ?', (file_id,))
        file_info = cursor.fetchone()
        conn.close()
        
        if file_info:
            try:
                await context.bot.send_message(
                    chat_id=file_info['user_id'],
                    text=f"❌ *File Rejected*\n\n📄 File: {file_info['file_name']}\n\nReason: {reason}\n\nPlease fix the issues and re-upload.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await update.message.reply_text(f"✅ File #{file_id} rejected successfully!")
    else:
        await update.message.reply_text("❌ Failed to reject file!")

# ============================================
# ERROR HANDLING
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"⚠️ *An error occurred*\n\nPlease try again later or contact support.\n\nSupport: {', '.join(SUPPORT_CONTACTS)}",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❓ *Unknown Command*\n\nUse /start to see available commands\nor use the menu buttons below.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_main_menu_keyboard()
    )

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu callback"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🏠 *Main Menu*", parse_mode=ParseMode.MARKDOWN, reply_markup=create_main_menu_keyboard())
    await query.message.delete()

# ============================================
# MAIN BOT FUNCTION
# ============================================

async def post_init(application: Application):
    """Post initialization function"""
    logger.info("Bot started successfully!")
    logger.info(f"Bot username: {BOT_USERNAME}")
    logger.info(f"Owners: {', '.join([str(owner_id) for owner_id in OWNER_IDS])}")
    
    for owner_id in OWNER_IDS:
        try:
            await application.bot.send_message(
                chat_id=owner_id,
                text=f"🤖 *Bot Started Successfully!*\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nStatus: Online ✅\n\nAll systems operational.",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass

def main():
    """Main function to run the bot"""
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    db = DatabaseManager()
    logger.info("Database initialized")
    
    # Conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(upload_credit_screenshot_callback, pattern="^upload_credit_screenshot$"),
            CallbackQueryHandler(reseller_callback, pattern="^reseller_"),
            MessageHandler(filters.TEXT & filters.Regex("^💰 Buy Credits$"), buy_credits),
            MessageHandler(filters.TEXT & filters.Regex("^📤 Upload File$"), upload_file),
        ],
        states={
            AWAITING_CREDIT_PAYMENT_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_credit_payment_screenshot),
            ],
            AWAITING_RESELLER_PAYMENT: [
                MessageHandler(filters.PHOTO, handle_reseller_payment),
            ],
            AWAITING_FILE_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_file_upload),
            ],
            AWAITING_NEW_LOADER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_loader_name),
            ],
            AWAITING_NEW_LOADER_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_loader_link),
            ],
            AWAITING_NEW_LOADER_FEATURES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_loader_features),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", unknown_command),
            MessageHandler(filters.COMMAND, unknown_command),
        ],
        allow_reentry=True
    )
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("home", home))
    application.add_handler(CommandHandler("loaders", show_loaders))
    application.add_handler(CommandHandler("buy_credits", buy_credits))
    application.add_handler(CommandHandler("my_credits", my_credits))
    application.add_handler(CommandHandler("purchase", show_loaders))
    application.add_handler(CommandHandler("referral", show_referral))
    application.add_handler(CommandHandler("support", show_support))
    
    # Owner/Admin commands
    application.add_handler(CommandHandler("add_credits", add_credits_command))
    application.add_handler(CommandHandler("remove_credits", remove_credits_command))
    application.add_handler(CommandHandler("pending_credits", pending_credits))
    application.add_handler(CommandHandler("verify_credit", verify_credit_command))
    application.add_handler(CommandHandler("reject_credit", reject_credit_command))
    application.add_handler(CommandHandler("pending", pending_credits))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("add_loader", add_loader_command))
    application.add_handler(CommandHandler("backup", backup_database))
    application.add_handler(CommandHandler("pending_files", pending_files))
    application.add_handler(CommandHandler("approve_file", approve_file_command))
    application.add_handler(CommandHandler("reject_file", reject_file_command))
    application.add_handler(CommandHandler("pending_resellers", pending_resellers))
    application.add_handler(CommandHandler("approve_reseller", approve_reseller_command))
    application.add_handler(CommandHandler("lock_bot", lock_bot))
    application.add_handler(CommandHandler("unlock_bot", unlock_bot))
    application.add_handler(CommandHandler("run_all_scripts", run_all_scripts))
    
    application.add_handler(conv_handler)
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🏠 Home$"), home))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📦 Loaders$"), show_loaders))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💰 Buy Credits$"), buy_credits))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^👥 Referral$"), show_referral))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💳 Purchase$"), show_loaders))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^👑 Reseller Panel$"), show_reseller_panel))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📤 Upload File$"), upload_file))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📁 My Scripts$"), my_scripts))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📢 Broadcast$"), broadcast_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^❓ Support$"), show_support))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📸 Purchase Details$"), show_purchase_details))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🎥 Setup Video$"), show_setup_video))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📢 Contact Channel$"), contact_channel))
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, broadcast_with_media))
    application.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, broadcast_with_media))
    application.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, broadcast_with_media))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(credit_plan_callback, pattern="^credit_plan_"))
    application.add_handler(CallbackQueryHandler(loader_callback, pattern="^loader_"))
    application.add_handler(CallbackQueryHandler(duration_callback, pattern="^duration_"))
    application.add_handler(CallbackQueryHandler(confirm_purchase_callback, pattern="^confirm_purchase_"))
    application.add_handler(CallbackQueryHandler(upload_credit_screenshot_callback, pattern="^upload_credit_screenshot$"))
    application.add_handler(CallbackQueryHandler(script_control_callback, pattern="^script_control_"))
    application.add_handler(CallbackQueryHandler(start_script_callback, pattern="^start_script_"))
    application.add_handler(CallbackQueryHandler(stop_script_callback, pattern="^stop_script_"))
    application.add_handler(CallbackQueryHandler(restart_script_callback, pattern="^restart_script_"))
    application.add_handler(CallbackQueryHandler(logs_script_callback, pattern="^logs_script_"))
    application.add_handler(CallbackQueryHandler(delete_script_callback, pattern="^delete_script_"))
    application.add_handler(CallbackQueryHandler(confirm_broadcast_callback, pattern="^confirm_broadcast$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_my_scripts$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_loaders$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_duration$"))
    
    application.add_error_handler(error_handler)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.TEXT, unknown_command))
    
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

# End of bot code - Total lines: 5432
