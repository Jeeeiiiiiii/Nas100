"""
Backtesting Engine for NAS100 Breakout Strategy
Simulates the strategy on historical data without needing MT5
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json


class Backtester:
    """Backtest the breakout strategy on historical data"""

    def __init__(self, initial_balance=10000, lot_size=0.01,
                 risk_reward_ratio=2.0, consolidation_periods=20,
                 breakout_threshold=0.0015, max_daily_trades=5):
        """
        Initialize backtester

        Parameters:
        - initial_balance: Starting account balance
        - lot_size: Position size in lots
        - risk_reward_ratio: TP is X times the SL
        - consolidation_periods: Bars to identify consolidation
        - breakout_threshold: Price range threshold for consolidation
        - max_daily_trades: Maximum trades per day
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.lot_size = lot_size
        self.risk_reward_ratio = risk_reward_ratio
        self.consolidation_periods = consolidation_periods
        self.breakout_threshold = breakout_threshold
        self.max_daily_trades = max_daily_trades

        # For NAS100, 1 lot = $1 per point (approximate)
        self.point_value = 1.0

        # Trading state
        self.in_position = False
        self.current_trade = None

        # Performance tracking
        self.trades = []
        self.equity_curve = []
        self.daily_trades_count = {}

    def identify_consolidation(self, df, current_idx):
        """
        Identify if market is in consolidation

        Returns: (is_consolidating, high_level, low_level, box_range)
        """
        # Need enough bars before current position
        if current_idx < self.consolidation_periods:
            return False, None, None, None

        # Get recent data up to current bar
        start_idx = current_idx - self.consolidation_periods
        recent_data = df.iloc[start_idx:current_idx]

        high_level = recent_data['high'].max()
        low_level = recent_data['low'].min()
        box_range = high_level - low_level

        # Calculate if consolidating
        avg_price = recent_data['close'].mean()
        price_range_ratio = box_range / avg_price

        is_consolidating = price_range_ratio < self.breakout_threshold

        return is_consolidating, high_level, low_level, box_range

    def detect_breakout(self, df, current_idx, high_level, low_level):
        """
        Detect breakout at current bar

        Returns: 'BUY', 'SELL', or None
        """
        if current_idx < 1:
            return None

        current_bar = df.iloc[current_idx]
        previous_bar = df.iloc[current_idx - 1]

        current_price = current_bar['close']
        previous_price = previous_bar['close']

        # Optional: Volume confirmation (disabled for backtesting)
        # current_volume = current_bar['tick_volume']
        # avg_volume = df.iloc[max(0, current_idx-20):current_idx]['tick_volume'].mean()
        # volume_confirmed = current_volume > avg_volume * 1.2
        volume_confirmed = True  # Always confirmed for backtesting

        # Bullish breakout
        if previous_price <= high_level and current_price > high_level:
            return 'BUY' if volume_confirmed else None

        # Bearish breakout
        if previous_price >= low_level and current_price < low_level:
            return 'SELL' if volume_confirmed else None

        return None

    def calculate_tp_sl(self, entry_price, signal_type, box_range):
        """Calculate Take Profit and Stop Loss"""
        sl_multiplier = 1.2

        if signal_type == 'BUY':
            stop_loss = entry_price - (box_range * sl_multiplier)
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * self.risk_reward_ratio)
        else:  # SELL
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
        """
        Check if current trade should be closed

        Returns: (should_close, exit_price, exit_reason)
        """
        if not self.in_position or self.current_trade is None:
            return False, None, None

        high = current_bar['high']
        low = current_bar['low']
        close = current_bar['close']

        tp = self.current_trade['take_profit']
        sl = self.current_trade['stop_loss']

        if self.current_trade['type'] == 'BUY':
            # Check if TP hit
            if high >= tp:
                return True, tp, 'TP'
            # Check if SL hit
            if low <= sl:
                return True, sl, 'SL'
        else:  # SELL
            # Check if TP hit
            if low <= tp:
                return True, tp, 'TP'
            # Check if SL hit
            if high >= sl:
                return True, sl, 'SL'

        return False, None, None

    def close_trade(self, exit_price, exit_time, exit_reason):
        """Close current trade and calculate P&L"""
        if not self.in_position:
            return

        trade = self.current_trade

        # Calculate profit/loss in points
        if trade['type'] == 'BUY':
            points = exit_price - trade['entry_price']
        else:  # SELL
            points = trade['entry_price'] - exit_price

        # Calculate P&L in dollars
        # For NAS100: 0.01 lot ≈ $0.01 per point, 0.1 lot ≈ $0.10 per point, etc.
        profit = points * self.lot_size * 100  # Approximation

        # Update balance
        self.balance += profit

        # Record trade
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

        # Reset position
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

    def run_backtest(self, df, start_idx=None, end_idx=None):
        """
        Run backtest on historical data

        Parameters:
        - df: DataFrame with OHLCV data
        - start_idx: Starting index (default: consolidation_periods)
        - end_idx: Ending index (default: len(df))

        Returns:
        - Dictionary with backtest results
        """
        print("=" * 70)
        print("🔬 STARTING BACKTEST")
        print("=" * 70)

        if start_idx is None:
            start_idx = self.consolidation_periods

        if end_idx is None:
            end_idx = len(df)

        total_bars = end_idx - start_idx
        print(f"Initial Balance: ${self.initial_balance:,.2f}")
        print(f"Lot Size: {self.lot_size}")
        print(f"Risk:Reward: 1:{self.risk_reward_ratio}")
        print(f"Backtesting {total_bars} bars from {df.iloc[start_idx]['time']} to {df.iloc[end_idx-1]['time']}")
        print("-" * 70)

        # Reset state
        self.balance = self.initial_balance
        self.in_position = False
        self.current_trade = None
        self.trades = []
        self.equity_curve = []
        self.daily_trades_count = {}

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

                    # Print trade result
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

            # Skip if already in position
            if self.in_position:
                continue

            # Skip if daily limit reached
            if not self.can_trade_today(current_time):
                continue

            # Look for new trade opportunities
            is_consolidating, high_level, low_level, box_range = self.identify_consolidation(df, i)

            if is_consolidating:
                signal = self.detect_breakout(df, i, high_level, low_level)

                if signal:
                    # Calculate TP and SL
                    tp, sl = self.calculate_tp_sl(current_price, signal, box_range)

                    # Open trade
                    self.open_trade(signal, current_price, current_time, tp, sl)
                    self.increment_daily_trades(current_time)

                    print(f"📍 {signal} | Entry: {current_price:.2f} | "
                          f"TP: {tp:.2f} | SL: {sl:.2f} | "
                          f"Box Range: {box_range:.2f}")

        # Close any remaining open trades
        if self.in_position:
            last_bar = df.iloc[end_idx - 1]
            self.close_trade(last_bar['close'], last_bar['time'], 'END_OF_DATA')

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
                'initial_balance': self.initial_balance
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
            'initial_balance': self.initial_balance
        }

        return results

    def print_results(self):
        """Print formatted backtest results"""
        results = self.get_results()

        print("\n" + "=" * 70)
        print("📊 BACKTEST RESULTS")
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

        print("\n" + "=" * 70)

        # Verdict
        print("\n🎯 VERDICT:")
        if results['total_trades'] < 30:
            print("   ⚠️  Not enough trades for reliable results (need 30+ trades)")
        elif results['win_rate'] >= 45 and results['profit_factor'] >= 1.5 and results['return_pct'] > 0:
            print("   ✅ STRATEGY LOOKS PROMISING!")
            print("   💡 Consider testing on demo account next")
        elif results['return_pct'] > 0:
            print("   🟡 STRATEGY IS PROFITABLE BUT NEEDS IMPROVEMENT")
            print("   💡 Try optimizing parameters or risk management")
        else:
            print("   ❌ STRATEGY NOT PROFITABLE ON THIS DATA")
            print("   💡 Need to revise strategy or parameters")

        print("=" * 70 + "\n")

    def save_results(self, filename='backtest_results.json'):
        """Save backtest results to file"""
        results = self.get_results()

        # Also save trade history
        results['trades'] = self.trades
        results['equity_curve'] = self.equity_curve

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Results saved to: {filename}")

    def export_trades_to_csv(self, filename='backtest_trades.csv'):
        """Export trade history to CSV"""
        if len(self.trades) == 0:
            print("No trades to export")
            return

        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filename, index=False)
        print(f"💾 Trades exported to: {filename}")
