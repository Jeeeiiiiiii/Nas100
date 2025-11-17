"""
NAS100 Breakout Trading Bot
Based on the consolidation breakout strategy shown in the screenshots
Strategy: Identify consolidation zones, trade breakouts with defined TP/SL levels
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class NAS100BreakoutBot:
    def __init__(self, symbol="NAS100", timeframe=mt5.TIMEFRAME_M1, 
                 lot_size=0.01, risk_reward_ratio=2.0):
        """
        Initialize the NAS100 Breakout Trading Bot
        
        Parameters:
        - symbol: Trading instrument (default: NAS100)
        - timeframe: Chart timeframe (default: 1 minute)
        - lot_size: Position size
        - risk_reward_ratio: Risk to reward ratio for trades
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.lot_size = lot_size
        self.risk_reward_ratio = risk_reward_ratio
        self.consolidation_periods = 20  # Bars to identify consolidation
        self.breakout_threshold = 0.0015  # 0.15% breakout threshold
        self.in_position = False
        
    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            print("MT5 initialization failed")
            return False
        print("MT5 initialized successfully")
        return True
    
    def get_market_data(self, bars=100):
        """Fetch market data from MT5"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None:
            print(f"Failed to get rates for {self.symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def identify_consolidation(self, df):
        """
        Identify consolidation zones (similar to the boxes in the screenshots)
        Returns: (is_consolidating, high_level, low_level, box_range)
        """
        if len(df) < self.consolidation_periods:
            return False, None, None, None
        
        recent_data = df.tail(self.consolidation_periods)
        
        high_level = recent_data['high'].max()
        low_level = recent_data['low'].min()
        box_range = high_level - low_level
        
        # Calculate average range
        avg_range = (recent_data['high'] - recent_data['low']).mean()
        
        # Check if we're in consolidation (tight range)
        price_range_ratio = box_range / recent_data['close'].mean()
        
        # Consolidation criteria: range is relatively tight
        is_consolidating = price_range_ratio < self.breakout_threshold
        
        return is_consolidating, high_level, low_level, box_range
    
    def detect_breakout(self, df, high_level, low_level):
        """
        Detect breakout from consolidation zone
        Returns: 'BUY', 'SELL', or None
        """
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2]
        
        # Bullish breakout (like in image 3 - "TPPPP")
        if previous_price <= high_level and current_price > high_level:
            return 'BUY'
        
        # Bearish breakout
        if previous_price >= low_level and current_price < low_level:
            return 'SELL'
        
        return None
    
    def calculate_tp_sl(self, entry_price, signal_type, box_range):
        """
        Calculate Take Profit and Stop Loss levels
        Based on the box range and risk-reward ratio
        """
        # Stop Loss is typically the opposite side of the box
        # Take Profit is based on risk-reward ratio
        
        if signal_type == 'BUY':
            stop_loss = entry_price - box_range * 1.2  # SL below the box
            take_profit = entry_price + (box_range * 1.2 * self.risk_reward_ratio)
        else:  # SELL
            stop_loss = entry_price + box_range * 1.2  # SL above the box
            take_profit = entry_price - (box_range * 1.2 * self.risk_reward_ratio)
        
        return take_profit, stop_loss
    
    def place_order(self, signal_type, entry_price, take_profit, stop_loss):
        """
        Place order in MT5
        """
        point = mt5.symbol_info(self.symbol).point
        
        # Prepare the request
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
        
        # Send the order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.comment}")
            return False
        
        print(f"✅ {signal_type} order placed successfully!")
        print(f"Entry: {entry_price:.2f}")
        print(f"TP: {take_profit:.2f}")
        print(f"SL: {stop_loss:.2f}")
        self.in_position = True
        return True
    
    def check_open_positions(self):
        """Check if we have open positions"""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None or len(positions) == 0:
            self.in_position = False
            return False
        self.in_position = True
        return True
    
    def run(self, max_iterations=None):
        """
        Main trading loop
        """
        if not self.initialize_mt5():
            return
        
        print(f"🚀 Starting NAS100 Breakout Bot...")
        print(f"Symbol: {self.symbol}")
        print(f"Timeframe: {self.timeframe}")
        print(f"Lot Size: {self.lot_size}")
        print(f"Risk:Reward = 1:{self.risk_reward_ratio}")
        print("-" * 50)
        
        iteration = 0
        
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                
                # Check for open positions
                self.check_open_positions()
                
                # Skip if already in position
                if self.in_position:
                    print(f"⏳ Position already open. Waiting... ({datetime.now().strftime('%H:%M:%S')})")
                    time.sleep(10)
                    continue
                
                # Get market data
                df = self.get_market_data(bars=100)
                if df is None:
                    time.sleep(5)
                    continue
                
                # Identify consolidation
                is_consolidating, high_level, low_level, box_range = self.identify_consolidation(df)
                
                current_price = df['close'].iloc[-1]
                current_time = df['time'].iloc[-1]
                
                print(f"\n📊 {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Current Price: {current_price:.2f}")
                
                if is_consolidating:
                    print(f"📦 Consolidation detected!")
                    print(f"   High: {high_level:.2f}")
                    print(f"   Low: {low_level:.2f}")
                    print(f"   Range: {box_range:.2f}")
                    
                    # Check for breakout
                    signal = self.detect_breakout(df, high_level, low_level)
                    
                    if signal:
                        print(f"\n🔥 BREAKOUT DETECTED: {signal}")
                        
                        # Calculate TP and SL
                        take_profit, stop_loss = self.calculate_tp_sl(
                            current_price, signal, box_range
                        )
                        
                        # Place order
                        self.place_order(signal, current_price, take_profit, stop_loss)
                    else:
                        print("⏸️  Waiting for breakout...")
                else:
                    print("🔍 No consolidation pattern found")
                
                # Wait before next iteration
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Bot stopped by user")
        finally:
            mt5.shutdown()
            print("MT5 connection closed")


def main():
    """
    Main function to run the bot
    Configure your parameters here
    """
    
    # Configuration
    bot = NAS100BreakoutBot(
        symbol="NAS100",           # or "US100", "USTEC" depending on broker
        timeframe=mt5.TIMEFRAME_M1, # 1-minute chart (can change to M5, M15, etc.)
        lot_size=0.01,              # Start small!
        risk_reward_ratio=2.0       # 1:2 risk-reward
    )
    
    # Run the bot
    bot.run()


if __name__ == "__main__":
    main()
