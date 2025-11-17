#!/usr/bin/env python3
"""
Test Ultra Strategy with OPTIMIZED Parameters
Based on fast optimization results: 52.94% win rate!
"""

from ultra_backtester import UltraBacktester
from data_fetcher import DataFetcher

def main():
    print("\n" + "=" * 110)
    print("                           🎯 TESTING OPTIMIZED ULTRA STRATEGY")
    print("=" * 110)
    print("\nThese parameters achieved 52.94% win rate in optimization!")
    print("Improvement: 44.19% → 52.94% (+8.75%)\n")

    # Load data
    fetcher = DataFetcher()
    df = fetcher.load_data('NAS100_synthetic_30days.csv')
    print(f"✅ Loaded {len(df)} bars\n")

    # OPTIMIZED PARAMETERS (from fast optimization)
    print("=" * 110)
    print("⚙️  OPTIMIZED PARAMETERS:")
    print("=" * 110)
    print("Core Settings:")
    print("  Risk:Reward Ratio:       2.0 (was variable)")
    print("  Consolidation Period:    20 (tighter consolidations)")
    print("  Breakout Threshold:      0.003 (0.3%)")
    print("\nEnhanced Filters:")
    print("  Trend Period (MA):       30 (faster trend detection)")
    print("  Min Breakout Strength:   0.20 (stronger breakouts only)")
    print("  Volume Multiplier:       1.1 (slight volume confirmation)")
    print("\nUltra Filters:")
    print("  RSI Range:               30-70 (avoid extremes)")
    print("  Min Touches:             2 (quality consolidations)")
    print("  Trading Hours:           02:00-20:00")
    print("  Confirmation Bars:       1")
    print("=" * 110 + "\n")

    # Create backtester with OPTIMIZED parameters
    backtester = UltraBacktester(
        initial_balance=10000,
        lot_size=0.01,
        # OPTIMIZED core parameters
        risk_reward_ratio=2.0,          # ← Changed from 2.0 variable
        consolidation_periods=20,       # ← Changed from 25/30
        breakout_threshold=0.003,       # ← Kept at 0.003
        # Enhanced filters - OPTIMIZED
        use_trend_filter=True,
        trend_period=30,                # ← Changed from 50 to 30
        use_breakout_strength=True,
        min_breakout_strength=0.20,     # ← Changed from 0.15 to 0.20
        use_atr_stops=True,
        volume_multiplier=1.1,          # ← Kept at 1.1
        # Ultra filters - OPTIMIZED
        use_rsi_filter=True,
        rsi_oversold=30,                # ← Changed from 25 to 30
        rsi_overbought=70,              # ← Changed from 75 to 70
        use_consolidation_quality=True,
        min_touches=2,                  # ← Changed from 3 to 2
        use_time_filter=True,
        trading_start_hour=2,
        trading_end_hour=20,
        use_false_breakout_filter=True,
        confirmation_bars=1,
        use_mtf_confirmation=True,
        use_trailing_stop=False
    )

    # Run backtest
    print("Running backtest with optimized parameters...\n")
    results = backtester.run_backtest(df, verbose=True)

    # Show comparison
    print("\n" + "=" * 110)
    print("                           📊 BEFORE vs AFTER OPTIMIZATION")
    print("=" * 110)
    print(f"{'Metric':<30} {'BEFORE':<20} {'AFTER':<20} {'Change':<20}")
    print("-" * 110)

    wr_after = f"{results['win_rate']:.2f}%"
    wr_change = f"+{results['win_rate']-44.19:.2f}%"
    pf_after = f"{results['profit_factor']:.2f}"
    pf_change = f"+{results['profit_factor']-1.60:.2f}"
    ret_after = f"{results['return_pct']:.2f}%"
    ret_change = f"+{results['return_pct']-5.86:.2f}%"
    trades_after = str(results['total_trades'])
    trades_change = f"{results['total_trades']-43:+d}"
    dd_after = f"{results['max_drawdown_pct']:.2f}%"
    dd_change = f"{results['max_drawdown_pct']-3.82:+.2f}%"

    print(f"{'Win Rate':<30} {'44.19%':<20} {wr_after:<20} {wr_change:<20}")
    print(f"{'Profit Factor':<30} {'1.60':<20} {pf_after:<20} {pf_change:<20}")
    print(f"{'Return %':<30} {'5.86%':<20} {ret_after:<20} {ret_change:<20}")
    print(f"{'Total Trades':<30} {'43':<20} {trades_after:<20} {trades_change:<20}")
    print(f"{'Max Drawdown %':<30} {'3.82%':<20} {dd_after:<20} {dd_change:<20}")
    print("=" * 110)

    if results['win_rate'] >= 50:
        print("\n🎉 SUCCESS! Achieved 50%+ win rate!")
        print("💡 These optimized parameters are ready for demo testing!")
    elif results['win_rate'] >= 45:
        print("\n⭐ GREAT! 45%+ win rate is very solid!")
        print("💡 Strategy is profitable and ready for testing!")
    else:
        print("\n🟡 IMPROVED but could be better.")
        print("💡 Consider running full optimization for even better results.")

    print("\n" + "=" * 110 + "\n")

if __name__ == "__main__":
    main()
