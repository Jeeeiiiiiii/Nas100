"""
Configuration file for NAS100 Breakout Bot
Customize these settings based on your broker and preferences
"""

# ==================== BROKER SETTINGS ====================
# Your MT5 broker details
MT5_ACCOUNT = 12345678  # Your MT5 account number
MT5_PASSWORD = "your_password"  # Your MT5 password
MT5_SERVER = "YourBroker-Demo"  # Your broker server name

# ==================== TRADING SETTINGS ====================
# Symbol name (varies by broker)
# Common variations: "NAS100", "US100", "USTEC", "NASDAQ"
SYMBOL = "NAS100"

# Timeframe for analysis
# Options: mt5.TIMEFRAME_M1, M5, M15, M30, H1, H4, D1
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60

ACTIVE_TIMEFRAME = TIMEFRAME_M1  # Default: 1-minute

# Position sizing
LOT_SIZE = 0.01  # Start small! Increase gradually
MAX_POSITIONS = 1  # Maximum simultaneous positions

# Risk management
RISK_REWARD_RATIO = 2.0  # Take profit is 2x the stop loss
MAX_RISK_PER_TRADE = 0.02  # 2% of account per trade

# ==================== STRATEGY PARAMETERS ====================
# Consolidation detection
CONSOLIDATION_PERIODS = 20  # Number of bars to analyze
BREAKOUT_THRESHOLD = 0.0015  # 0.15% price range for consolidation

# Stop Loss and Take Profit multipliers
SL_BOX_MULTIPLIER = 1.2  # SL is 1.2x the box range
TP_MULTIPLIER = 2.0  # TP is 2x the risk

# ==================== OPERATIONAL SETTINGS ====================
# Trading hours (24-hour format, UTC)
TRADING_START_HOUR = 0  # Start trading at midnight UTC
TRADING_END_HOUR = 23  # End trading at 11 PM UTC

# Days to trade (0 = Monday, 6 = Sunday)
TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# Bot behavior
CHECK_INTERVAL = 10  # Seconds between market checks
MAX_DAILY_TRADES = 5  # Maximum trades per day

# ==================== NOTIFICATIONS ====================
ENABLE_TELEGRAM = False  # Enable Telegram notifications
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

ENABLE_EMAIL = False  # Enable email notifications
EMAIL_FROM = "your_email@gmail.com"
EMAIL_TO = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "nas100_bot.log"
LOG_TRADES = True  # Log all trades to CSV

# ==================== BACKTEST SETTINGS ====================
BACKTEST_START_DATE = "2024-01-01"
BACKTEST_END_DATE = "2024-12-31"
INITIAL_BALANCE = 10000  # Starting balance for backtest
