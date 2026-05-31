#!/usr/bin/env python3
"""
MENTAL CHEAT SHOP - Telegram Bot
Version: 4.5.0 - Railway Production Ready
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
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

# File Configuration
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.py', '.js', '.zip'}

# Channel Verification
REQUIRED_CHANNELS = [
    {"id": "channel_1", "url": "https://t.me/+Cbgy8_v9d-BmOWM1", "username": "@MENTALCHEAT1"},
    {"id": "channel_2", "url": "https://t.me/+3Bcd86oEyr5jODQ1", "username": "@MENTALCHEAT2"},
    {"id": "channel_3", "url": "https://t.me/+p7-JZZTJlgdmOGE1", "username": "@MENTALCHEAT3"}
]

# Owner Configuration
OWNER_IDS = [8420590053, 6650888707, 8033555435]
ADMIN_IDS = [8420590053, 6650888707, 8033555435]

SUPPORT_CONTACTS = ["@TylerDurden21", "@SegsyToxic", "@MentalOfficial69"]

# Payment Configuration
UPI_ID = "msuhasvardhan@fam"
PURCHASE_CHANNEL = "https://t.me/MENTALPURCHASEDETAIL"
PURCHASE_CHANNEL_ID = -1003954802330

# Setup Video
SETUP_VIDEO_LINK = "https://youtu.be/EihjAoje3z8"

# Bot Lock Status
BOT_LOCKED = False

# Loader Data
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

# Price Plans
PRICE_PLANS = {
    "1 Day": 80,
    "3 Days": 150,
    "7 Days": 300,
    "15 Days": 500,
    "30 Days": 650,
    "2 Months": 800
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

# Referral Rewards
REFERRAL_REWARDS = {
    10: {"reward": "1 day key", "duration": "1 Day", "days": 1},
    30: {"reward": "3 days key", "duration": "3 Days", "days": 3},
    70: {"reward": "7 days key", "duration": "7 Days", "days": 7}
}

# Conversation States
(
    AWAITING_PAYMENT_SCREENSHOT,
    AWAITING_RESELLER_PAYMENT,
    AWAITING_BROADCAST_MESSAGE,
    AWAITING_EDIT_PRICE,
    AWAITING_NEW_LOADER_NAME,
    AWAITING_NEW_LOADER_LINK,
    AWAITING_NEW_LOADER_FEATURES,
    AWAITING_FILE_UPLOAD,
) = range(8)

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
    """Complete database management system with persistent storage"""
    
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
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP,
                referrals_count INTEGER DEFAULT 0,
                referred_by INTEGER,
                is_verified BOOLEAN DEFAULT 0,
                verification_date TIMESTAMP,
                is_banned BOOLEAN DEFAULT 0,
                ban_reason TEXT,
                total_spent INTEGER DEFAULT 0,
                subscription_expiry TIMESTAMP,
                user_type TEXT DEFAULT 'free',
                last_active TIMESTAMP,
                language_code TEXT,
                phone_number TEXT
            )
        ''')
        
        # Purchases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                loader_name TEXT,
                duration TEXT,
                amount INTEGER,
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
                amount INTEGER,
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
                amount INTEGER,
                updated_by INTEGER,
                updated_date TIMESTAMP
            )
        ''')
        
        # Channel verification table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_verification (
                user_id INTEGER PRIMARY KEY,
                channel_1_joined BOOLEAN DEFAULT 0,
                channel_2_joined BOOLEAN DEFAULT 0,
                channel_3_joined BOOLEAN DEFAULT 0,
                verified_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Insert default price plans
        for duration, amount in PRICE_PLANS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO price_plans (duration, amount, updated_date)
                VALUES (?, ?, ?)
            ''', (duration, amount, datetime.now()))
        
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
                            self.give_referral_reward(referred_by, reward['duration'])
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
    
    def give_referral_reward(self, user_id: int, duration: str) -> Optional[str]:
        """Give referral reward to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            key_code = self.generate_key()
            expiry_date = datetime.now() + timedelta(days=self.get_duration_days(duration))
            
            cursor.execute('''
                INSERT INTO keys (key_code, loader_name, duration, expiry_date, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', ('ALL_LOADERS', duration, key_code, expiry_date, datetime.now()))
            
            conn.commit()
            return key_code
        except Exception as e:
            logger.error(f"Error giving referral reward: {e}")
            return None
        finally:
            conn.close()
    
    def generate_key(self) -> str:
        """Generate unique key for loader access"""
        return f"MC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=16))}"
    
    def get_duration_days(self, duration: str) -> int:
        """Convert duration string to days"""
        duration_map = {
            "1 Day": 1, "3 Days": 3, "7 Days": 7,
            "15 Days": 15, "30 Days": 30, "2 Months": 60
        }
        return duration_map.get(duration, 1)
    
    def add_purchase(self, user_id: int, loader_name: str, duration: str, 
                     amount: int, screenshot_file_id: str) -> Optional[int]:
        """Add new purchase record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO purchases (user_id, loader_name, duration, amount, 
                                     payment_screenshot, purchase_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, loader_name, duration, amount, screenshot_file_id, 
                  datetime.now(), 'pending'))
            
            purchase_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO pending_verifications (user_id, loader_name, duration, 
                                                  amount, screenshot_file_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, loader_name, duration, amount, screenshot_file_id, datetime.now()))
            
            conn.commit()
            return purchase_id
        except Exception as e:
            logger.error(f"Error adding purchase: {e}")
            return None
        finally:
            conn.close()
    
    def verify_payment(self, pending_id: int, verified_by: int):
        """Verify payment and issue key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM pending_verifications WHERE id = ? AND status = "pending"', (pending_id,))
            pending = cursor.fetchone()
            
            if not pending:
                return False
            
            key_code = self.generate_key()
            expiry_date = datetime.now() + timedelta(days=self.get_duration_days(pending['duration']))
            
            cursor.execute('''
                INSERT INTO keys (key_code, loader_name, duration, expiry_date, created_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key_code, pending['loader_name'], pending['duration'], expiry_date, datetime.now(), verified_by))
            
            cursor.execute('''
                UPDATE users SET user_type = 'subscribed', subscription_expiry = ? WHERE user_id = ?
            ''', (expiry_date, pending['user_id']))
            
            cursor.execute('''
                UPDATE purchases SET status = 'verified', key_issued = ?, verified_by = ?, verification_date = ?
                WHERE user_id = ? AND loader_name = ? AND purchase_date = ?
            ''', (key_code, verified_by, datetime.now(), pending['user_id'], pending['loader_name'], pending['timestamp']))
            
            cursor.execute('UPDATE pending_verifications SET status = "verified" WHERE id = ?', (pending_id,))
            cursor.execute('UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?', (pending['amount'], pending['user_id']))
            
            conn.commit()
            return key_code
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return False
        finally:
            conn.close()
    
    def get_pending_verifications(self) -> List[Dict]:
        """Get all pending verifications"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT p.*, u.username, u.first_name 
                FROM pending_verifications p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.status = 'pending'
                ORDER BY p.timestamp DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending verifications: {e}")
            return []
        finally:
            conn.close()
    
    def check_user_verification(self, user_id: int) -> bool:
        """Check if user has verified channel membership"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['is_verified'] == 1 if result else False
        except Exception as e:
            logger.error(f"Error checking user verification: {e}")
            return False
        finally:
            conn.close()
    
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
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                return {}
            
            cursor.execute('SELECT COUNT(*) as total_purchases, SUM(amount) as total_spent FROM purchases WHERE user_id = ? AND status = "verified"', (user_id,))
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
                'is_verified': user['is_verified'],
                'user_type': user['user_type'],
                'subscription_expiry': user['subscription_expiry']
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
            cursor.execute('SELECT user_id, username, first_name, join_date, is_verified FROM users')
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
            cursor.execute('SELECT * FROM price_plans ORDER BY amount')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting price plans: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_limit(self, user_id: int) -> int:
        """Get user's file upload limit"""
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
        elif user_type == 'subscribed':
            return SUBSCRIBED_USER_LIMIT
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

