"""
Enhanced NAS100 Breakout Trading Bot
With backtesting, notifications, and advanced risk management
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, Tuple
import json

# Try importing optional dependencies
try:
    import requests
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

class EnhancedNAS100Bot:
    def __init__(self, config):
        """Initialize bot with configuration"""
        self.config = config
        self.symbol = config.get('SYMBOL', 'NAS100')
        self.timeframe = self._get_timeframe(config.get('ACTIVE_TIMEFRAME', 1))
        self.lot_size = config.get('LOT_SIZE', 0.01)
        self.risk_reward_ratio = config.get('RISK_REWARD_RATIO', 2.0)
        self.consolidation_periods = config.get('CONSOLIDATION_PERIODS', 20)
        self.breakout_threshold = config.get('BREAKOUT_THRESHOLD', 0.0015)
        
        self.in_position = False
        self.daily_trades = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        
        # Setup logging
        self._setup_logging()
        
        # Trade history
        self.trade_history = []
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('LOG_LEVEL', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.get('LOG_FILE', 'bot.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_timeframe(self, minutes):
        """Convert minutes to MT5 timeframe"""
        timeframe_map = {
            1: mt5.TIMEFRAME_M1,
            5: mt5.TIMEFRAME_M5,
            15: mt5.TIMEFRAME_M15,
            30: mt5.TIMEFRAME_M30,
            60: mt5.TIMEFRAME_H1,
            240: mt5.TIMEFRAME_H4,
            1440: mt5.TIMEFRAME_D1
        }
        return timeframe_map.get(minutes, mt5.TIMEFRAME_M1)
    
    def initialize_mt5(self, login=None, password=None, server=None):
        """Initialize MT5 connection with credentials"""
        if not mt5.initialize():
            self.logger.error("MT5 initialization failed")
            return False
        
        # Login if credentials provided
        if login and password and server:
            authorized = mt5.login(login, password, server)
            if not authorized:
                self.logger.error(f"Failed to login to MT5: {mt5.last_error()}")
                mt5.shutdown()
                return False
            self.logger.info(f"Logged in to MT5 account {login}")
        
        self.logger.info("MT5 initialized successfully")
        return True
    
    def get_account_info(self):
        """Get account information"""
        account_info = mt5.account_info()
        if account_info is None:
            return None
        
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'profit': account_info.profit,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free
        }
    
    def calculate_dynamic_lot_size(self, stop_loss_points):
        """
        Calculate position size based on risk percentage
        Risk = Account Balance * Risk% / Stop Loss in Points
        """
        account_info = self.get_account_info()
        if not account_info:
            return self.lot_size
        
        balance = account_info['balance']
        risk_amount = balance * self.config.get('MAX_RISK_PER_TRADE', 0.02)
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return self.lot_size
        
        point_value = symbol_info.trade_contract_size * symbol_info.point
        lot_size = risk_amount / (stop_loss_points * point_value)
        
        # Round to valid lot size
        lot_step = symbol_info.volume_step
        lot_size = round(lot_size / lot_step) * lot_step
        
        # Ensure within limits
        lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        
        return lot_size
    
    def send_telegram_notification(self, message):
        """Send notification via Telegram"""
        if not self.config.get('ENABLE_TELEGRAM', False) or not TELEGRAM_AVAILABLE:
            return
        
        try:
            token = self.config.get('TELEGRAM_BOT_TOKEN')
            chat_id = self.config.get('TELEGRAM_CHAT_ID')
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": message}
            requests.post(url, data=data, timeout=5)
        except Exception as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")
    
    def is_trading_hours(self):
        """Check if current time is within trading hours"""
        now = datetime.utcnow()
        
        # Check day of week
        if now.weekday() not in self.config.get('TRADING_DAYS', [0, 1, 2, 3, 4]):
            return False
        
        # Check hours
        start_hour = self.config.get('TRADING_START_HOUR', 0)
        end_hour = self.config.get('TRADING_END_HOUR', 23)
        
        if now.hour < start_hour or now.hour > end_hour:
            return False
        
        return True
    
    def get_market_data(self, bars=100):
        """Fetch market data from MT5"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None:
            self.logger.error(f"Failed to get rates for {self.symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def identify_consolidation(self, df):
        """Identify consolidation zones"""
        if len(df) < self.consolidation_periods:
            return False, None, None, None
        
        recent_data = df.tail(self.consolidation_periods)
        
        high_level = recent_data['high'].max()
        low_level = recent_data['low'].min()
        box_range = high_level - low_level
        
        # Calculate if price is consolidating
        price_range_ratio = box_range / recent_data['close'].mean()
        is_consolidating = price_range_ratio < self.breakout_threshold
        
        return is_consolidating, high_level, low_level, box_range
    
    def detect_breakout(self, df, high_level, low_level):
        """Detect breakout from consolidation"""
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2]
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = df['tick_volume'].tail(20).mean()
        
        # Volume confirmation (optional but recommended)
        volume_confirmed = current_volume > avg_volume * 1.2
        
        # Bullish breakout
        if previous_price <= high_level and current_price > high_level:
            return 'BUY' if volume_confirmed else None
        
        # Bearish breakout
        if previous_price >= low_level and current_price < low_level:
            return 'SELL' if volume_confirmed else None
        
        return None
    
    def calculate_tp_sl(self, entry_price, signal_type, box_range):
        """Calculate TP and SL with proper formatting"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return None, None
        
        digits = symbol_info.digits
        sl_multiplier = self.config.get('SL_BOX_MULTIPLIER', 1.2)
        
        if signal_type == 'BUY':
            stop_loss = round(entry_price - (box_range * sl_multiplier), digits)
            risk = entry_price - stop_loss
            take_profit = round(entry_price + (risk * self.risk_reward_ratio), digits)
        else:
            stop_loss = round(entry_price + (box_range * sl_multiplier), digits)
            risk = stop_loss - entry_price
            take_profit = round(entry_price - (risk * self.risk_reward_ratio), digits)
        
        return take_profit, stop_loss
    
    def place_order(self, signal_type, entry_price, take_profit, stop_loss):
        """Place order with enhanced error handling"""
        # Check daily trade limit
        max_daily = self.config.get('MAX_DAILY_TRADES', 5)
        if self.daily_trades >= max_daily:
            self.logger.warning(f"Daily trade limit reached ({max_daily})")
            return False
        
        point = mt5.symbol_info(self.symbol).point
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": mt5.ORDER_TYPE_BUY if signal_type == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 234000,
            "comment": f"NAS100 Breakout {signal_type}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order failed: {result.comment}")
            return False
        
        # Log successful trade
        trade_info = {
            'timestamp': datetime.now(),
            'signal': signal_type,
            'entry': entry_price,
            'sl': stop_loss,
            'tp': take_profit,
            'lot_size': self.lot_size,
            'ticket': result.order
        }
        
        self.trade_history.append(trade_info)
        self.total_trades += 1
        self.daily_trades += 1
        self.in_position = True
        
        message = f"✅ {signal_type} Order Placed!\n"
        message += f"Entry: {entry_price:.2f}\n"
        message += f"TP: {take_profit:.2f}\n"
        message += f"SL: {stop_loss:.2f}\n"
        message += f"Lot Size: {self.lot_size}\n"
        message += f"Ticket: {result.order}"
        
        self.logger.info(message)
        self.send_telegram_notification(message)
        
        return True
    
    def check_open_positions(self):
        """Check and update position status"""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None or len(positions) == 0:
            self.in_position = False
            return False
        
        self.in_position = True
        return True
    
    def get_statistics(self):
        """Get trading statistics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        stats = {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'daily_trades': self.daily_trades
        }
        
        return stats
    
    def save_trade_history(self, filename='trade_history.json'):
        """Save trade history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.trade_history, f, default=str, indent=2)
            self.logger.info(f"Trade history saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save trade history: {e}")
    
    def run(self, max_iterations=None):
        """Main trading loop"""
        if not self.initialize_mt5():
            return
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 NAS100 Breakout Bot Started")
        self.logger.info(f"Symbol: {self.symbol}")
        self.logger.info(f"Timeframe: {self.timeframe}")
        self.logger.info(f"Lot Size: {self.lot_size}")
        self.logger.info(f"Risk:Reward = 1:{self.risk_reward_ratio}")
        self.logger.info("=" * 60)
        
        iteration = 0
        last_date = datetime.now().date()
        
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                
                # Reset daily counter
                current_date = datetime.now().date()
                if current_date != last_date:
                    self.daily_trades = 0
                    last_date = current_date
                    self.logger.info(f"📅 New trading day: {current_date}")
                
                # Check trading hours
                if not self.is_trading_hours():
                    self.logger.debug("Outside trading hours")
                    time.sleep(60)
                    continue
                
                # Check positions
                self.check_open_positions()
                
                if self.in_position:
                    self.logger.debug("Position already open")
                    time.sleep(self.config.get('CHECK_INTERVAL', 10))
                    continue
                
                # Get market data
                df = self.get_market_data(bars=100)
                if df is None:
                    time.sleep(5)
                    continue
                
                # Analyze market
                is_consolidating, high_level, low_level, box_range = self.identify_consolidation(df)
                
                current_price = df['close'].iloc[-1]
                current_time = df['time'].iloc[-1]
                
                if iteration % 6 == 0:  # Log every minute (if checking every 10 sec)
                    self.logger.info(f"Price: {current_price:.2f} | Consolidating: {is_consolidating}")
                
                if is_consolidating:
                    signal = self.detect_breakout(df, high_level, low_level)
                    
                    if signal:
                        self.logger.info(f"🔥 BREAKOUT DETECTED: {signal}")
                        
                        take_profit, stop_loss = self.calculate_tp_sl(
                            current_price, signal, box_range
                        )
                        
                        if take_profit and stop_loss:
                            self.place_order(signal, current_price, take_profit, stop_loss)
                
                time.sleep(self.config.get('CHECK_INTERVAL', 10))
                
        except KeyboardInterrupt:
            self.logger.info("\n⏹️  Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            # Save statistics
            stats = self.get_statistics()
            self.logger.info("\n" + "=" * 60)
            self.logger.info("📊 Final Statistics:")
            for key, value in stats.items():
                self.logger.info(f"{key}: {value}")
            self.logger.info("=" * 60)
            
            self.save_trade_history()
            mt5.shutdown()
            self.logger.info("MT5 connection closed")


def main():
    """Main entry point"""
    # Load configuration
    try:
        import config
        bot_config = {
            'SYMBOL': config.SYMBOL,
            'ACTIVE_TIMEFRAME': config.ACTIVE_TIMEFRAME,
            'LOT_SIZE': config.LOT_SIZE,
            'RISK_REWARD_RATIO': config.RISK_REWARD_RATIO,
            'CONSOLIDATION_PERIODS': config.CONSOLIDATION_PERIODS,
            'BREAKOUT_THRESHOLD': config.BREAKOUT_THRESHOLD,
            'MAX_RISK_PER_TRADE': config.MAX_RISK_PER_TRADE,
            'TRADING_START_HOUR': config.TRADING_START_HOUR,
            'TRADING_END_HOUR': config.TRADING_END_HOUR,
            'TRADING_DAYS': config.TRADING_DAYS,
            'CHECK_INTERVAL': config.CHECK_INTERVAL,
            'MAX_DAILY_TRADES': config.MAX_DAILY_TRADES,
            'ENABLE_TELEGRAM': config.ENABLE_TELEGRAM,
            'TELEGRAM_BOT_TOKEN': config.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': config.TELEGRAM_CHAT_ID,
            'LOG_LEVEL': config.LOG_LEVEL,
            'LOG_FILE': config.LOG_FILE,
        }
    except ImportError:
        print("Config file not found, using defaults")
        bot_config = {}
    
    # Create and run bot
    bot = EnhancedNAS100Bot(bot_config)
    bot.run()


if __name__ == "__main__":
    main()
