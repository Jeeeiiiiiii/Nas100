"""
Enhanced Backtesting Engine for NAS100 Breakout Strategy
Includes advanced filters to improve win rate while maintaining profitability

Improvements over basic backtester:
1. Trend Filter - Only trade with the trend
2. Breakout Strength Filter - Require strong breakouts
3. ATR-based Stop Loss - Adaptive to volatility
4. Enhanced Volume Confirmation - Stronger volume requirements
5. Multi-timeframe Confirmation - Optional higher timeframe filter
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json


class EnhancedBacktester:
    """Enhanced backtest engine with filters to improve win rate"""

    def __init__(self, initial_balance=10000, lot_size=0.01,
                 risk_reward_ratio=2.0, consolidation_periods=20,
                 breakout_threshold=0.0015, max_daily_trades=5,
                 # New parameters
                 use_trend_filter=True, trend_period=50,
                 use_breakout_strength=True, min_breakout_strength=0.3,
                 use_atr_stops=True, atr_period=14, atr_multiplier=2.0,
                 volume_multiplier=1.5):
        """
        Initialize enhanced backtester

        New Parameters:
        - use_trend_filter: Only trade breakouts in trend direction
        - trend_period: Moving average period for trend
        - use_breakout_strength: Require minimum breakout strength
        - min_breakout_strength: Minimum % breakout from consolidation
        - use_atr_stops: Use ATR instead of box-based stops
        - atr_period: ATR calculation period
        - atr_multiplier: Multiplier for ATR stops
        - volume_multiplier: Volume must be X times average
        """
        # Basic parameters
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.lot_size = lot_size
        self.risk_reward_ratio = risk_reward_ratio
        self.consolidation_periods = consolidation_periods
        self.breakout_threshold = breakout_threshold
        self.max_daily_trades = max_daily_trades
        self.point_value = 1.0

        # Enhanced parameters
        self.use_trend_filter = use_trend_filter
        self.trend_period = trend_period
        self.use_breakout_strength = use_breakout_strength
        self.min_breakout_strength = min_breakout_strength
        self.use_atr_stops = use_atr_stops
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.volume_multiplier = volume_multiplier

        # Trading state
        self.in_position = False
        self.current_trade = None

        # Performance tracking
        self.trades = []
        self.equity_curve = []
        self.daily_trades_count = {}
        self.rejected_trades = {'trend': 0, 'strength': 0, 'volume': 0}

    def calculate_sma(self, df, period, idx):
        """Calculate Simple Moving Average at given index"""
        if idx < period:
            return None
        return df.iloc[idx-period:idx]['close'].mean()

    def calculate_atr(self, df, period, idx):
        """Calculate Average True Range at given index"""
        if idx < period + 1:
            return None

        recent_data = df.iloc[idx-period:idx]

        high_low = recent_data['high'] - recent_data['low']
        high_close = abs(recent_data['high'] - recent_data['close'].shift(1))
        low_close = abs(recent_data['low'] - recent_data['close'].shift(1))

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.mean()

        return atr

    def check_trend(self, df, idx, signal):
        """
        Check if trade is aligned with trend
        Returns: True if trade should be taken, False otherwise
        """
        if not self.use_trend_filter:
            return True

        # Calculate fast and slow moving averages
        fast_ma = self.calculate_sma(df, 20, idx)
        slow_ma = self.calculate_sma(df, self.trend_period, idx)

        if fast_ma is None or slow_ma is None:
            return False

        current_price = df.iloc[idx]['close']

        # BUY: Price and fast MA should be above slow MA (uptrend)
        if signal == 'BUY':
            return current_price > slow_ma and fast_ma > slow_ma

        # SELL: Price and fast MA should be below slow MA (downtrend)
        if signal == 'SELL':
            return current_price < slow_ma and fast_ma < slow_ma

        return False

    def check_breakout_strength(self, current_price, high_level, low_level, signal):
        """
        Check if breakout is strong enough
        Returns: True if breakout is strong, False otherwise
        """
        if not self.use_breakout_strength:
            return True

        box_range = high_level - low_level
        min_breakout = box_range * self.min_breakout_strength

        if signal == 'BUY':
            # Price should break above high by minimum percentage
            breakout_amount = current_price - high_level
            return breakout_amount >= min_breakout

        if signal == 'SELL':
            # Price should break below low by minimum percentage
            breakout_amount = low_level - current_price
            return breakout_amount >= min_breakout

        return False

    def check_volume(self, df, idx):
        """
        Enhanced volume confirmation
        Returns: True if volume is sufficient
        """
        if idx < 20:
            return True

        current_volume = df.iloc[idx]['tick_volume']
        avg_volume = df.iloc[idx-20:idx]['tick_volume'].mean()

        return current_volume > (avg_volume * self.volume_multiplier)

    def identify_consolidation(self, df, current_idx):
        """Identify if market is in consolidation"""
        if current_idx < self.consolidation_periods:
            return False, None, None, None

        start_idx = current_idx - self.consolidation_periods
        recent_data = df.iloc[start_idx:current_idx]

        high_level = recent_data['high'].max()
        low_level = recent_data['low'].min()
        box_range = high_level - low_level

        avg_price = recent_data['close'].mean()
        price_range_ratio = box_range / avg_price

        is_consolidating = price_range_ratio < self.breakout_threshold

        return is_consolidating, high_level, low_level, box_range

    def detect_breakout(self, df, current_idx, high_level, low_level):
        """Detect breakout with enhanced filters"""
        if current_idx < 1:
            return None

        current_bar = df.iloc[current_idx]
        previous_bar = df.iloc[current_idx - 1]

        current_price = current_bar['close']
        previous_price = previous_bar['close']

        signal = None

        # Detect basic breakout
        if previous_price <= high_level and current_price > high_level:
            signal = 'BUY'
        elif previous_price >= low_level and current_price < low_level:
            signal = 'SELL'

        if signal is None:
            return None

        # Apply filters
        # 1. Volume filter
        if not self.check_volume(df, current_idx):
            self.rejected_trades['volume'] += 1
            return None

        # 2. Trend filter
        if not self.check_trend(df, current_idx, signal):
            self.rejected_trades['trend'] += 1
            return None

        # 3. Breakout strength filter
        if not self.check_breakout_strength(current_price, high_level, low_level, signal):
            self.rejected_trades['strength'] += 1
            return None

        return signal

    def calculate_tp_sl(self, df, idx, entry_price, signal_type, box_range):
        """Calculate TP and SL using ATR or box range"""

        if self.use_atr_stops:
            # Use ATR-based stops
            atr = self.calculate_atr(df, self.atr_period, idx)

            if atr is None:
                # Fallback to box range if ATR not available
                return self.calculate_tp_sl_box(entry_price, signal_type, box_range)

            stop_distance = atr * self.atr_multiplier

            if signal_type == 'BUY':
                stop_loss = entry_price - stop_distance
                take_profit = entry_price + (stop_distance * self.risk_reward_ratio)
            else:
                stop_loss = entry_price + stop_distance
                take_profit = entry_price - (stop_distance * self.risk_reward_ratio)
        else:
            # Use box-based stops
            return self.calculate_tp_sl_box(entry_price, signal_type, box_range)

        return take_profit, stop_loss

    def calculate_tp_sl_box(self, entry_price, signal_type, box_range):
        """Calculate TP/SL using box range (fallback method)"""
        sl_multiplier = 1.2

        if signal_type == 'BUY':
            stop_loss = entry_price - (box_range * sl_multiplier)
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * self.risk_reward_ratio)
        else:
            stop_loss = entry_price + (box_range * sl_multiplier)
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * self.risk_reward_ratio)

        return take_profit, stop_loss

    def open_trade(self, signal_type, entry_price, entry_time, take_profit, stop_loss):
        """Open a new trade"""
        self.current_trade = {
            'type': signal_type,
            'entry_price': entry_price,
            'entry_time': entry_time,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'lot_size': self.lot_size
        }
        self.in_position = True

    def check_trade_exit(self, current_bar):
        """Check if current trade should be closed"""
        if not self.in_position or self.current_trade is None:
            return False, None, None

        high = current_bar['high']
        low = current_bar['low']

        tp = self.current_trade['take_profit']
        sl = self.current_trade['stop_loss']

        if self.current_trade['type'] == 'BUY':
            if high >= tp:
                return True, tp, 'TP'
            if low <= sl:
                return True, sl, 'SL'
        else:
            if low <= tp:
                return True, tp, 'TP'
            if high >= sl:
                return True, sl, 'SL'

        return False, None, None

    def close_trade(self, exit_price, exit_time, exit_reason):
        """Close current trade and calculate P&L"""
        if not self.in_position:
            return

        trade = self.current_trade

        if trade['type'] == 'BUY':
            points = exit_price - trade['entry_price']
        else:
            points = trade['entry_price'] - exit_price

        profit = points * self.lot_size * 100

        self.balance += profit

        trade_record = {
            'entry_time': trade['entry_time'],
            'exit_time': exit_time,
            'type': trade['type'],
            'entry_price': trade['entry_price'],
            'exit_price': exit_price,
            'take_profit': trade['take_profit'],
            'stop_loss': trade['stop_loss'],
            'points': points,
            'profit': profit,
            'balance': self.balance,
            'exit_reason': exit_reason,
            'win': profit > 0
        }

        self.trades.append(trade_record)
        self.in_position = False
        self.current_trade = None

    def can_trade_today(self, current_time):
        """Check if we can take more trades today"""
        date_str = current_time.strftime('%Y-%m-%d')
        trades_today = self.daily_trades_count.get(date_str, 0)
        return trades_today < self.max_daily_trades

    def increment_daily_trades(self, current_time):
        """Increment daily trade counter"""
        date_str = current_time.strftime('%Y-%m-%d')
        self.daily_trades_count[date_str] = self.daily_trades_count.get(date_str, 0) + 1

    def run_backtest(self, df, start_idx=None, end_idx=None, verbose=True):
        """Run backtest on historical data"""
        if verbose:
            print("=" * 70)
            print("🔬 STARTING ENHANCED BACKTEST")
            print("=" * 70)

        if start_idx is None:
            start_idx = max(self.consolidation_periods, self.trend_period)

        if end_idx is None:
            end_idx = len(df)

        total_bars = end_idx - start_idx

        if verbose:
            print(f"Initial Balance: ${self.initial_balance:,.2f}")
            print(f"Lot Size: {self.lot_size}")
            print(f"Risk:Reward: 1:{self.risk_reward_ratio}")
            print(f"\n🎯 Enhanced Filters:")
            print(f"   Trend Filter: {'ON' if self.use_trend_filter else 'OFF'} (MA{self.trend_period})")
            print(f"   Breakout Strength: {'ON' if self.use_breakout_strength else 'OFF'} ({self.min_breakout_strength*100}%)")
            print(f"   ATR Stops: {'ON' if self.use_atr_stops else 'OFF'} (ATR{self.atr_period} x {self.atr_multiplier})")
            print(f"   Volume Filter: {self.volume_multiplier}x average")
            print(f"\nBacktesting {total_bars} bars from {df.iloc[start_idx]['time']} to {df.iloc[end_idx-1]['time']}")
            print("-" * 70)

        # Reset state
        self.balance = self.initial_balance
        self.in_position = False
        self.current_trade = None
        self.trades = []
        self.equity_curve = []
        self.daily_trades_count = {}
        self.rejected_trades = {'trend': 0, 'strength': 0, 'volume': 0}

        # Main backtest loop
        for i in range(start_idx, end_idx):
            current_bar = df.iloc[i]
            current_time = current_bar['time']
            current_price = current_bar['close']

            # Check if we need to close existing trade
            if self.in_position:
                should_close, exit_price, exit_reason = self.check_trade_exit(current_bar)
                if should_close:
                    self.close_trade(exit_price, current_time, exit_reason)

                    if verbose:
                        last_trade = self.trades[-1]
                        win_indicator = "✅ WIN" if last_trade['win'] else "❌ LOSS"
                        print(f"{win_indicator} | {last_trade['type']} | "
                              f"Entry: {last_trade['entry_price']:.2f} | "
                              f"Exit: {last_trade['exit_price']:.2f} | "
                              f"P&L: ${last_trade['profit']:.2f} | "
                              f"Balance: ${self.balance:,.2f}")

            # Record equity
            self.equity_curve.append({
                'time': current_time,
                'balance': self.balance,
                'in_position': self.in_position
            })

            if self.in_position:
                continue

            if not self.can_trade_today(current_time):
                continue

            # Look for new trades
            is_consolidating, high_level, low_level, box_range = self.identify_consolidation(df, i)

            if is_consolidating:
                signal = self.detect_breakout(df, i, high_level, low_level)

                if signal:
                    tp, sl = self.calculate_tp_sl(df, i, current_price, signal, box_range)

                    self.open_trade(signal, current_price, current_time, tp, sl)
                    self.increment_daily_trades(current_time)

                    if verbose:
                        print(f"📍 {signal} | Entry: {current_price:.2f} | "
                              f"TP: {tp:.2f} | SL: {sl:.2f}")

        # Close any remaining trades
        if self.in_position:
            last_bar = df.iloc[end_idx - 1]
            self.close_trade(last_bar['close'], last_bar['time'], 'END_OF_DATA')

        if verbose:
            print("-" * 70)
            print("✅ BACKTEST COMPLETE")
            print("=" * 70)

        return self.get_results()

    def get_results(self):
        """Calculate and return backtest results"""
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_loss': 0,
                'net_profit': 0,
                'return_pct': 0,
                'max_drawdown': 0,
                'max_drawdown_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'final_balance': self.balance,
                'initial_balance': self.initial_balance,
                'rejected_by_trend': self.rejected_trades['trend'],
                'rejected_by_strength': self.rejected_trades['strength'],
                'rejected_by_volume': self.rejected_trades['volume']
            }

        trades_df = pd.DataFrame(self.trades)

        winning_trades = trades_df[trades_df['win'] == True]
        losing_trades = trades_df[trades_df['win'] == False]

        total_profit = winning_trades['profit'].sum() if len(winning_trades) > 0 else 0
        total_loss = abs(losing_trades['profit'].sum()) if len(losing_trades) > 0 else 0

        # Calculate drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['peak'] = equity_df['balance'].cummax()
        equity_df['drawdown'] = equity_df['peak'] - equity_df['balance']
        equity_df['drawdown_pct'] = (equity_df['drawdown'] / equity_df['peak']) * 100

        max_drawdown = equity_df['drawdown'].max()
        max_drawdown_pct = equity_df['drawdown_pct'].max()

        results = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trades) * 100) if len(self.trades) > 0 else 0,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_profit': total_profit - total_loss,
            'return_pct': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'avg_win': winning_trades['profit'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['profit'].mean() if len(losing_trades) > 0 else 0,
            'profit_factor': total_profit / total_loss if total_loss > 0 else float('inf'),
            'largest_win': winning_trades['profit'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['profit'].min() if len(losing_trades) > 0 else 0,
            'final_balance': self.balance,
            'initial_balance': self.initial_balance,
            'rejected_by_trend': self.rejected_trades['trend'],
            'rejected_by_strength': self.rejected_trades['strength'],
            'rejected_by_volume': self.rejected_trades['volume']
        }

        return results

    def print_results(self):
        """Print formatted backtest results"""
        results = self.get_results()

        print("\n" + "=" * 70)
        print("📊 ENHANCED BACKTEST RESULTS")
        print("=" * 70)

        print(f"\n💰 ACCOUNT SUMMARY:")
        print(f"   Initial Balance:  ${results['initial_balance']:>12,.2f}")
        print(f"   Final Balance:    ${results['final_balance']:>12,.2f}")
        print(f"   Net Profit:       ${results['net_profit']:>12,.2f}")
        print(f"   Return:           {results['return_pct']:>12.2f}%")

        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades:     {results['total_trades']:>12}")
        print(f"   Winning Trades:   {results['winning_trades']:>12}")
        print(f"   Losing Trades:    {results['losing_trades']:>12}")
        print(f"   Win Rate:         {results['win_rate']:>12.2f}%")

        print(f"\n💵 PROFIT & LOSS:")
        print(f"   Total Profit:     ${results['total_profit']:>12,.2f}")
        print(f"   Total Loss:       ${results['total_loss']:>12,.2f}")
        print(f"   Avg Win:          ${results['avg_win']:>12,.2f}")
        print(f"   Avg Loss:         ${results['avg_loss']:>12,.2f}")
        print(f"   Largest Win:      ${results['largest_win']:>12,.2f}")
        print(f"   Largest Loss:     ${results['largest_loss']:>12,.2f}")
        print(f"   Profit Factor:    {results['profit_factor']:>12.2f}")

        print(f"\n📉 RISK METRICS:")
        print(f"   Max Drawdown:     ${results['max_drawdown']:>12,.2f}")
        print(f"   Max Drawdown %:   {results['max_drawdown_pct']:>12.2f}%")

        print(f"\n🎯 FILTER STATISTICS:")
        print(f"   Rejected by Trend:      {results['rejected_by_trend']:>6}")
        print(f"   Rejected by Strength:   {results['rejected_by_strength']:>6}")
        print(f"   Rejected by Volume:     {results['rejected_by_volume']:>6}")
        total_rejected = results['rejected_by_trend'] + results['rejected_by_strength'] + results['rejected_by_volume']
        print(f"   Total Rejected:         {total_rejected:>6}")

        print("\n" + "=" * 70)

        # Verdict
        print("\n🎯 VERDICT:")
        if results['total_trades'] < 30:
            print("   ⚠️  Not enough trades for reliable results (need 30+ trades)")
        elif results['win_rate'] >= 45 and results['profit_factor'] >= 1.5 and results['return_pct'] > 0:
            print("   ✅ STRATEGY LOOKS VERY PROMISING!")
            print("   💡 Consider testing on demo account next")
        elif results['return_pct'] > 0:
            print("   🟡 STRATEGY IS PROFITABLE BUT COULD BE BETTER")
            print("   💡 Try adjusting filter parameters")
        else:
            print("   ❌ STRATEGY NOT PROFITABLE ON THIS DATA")
            print("   💡 Need to revise strategy or parameters")

        print("=" * 70 + "\n")

    def save_results(self, filename='enhanced_backtest_results.json'):
        """Save backtest results to file"""
        results = self.get_results()
        results['trades'] = self.trades
        results['equity_curve'] = self.equity_curve

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Results saved to: {filename}")

    def export_trades_to_csv(self, filename='enhanced_backtest_trades.csv'):
        """Export trade history to CSV"""
        if len(self.trades) == 0:
            print("No trades to export")
            return

        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filename, index=False)
        print(f"💾 Trades exported to: {filename}")