# ============================================
# SCRIPT EXECUTION MANAGER
# ============================================

class ScriptManager:
    """Manage execution of approved Python and JavaScript scripts"""
    
    def __init__(self):
        self.processes = running_processes
        self.upload_dir = UPLOAD_DIR
        self.logs_dir = LOGS_DIR
    
    def get_user_scripts(self, user_id: int) -> List[Dict]:
        """Get all approved scripts for a user"""
        db = DatabaseManager()
        return db.get_approved_files(user_id)
    
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
    """Decorator to restrict commands to verified users only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        global BOT_LOCKED
        
        if BOT_LOCKED:
            await update.message.reply_text(
                "🔒 *Bot is Under Maintenance*\n\nPlease try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        user_id = update.effective_user.id
        
        if user_id in OWNER_IDS:
            return await func(update, context, *args, **kwargs)
        
        db = DatabaseManager()
        if not db.check_user_verification(user_id):
            await update.message.reply_text(
                "🔒 *Verification Required*\n\nPlease verify yourself by joining our channels first.\n\nUse /verify command to start verification.",
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
    """Create main menu keyboard"""
    keyboard = [
        [KeyboardButton("🏠 Home"), KeyboardButton("📦 Loaders")],
        [KeyboardButton("🎁 Free Trial"), KeyboardButton("👥 Referral")],
        [KeyboardButton("💰 Purchase"), KeyboardButton("👑 Reseller Panel")],
        [KeyboardButton("📤 Upload File"), KeyboardButton("📁 My Scripts")],
        [KeyboardButton("📢 Broadcast"), KeyboardButton("❓ Support")],
        [KeyboardButton("📸 Purchase Details"), KeyboardButton("🎥 Setup Video")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def create_loader_keyboard(loaders: List[Dict]) -> InlineKeyboardMarkup:
    """Create loader selection keyboard"""
    keyboard = []
    for loader in loaders:
        keyboard.append([InlineKeyboardButton(loader['loader_name'], callback_data=f"loader_{loader['loader_name']}")])
    return InlineKeyboardMarkup(keyboard)

def create_duration_keyboard(loader_name: str, price_plans: List[Dict]) -> InlineKeyboardMarkup:
    """Create duration selection keyboard with prices"""
    keyboard = []
    for plan in price_plans:
        keyboard.append([InlineKeyboardButton(f"{plan['duration']} - ₹{plan['amount']}", callback_data=f"duration_{loader_name}_{plan['duration']}_{plan['amount']}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_loaders")])
    return InlineKeyboardMarkup(keyboard)

def create_payment_keyboard(loader_name: str, duration: str, amount: int) -> InlineKeyboardMarkup:
    """Create payment keyboard"""
    keyboard = [
        [InlineKeyboardButton("💳 Pay via UPI", callback_data=f"pay_{loader_name}_{duration}_{amount}")],
        [InlineKeyboardButton("📸 Upload Payment Screenshot", callback_data=f"upload_screenshot_{loader_name}_{duration}_{amount}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_duration")]
    ]
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

# ============================================
# BOT HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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
    
    is_verified = db.check_user_verification(user_id)
    
    if not is_verified:
        await send_verification_message(update, context)
    else:
        await send_welcome_message(update, context)

async def send_verification_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send verification message with channel links"""
    message = "🔐 *VERIFICATION REQUIRED*\n\nPlease join all the channels below to access the bot:\n\n"
    
    for i, channel in enumerate(REQUIRED_CHANNELS, 1):
        message += f"{i}. [Channel {i}]({channel['url']})\n"
    
    message += "\n⚠️ *Important:*\n• Join all 3 channels\n• After joining, click 'Verify' button\n• You need to join permanently\n\n_Note: If you're already joined, click verify_"
    
    keyboard = [[InlineKeyboardButton("✅ Verify Membership", callback_data="verify_channels")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=reply_markup)

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message to verified users"""
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
        f"┃ 💰 Total Spent: ₹{stats.get('total_spent', 0)}\n"
        f"┃ 🎫 Active Keys: {stats.get('active_keys', 0)}\n"
        f"┃ 📁 Upload Limit: {db.get_user_limit(user_id)} files\n\n"
        f"⚡ Use the menu below to get started!"
    )
    
    reply_markup = create_main_menu_keyboard()
    
    if profile_photo:
        await update.message.reply_photo(photo=profile_photo, caption=welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verify button callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    all_joined = True
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel['username'], user_id=user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                all_joined = False
                break
        except:
            all_joined = False
    
    if all_joined:
        db = DatabaseManager()
        db.verify_user(user_id)
        
        await query.edit_message_text("✅ *Verification Successful!*\n\nYou have been verified. Starting bot...", parse_mode=ParseMode.MARKDOWN)
        
        mock_update = Update(update.update_id)
        mock_update.effective_user = query.from_user
        mock_update.effective_chat = query.message.chat
        mock_update.message = query.message
        
        await asyncio.sleep(1)
        await send_welcome_message(mock_update, context)
    else:
        await query.edit_message_text(
            "❌ *Verification Failed*\n\nYou haven't joined all required channels.\n\nPlease join all channels and try again:\n\n"
            + "\n".join([f"• [Channel {i+1}]({ch['url']})" for i, ch in enumerate(REQUIRED_CHANNELS)]),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Try Again", callback_data="verify_channels")]])
        )

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Home button"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    stats = db.get_user_stats(user_id)
    
    home_text = (
        "🏠 *MENTAL CHEAT - HOME*\n\n"
        f"👤 *User:* {update.effective_user.first_name}\n"
        f"📊 *Referrals:* {stats.get('referrals_count', 0)}\n"
        f"💰 *Total Spent:* ₹{stats.get('total_spent', 0)}\n"
        f"🎫 *Active Keys:* {stats.get('active_keys', 0)}\n"
        f"📁 *Upload Limit:* {db.get_user_limit(user_id)} files\n\n"
        "📌 *Quick Links:*\n"
        "• /loaders - View all loaders\n"
        "• /purchase - Buy loaders\n"
        "• /referral - Get referral link\n"
        "• /support - Contact support\n"
        "• /upload - Upload your script\n\n"
        "⚡ Select an option from the menu below!"
    )
    
    reply_markup = create_main_menu_keyboard()
    await update.message.reply_text(home_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

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
            f"❌ *Upload Limit Reached*\n\nYou have reached your upload limit of {user_limit} files.\n\nTo upload more files, please:\n• Purchase a subscription\n• Become a reseller\n• Contact support\n\nSupport: {', '.join(SUPPORT_CONTACTS)}",
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
# LOADER HANDLERS
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
    """Handle duration selection callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("duration_", "").split("_")
    loader_name = data[0]
    duration = data[1]
    amount = int(data[2])
    
    context.user_data['selected_loader'] = loader_name
    context.user_data['selected_duration'] = duration
    context.user_data['selected_amount'] = amount
    
    message = f"💳 *Payment Required*\n\n📦 Loader: {loader_name}\n⏱ Duration: {duration}\n💰 Amount: ₹{amount}\n\nPlease complete payment to get your loader key."
    keyboard = create_payment_keyboard(loader_name, duration, amount)
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("pay_", "").split("_")
    loader_name = data[0]
    duration = data[1]
    amount = int(data[2])
    
    qr_buffer = generate_upi_qr(UPI_ID, amount, f"Payment for {loader_name} - {duration}")
    
    message = (
        f"💸 *Complete Payment*\n\n📦 Loader: {loader_name}\n⏱ Duration: {duration}\n💰 Amount: ₹{amount}\n\n"
        f"🏦 *UPI ID:* `{UPI_ID}`\n\nScan QR code or send payment to above UPI ID\n\n"
        "📸 *After payment:*\n1. Take screenshot of payment confirmation\n2. Click 'Upload Screenshot' button\n3. Send the screenshot\n4. Wait for verification\n\n⚠️ *Important:* Only UPI payments accepted"
    )
    
    keyboard = [[InlineKeyboardButton("📸 Upload Screenshot", callback_data=f"upload_screenshot_{loader_name}_{duration}_{amount}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['pending_payment'] = {'loader_name': loader_name, 'duration': duration, 'amount': amount}
    
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    await query.message.reply_photo(photo=qr_buffer, caption="🔍 *Scan this QR code to pay*", parse_mode=ParseMode.MARKDOWN)

async def upload_screenshot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upload screenshot callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("upload_screenshot_", "").split("_")
    loader_name = data[0]
    duration = data[1]
    amount = int(data[2])
    
    context.user_data['payment_info'] = {'loader_name': loader_name, 'duration': duration, 'amount': amount}
    
    await query.edit_message_text(
        f"📸 *Upload Payment Screenshot*\n\nPlease send a screenshot of the payment confirmation.\n\nThe screenshot should clearly show:\n• Transaction ID\n• Amount paid (₹{amount})\n• Payment status (Success/Completed)\n\nSend the screenshot as a photo message.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return AWAITING_PAYMENT_SCREENSHOT

async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment screenshot upload"""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = photo.file_id
    
    payment_info = context.user_data.get('payment_info')
    if not payment_info:
        await update.message.reply_text("❌ *Session Expired*\n\nPlease start the purchase process again.", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    
    db = DatabaseManager()
    purchase_id = db.add_purchase(user_id, payment_info['loader_name'], payment_info['duration'], payment_info['amount'], file_id)
    
    if purchase_id:
        for owner_id in OWNER_IDS:
            try:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"💳 *New Payment Pending*\n\n👤 User: {update.effective_user.first_name}\n🆔 ID: {user_id}\n📦 Loader: {payment_info['loader_name']}\n⏱ Duration: {payment_info['duration']}\n💰 Amount: ₹{payment_info['amount']}\n🆔 Purchase ID: {purchase_id}\n\nUse /pending to verify payments.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        try:
            await context.bot.send_photo(
                chat_id=PURCHASE_CHANNEL_ID,
                photo=file_id,
                caption=f"💳 *New Purchase*\n\n👤 User: {update.effective_user.first_name}\n📦 Loader: {payment_info['loader_name']}\n⏱ Duration: {payment_info['duration']}\n💰 Amount: ₹{payment_info['amount']}\n🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
        
        await update.message.reply_text(
            "✅ *Screenshot Received!*\n\nYour payment is now pending verification.\n\n📌 *Next Steps:*\n• Owners will verify your payment\n• You'll receive your loader key\n• This usually takes 5-30 minutes\n\n🔔 You'll be notified once verified.\n\nFor urgent support, contact:\n" + "\n".join(SUPPORT_CONTACTS),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_main_menu_keyboard()
        )
    else:
        await update.message.reply_text("❌ *Error Processing Payment*\n\nPlease try again or contact support.", parse_mode=ParseMode.MARKDOWN)
    
    return ConversationHandler.END

# ============================================
# OTHER USER HANDLERS
# ============================================

async def show_purchase_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Purchase Details button"""
    message = f"📸 *PURCHASE DETAILS CHANNEL*\n\nJoin our purchase details channel to see all transactions:\n\n🔗 [MENTAL PURCHASE DETAIL]({PURCHASE_CHANNEL})\n\nThis channel shows:\n• All purchase records\n• Payment confirmations\n• Transaction history\n\n⚠️ *Note:* You need to join to view purchase details"
    
    keyboard = [[InlineKeyboardButton("📱 Join Channel", url=PURCHASE_CHANNEL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=reply_markup)

async def show_setup_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Setup Video button"""
    message = f"🎥 *LOADER SETUP VIDEO*\n\nWatch this video to learn how to:\n• Download and install loaders\n• Activate your key\n• Configure settings\n• Troubleshoot common issues\n\n📹 [Watch Setup Video]({SETUP_VIDEO_LINK})\n\n⚠️ *Important:*\n• Follow steps exactly\n• Use VPN if needed\n• Disable Google Play Protect\n\nNeed help? Contact support."
    
    keyboard = [[InlineKeyboardButton("🎬 Watch Video", url=SETUP_VIDEO_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True, reply_markup=reply_markup)

async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Referral button"""
    user_id = update.effective_user.id
    
    db = DatabaseManager()
    referral_link = db.get_referral_link(user_id)
    stats = db.get_user_stats(user_id)
    
    message = (
        "👥 *REFERRAL PROGRAM*\n\nInvite friends and earn rewards!\n\n"
        f"🔗 *Your Referral Link:*\n`{referral_link}`\n\n"
        f"📊 *Your Stats:*\n┃ 👥 Referrals: {stats.get('referrals_count', 0)}\n\n"
        "🎁 *Rewards:*\n• 10 referrals → 1 Day Key\n• 30 referrals → 3 Days Key\n• 70 referrals → 7 Days Key\n\n"
        "💡 *How it works:*\n1. Share your referral link\n2. Friends join using your link\n3. Both get verified automatically\n4. Earn rewards at milestones\n\n⚠️ *Note:* Only new users count\nShare your link now!"
    )
    
    keyboard = [[InlineKeyboardButton("📤 Share Link", switch_inline_query=referral_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def show_free_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Free Trial button"""
    message = (
        "🎁 *FREE TRIAL OFFER*\n\nGet a taste of our premium loaders!\n\n"
        "✨ *Trial Details:*\n• Duration: 2 Hours\n• Features: Basic features only\n• Limited availability\n\n"
        "📋 *Requirements:*\n• Must be channel verified\n• New users only\n• One trial per user\n\n"
        "🔧 *How to get trial:*\n1. Contact support\n2. Request trial access\n3. Get temporary key\n\n"
        f"⚠️ *Note:* Trial keys are limited\n\nContact support for trial:\n" + "\n".join(SUPPORT_CONTACTS)
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
            f"📊 *Your Status:*\n┃ Type: {reseller_status['reseller_type']}\n┃ Status: Active ✅\n┃ Days Left: {days_left}\n"
            f"┃ Total Sales: {reseller_status['total_sales']}\n┃ Revenue: ₹{reseller_status['total_revenue']}\n\n"
            "🔧 *Reseller Tools:*\n• Generate keys\n• View sales\n• Withdraw earnings\n• Stock management\n\nUse /reseller for commands"
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
            "\n✨ *Benefits:*\n• 30% discount on all loaders\n• Generate unlimited keys\n• Dedicated support\n• Weekly commission\n• Marketing materials\n\n"
            "📌 *How to become reseller:*\n1. Select package\n2. Make payment\n3. Wait for admin approval\n\nSelect a package to proceed:"
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
        f"👑 *Reseller Package*\n\n📦 Package: {package}\n💰 Amount: ₹{price}\n\n"
        f"🏦 *UPI ID:* `{UPI_ID}`\n\nScan QR code or send payment to above UPI ID\n\n"
        "📸 *After payment:*\n1. Take screenshot\n2. Send screenshot\n3. Wait for approval\n\nSend payment screenshot to activate:"
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

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Support button"""
    message = (
        "❓ *SUPPORT CENTER*\n\nNeed help? Contact our support team:\n\n👨‍💼 *Support Team:*\n" + 
        "\n".join([f"• {contact}" for contact in SUPPORT_CONTACTS]) +
        "\n\n📌 *Common Issues:*\n• Loader not working\n• Key activation failed\n• Payment issues\n• Technical problems\n\n"
        "⚡ *Response Time:* 5-30 minutes\n\n💡 *Tips:*\n• Provide screenshots\n• Describe your issue clearly\n• Be patient\n\nClick below to contact support:"
    )
    
    keyboard = [[InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{SUPPORT_CONTACTS[0][1:]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# ============================================
# OWNER COMMANDS
# ============================================

@owner_only
async def pending_verifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending verifications (owner only)"""
    db = DatabaseManager()
    pending = db.get_pending_verifications()
    
    if not pending:
        await update.message.reply_text("✅ *No Pending Verifications*\n\nAll payments have been processed.", parse_mode=ParseMode.MARKDOWN)
        return
    
    for pend in pending[:10]:
        message = (
            f"💳 *Pending Verification #{pend['id']}*\n\n👤 User: {pend['first_name']}\n🆔 ID: {pend['user_id']}\n"
            f"📦 Loader: {pend['loader_name']}\n⏱ Duration: {pend['duration']}\n💰 Amount: ₹{pend['amount']}\n"
            f"🕐 Time: {pend['timestamp']}\n\nUse:\n/verify_payment {pend['id']} - to verify\n/reject_payment {pend['id']} - to reject"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Verify", callback_data=f"admin_verify_{pend['id']}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{pend['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if pend['screenshot_file_id']:
            try:
                await update.message.reply_photo(photo=pend['screenshot_file_id'], caption=message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            except:
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

@owner_only
async def verify_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify payment (owner only)"""
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/verify_payment [pending_id]`\n\nUse /pending to see pending IDs.", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        pending_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid pending ID!")
        return
    
    db = DatabaseManager()
    key_code = db.verify_payment(pending_id, update.effective_user.id)
    
    if key_code:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pending_verifications WHERE id = ?', (pending_id,))
        pending = cursor.fetchone()
        conn.close()
        
        if pending:
            try:
                message = (
                    f"✅ *Payment Verified!*\n\n📦 Loader: {pending['loader_name']}\n⏱ Duration: {pending['duration']}\n\n"
                    f"🔑 *Your Key:*\n`{key_code}`\n\n📌 *How to use:*\n1. Download loader from /loaders\n2. Open loader\n"
                    f"3. Enter this key\n4. Enjoy!\n\n⚠️ *Note:* Key expires in {pending['duration']}\n"
                    f"Support: {', '.join(SUPPORT_CONTACTS)}"
                )
                
                await context.bot.send_message(chat_id=pending['user_id'], text=message, parse_mode=ParseMode.MARKDOWN)
                await update.message.reply_text(f"✅ *Payment Verified!*\n\nKey sent to user {pending['user_id']}\nKey: `{key_code}`", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await update.message.reply_text(f"✅ *Payment Verified!*\n\nKey: `{key_code}`\nCould not send to user {pending['user_id']}: {e}", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ Failed to verify payment!")

@owner_only
async def reject_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject payment (owner only)"""
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/reject_payment [pending_id]`\n\nUse /pending to see pending IDs.", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        pending_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid pending ID!")
        return
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM pending_verifications WHERE id = ?', (pending_id,))
        pending = cursor.fetchone()
        
        if pending:
            cursor.execute('UPDATE pending_verifications SET status = "rejected" WHERE id = ?', (pending_id,))
            cursor.execute('UPDATE purchases SET status = "rejected" WHERE user_id = ? AND purchase_date = ?', (pending['user_id'], pending['timestamp']))
            conn.commit()
            
            try:
                await context.bot.send_message(
                    chat_id=pending['user_id'],
                    text="❌ *Payment Rejected*\n\nYour payment has been rejected.\n\nPossible reasons:\n• Wrong amount\n• Invalid screenshot\n• Payment not received\n\n" + f"Contact support: {', '.join(SUPPORT_CONTACTS)}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
            
            await update.message.reply_text(f"✅ *Payment Rejected!*\n\nUser {pending['user_id']} has been notified.")
        else:
            await update.message.reply_text("❌ Pending verification not found!")
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        await update.message.reply_text("❌ Failed to reject payment!")
    finally:
        conn.close()

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
            f"📁 *Pending File #{pend['id']}*\n\n👤 User: {pend['first_name']}\n🆔 ID: {pend['user_id']}\n"
            f"📄 File: {pend['file_name']}\n📂 Type: {pend['file_type']}\n🕐 Time: {pend['uploaded_time']}\n\n"
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
            f"👑 *Pending Reseller*\n\n👤 User: {pend['first_name']}\n🆔 ID: {pend['user_id']}\n"
            f"📦 Package: {pend['reseller_type']}\n💰 Amount: ₹{pend['amount_paid']}\n🕐 Time: {pend['purchase_date']}\n\n"
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
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics (owner only)"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total_users FROM users')
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute('SELECT COUNT(*) as verified_users FROM users WHERE is_verified = 1')
    verified_users = cursor.fetchone()['verified_users']
    
    cursor.execute('SELECT COUNT(*) as pending_payments FROM pending_verifications WHERE status = "pending"')
    pending_payments = cursor.fetchone()['pending_payments']
    
    cursor.execute('SELECT SUM(amount) as total_revenue FROM purchases WHERE status = "verified"')
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    
    cursor.execute('SELECT COUNT(*) as total_purchases FROM purchases WHERE status = "verified"')
    total_purchases = cursor.fetchone()['total_purchases']
    
    cursor.execute('SELECT COUNT(*) as active_resellers FROM resellers WHERE status = "active" AND expiry_date > ?', (datetime.now(),))
    active_resellers = cursor.fetchone()['active_resellers']
    
    cursor.execute('SELECT COUNT(*) as pending_files FROM file_approvals WHERE status = "pending"')
    pending_files = cursor.fetchone()['pending_files']
    
    cursor.execute('SELECT COUNT(*) as approved_files FROM file_approvals WHERE status = "approved"')
    approved_files = cursor.fetchone()['approved_files']
    
    cursor.execute('SELECT COUNT(*) as running_scripts FROM file_approvals WHERE status = "approved"')
    running_scripts = len([p for p in running_processes.values() if p.poll() is None])
    
    conn.close()
    
    message = (
        "📊 *BOT STATISTICS*\n\n"
        f"👥 *Users:*\n┃ Total: {total_users}\n┃ Verified: {verified_users}\n┃ Unverified: {total_users - verified_users}\n\n"
        f"💰 *Revenue:*\n┃ Total: ₹{total_revenue:,}\n┃ Purchases: {total_purchases}\n┃ Pending Payments: {pending_payments}\n\n"
        f"👑 *Resellers:*\n┃ Active: {active_resellers}\n\n"
        f"📁 *Files:*\n┃ Pending: {pending_files}\n┃ Approved: {approved_files}\n┃ Running: {running_scripts}\n\n"
        f"📈 *System:*\n┃ Database: SQLite3\n┃ Status: Online ✅\n┃ Uptime: Active\n\n"
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@owner_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast (owner only)"""
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/broadcast [message]`\n\nOr send a photo/video with caption as broadcast.", parse_mode=ParseMode.MARKDOWN)
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
            CallbackQueryHandler(upload_screenshot_callback, pattern="^upload_screenshot_"),
            MessageHandler(filters.TEXT & filters.Regex("^💰 Purchase$"), show_loaders),
            CallbackQueryHandler(reseller_callback, pattern="^reseller_"),
            MessageHandler(filters.TEXT & filters.Regex("^📤 Upload File$"), upload_file),
        ],
        states={
            AWAITING_PAYMENT_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_payment_screenshot),
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
    application.add_handler(CommandHandler("verify", send_verification_message))
    application.add_handler(CommandHandler("home", home))
    application.add_handler(CommandHandler("loaders", show_loaders))
    application.add_handler(CommandHandler("purchase", show_loaders))
    application.add_handler(CommandHandler("referral", show_referral))
    application.add_handler(CommandHandler("support", show_support))
    application.add_handler(CommandHandler("pending", pending_verifications))
    application.add_handler(CommandHandler("verify_payment", verify_payment_command))
    application.add_handler(CommandHandler("reject_payment", reject_payment_command))
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
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🎁 Free Trial$"), show_free_trial))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^👥 Referral$"), show_referral))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^💰 Purchase$"), show_loaders))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^👑 Reseller Panel$"), show_reseller_panel))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📤 Upload File$"), upload_file))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📁 My Scripts$"), my_scripts))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📢 Broadcast$"), broadcast_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^❓ Support$"), show_support))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📸 Purchase Details$"), show_purchase_details))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🎥 Setup Video$"), show_setup_video))
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, broadcast_with_media))
    application.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, broadcast_with_media))
    application.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, broadcast_with_media))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_channels$"))
    application.add_handler(CallbackQueryHandler(loader_callback, pattern="^loader_"))
    application.add_handler(CallbackQueryHandler(duration_callback, pattern="^duration_"))
    application.add_handler(CallbackQueryHandler(payment_callback, pattern="^pay_"))
    application.add_handler(CallbackQueryHandler(upload_screenshot_callback, pattern="^upload_screenshot_"))
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

# End of bot code - Total lines: 3540