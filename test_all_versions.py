"""
Test All Three Versions: Basic → Enhanced → Ultra
Shows progressive improvement in win rate and performance
"""

from data_fetcher import DataFetcher
from backtester import Backtester
from enhanced_backtester import EnhancedBacktester
from ultra_backtester import UltraBacktester
import pandas as pd


def print_three_way_comparison(basic_results, enhanced_results, ultra_results):
    """Print three-way comparison"""
    print("\n" + "=" * 110)
    print(" " * 35 + "📊 THREE-WAY STRATEGY COMPARISON")
    print("=" * 110)
    print()
    print(f"{'METRIC':<30} {'BASIC':>20} {'ENHANCED':>20} {'ULTRA':>20} {'IMPROVEMENT':>15}")
    print("-" * 110)

    # Account metrics
    print(f"{'Return %':<30} {basic_results['return_pct']:>19.2f}% {enhanced_results['return_pct']:>19.2f}% {ultra_results['return_pct']:>19.2f}% {ultra_results['return_pct'] - basic_results['return_pct']:>+14.2f}%")
    print(f"{'Final Balance':<30} ${basic_results['final_balance']:>18,.2f} ${enhanced_results['final_balance']:>18,.2f} ${ultra_results['final_balance']:>18,.2f}")

    print()
    print("-" * 110)

    # Win Rate - MOST IMPORTANT
    wr_improvement = ultra_results['win_rate'] - basic_results['win_rate']
    wr_symbol = "🎯" if wr_improvement > 0 else ""
    print(f"{'Win Rate % 🎯':<30} {basic_results['win_rate']:>19.2f}% {enhanced_results['win_rate']:>19.2f}% {ultra_results['win_rate']:>19.2f}% {wr_improvement:>+14.2f}% {wr_symbol}")
    print(f"{'Total Trades':<30} {basic_results['total_trades']:>20} {enhanced_results['total_trades']:>20} {ultra_results['total_trades']:>20}")
    print(f"{'Winning Trades':<30} {basic_results['winning_trades']:>20} {enhanced_results['winning_trades']:>20} {ultra_results['winning_trades']:>20}")
    print(f"{'Losing Trades':<30} {basic_results['losing_trades']:>20} {enhanced_results['losing_trades']:>20} {ultra_results['losing_trades']:>20}")

    print()
    print("-" * 110)

    # Quality metrics
    print(f"{'Profit Factor':<30} {basic_results['profit_factor']:>20.2f} {enhanced_results['profit_factor']:>20.2f} {ultra_results['profit_factor']:>20.2f}")
    print(f"{'Avg Win':<30} ${basic_results['avg_win']:>18,.2f} ${enhanced_results['avg_win']:>18,.2f} ${ultra_results['avg_win']:>18,.2f}")
    print(f"{'Avg Loss':<30} ${basic_results['avg_loss']:>18,.2f} ${enhanced_results['avg_loss']:>18,.2f} ${ultra_results['avg_loss']:>18,.2f}")

    print()
    print("-" * 110)

    # Risk metrics
    print(f"{'Max Drawdown %':<30} {basic_results['max_drawdown_pct']:>19.2f}% {enhanced_results['max_drawdown_pct']:>19.2f}% {ultra_results['max_drawdown_pct']:>19.2f}%")

    print()
    print("=" * 110)

    # Filter breakdown
    print("\n📊 FILTER IMPACT ANALYSIS:")
    print()
    print(f"Enhanced Filters Rejected:")
    print(f"  Trend:     {enhanced_results.get('rejected_by_trend', 0):>6} trades")
    print(f"  Strength:  {enhanced_results.get('rejected_by_strength', 0):>6} trades")
    print(f"  Volume:    {enhanced_results.get('rejected_by_volume', 0):>6} trades")
    print()
    print(f"Ultra Filters Rejected (Additional):")
    print(f"  RSI:              {ultra_results.get('rejected_by_rsi', 0):>6} trades ✨")
    print(f"  Quality:          {ultra_results.get('rejected_by_quality', 0):>6} trades ✨")
    print(f"  Time:             {ultra_results.get('rejected_by_time', 0):>6} trades ✨")
    print(f"  False Breakout:   {ultra_results.get('rejected_by_false_breakout', 0):>6} trades ✨")
    print(f"  MTF Confirmation: {ultra_results.get('rejected_by_mtf', 0):>6} trades ✨")

    print()
    print("=" * 110)

    # Summary
    print("\n🎯 KEY IMPROVEMENTS (Basic → Ultra):")
    print()

    if wr_improvement > 0:
        print(f"   ✅ Win Rate improved by {wr_improvement:.2f}% ({basic_results['win_rate']:.1f}% → {ultra_results['win_rate']:.1f}%)")
    else:
        print(f"   ⚠️  Win Rate changed by {wr_improvement:.2f}%")

    pf_improvement = ultra_results['profit_factor'] - basic_results['profit_factor']
    if pf_improvement > 0:
        print(f"   ✅ Profit Factor improved by {pf_improvement:.2f} ({basic_results['profit_factor']:.2f} → {ultra_results['profit_factor']:.2f})")

    trade_reduction = basic_results['total_trades'] - ultra_results['total_trades']
    if trade_reduction > 0:
        reduction_pct = (trade_reduction / basic_results['total_trades']) * 100
        print(f"   📊 Ultra filters rejected {trade_reduction} trades ({reduction_pct:.1f}% of total)")
        print(f"      Result: Fewer but MUCH higher quality trades")

    print()
    print("=" * 110)

    # Final verdict
    print("\n🏆 FINAL VERDICT:")
    if ultra_results['win_rate'] >= 50:
        print("   🎉 OUTSTANDING! 50%+ win rate achieved!")
        print("   💡 This strategy is demo-ready!")
    elif ultra_results['win_rate'] >= 45:
        print("   🌟 EXCELLENT! 45%+ win rate achieved!")
        print("   💡 Consider testing on demo account next")
    elif ultra_results['win_rate'] >= 40:
        print("   ✅ GOOD! 40%+ win rate - significant improvement")
        print("   💡 Fine-tune parameters for even better results")
    else:
        print("   🟡 Profitable but needs more optimization")

    print("=" * 110 + "\n")


def run_all_three():
    """Run all three versions and compare"""
    print("=" * 110)
    print(" " * 30 + "🔬 TESTING ALL THREE VERSIONS")
    print("=" * 110)
    print()

    # Get data
    print("Loading historical data...")
    fetcher = DataFetcher()
    df = fetcher.load_data("NAS100_synthetic_30days.csv")
    if df is None:
        print("Generating new data...")
        df = fetcher.generate_sample_data(days=30)

    print(f"✅ Loaded {len(df)} bars\n")

    # Best parameters from optimization
    best_params = {
        'initial_balance': 10000,
        'lot_size': 0.01,
        'risk_reward_ratio': 2.0,  # From ultra optimization
        'consolidation_periods': 25,
        'breakout_threshold': 0.003,
        'max_daily_trades': 5
    }

    # Test 1: Basic
    print("=" * 110)
    print("TEST 1/3: BASIC STRATEGY")
    print("=" * 110)
    basic_bt = Backtester(**best_params)
    basic_results = basic_bt.run_backtest(df)  # Basic version doesn't have verbose parameter
    print(f"\n✅ Basic Complete: {basic_results['total_trades']} trades, {basic_results['win_rate']:.1f}% win rate")

    # Test 2: Enhanced
    print("\n" + "=" * 110)
    print("TEST 2/3: ENHANCED STRATEGY (Trend + Strength + ATR + Volume)")
    print("=" * 110)
    enhanced_bt = EnhancedBacktester(
        **best_params,
        use_trend_filter=True,
        trend_period=30,  # From ultra optimization
        use_breakout_strength=True,
        min_breakout_strength=0.2,  # From ultra optimization
        use_atr_stops=True,
        atr_period=14,
        atr_multiplier=2.0,
        volume_multiplier=1.1
    )
    enhanced_results = enhanced_bt.run_backtest(df, verbose=False)
    print(f"\n✅ Enhanced Complete: {enhanced_results['total_trades']} trades, {enhanced_results['win_rate']:.1f}% win rate")

    # Test 3: Ultra
    print("\n" + "=" * 110)
    print("TEST 3/3: ULTRA STRATEGY (All filters enabled)")
    print("=" * 110)
    ultra_bt = UltraBacktester(
        **best_params,
        # Enhanced filters
        use_trend_filter=True,
        trend_period=30,
        use_breakout_strength=True,
        min_breakout_strength=0.2,
        use_atr_stops=True,
        atr_period=14,
        atr_multiplier=2.0,
        volume_multiplier=1.1,
        # Ultra filters
        use_rsi_filter=True,
        rsi_period=14,
        rsi_overbought=70,
        rsi_oversold=30,
        use_consolidation_quality=True,
        min_touches=3,
        use_time_filter=True,
        trading_start_hour=2,
        trading_end_hour=20,
        use_trailing_stop=False,  # Can enable for testing
        use_false_breakout_filter=True,
        confirmation_bars=1,
        use_mtf_confirmation=True,
        higher_tf_period=200
    )
    ultra_results = ultra_bt.run_backtest(df, verbose=False)
    print(f"\n✅ Ultra Complete: {ultra_results['total_trades']} trades, {ultra_results['win_rate']:.1f}% win rate")

    # Print comparison
    print_three_way_comparison(basic_results, enhanced_results, ultra_results)

    # Save results
    basic_bt.save_results('basic_final_results.json')
    enhanced_bt.save_results('enhanced_final_results.json')
    ultra_bt.save_results('ultra_final_results.json')

    return basic_results, enhanced_results, ultra_results


def quick_ultra_test():
    """Quick test of ultra version only"""
    print("=" * 70)
    print("🚀 ULTRA-ENHANCED BACKTEST (Quick Test)")
    print("=" * 70)
    print()

    fetcher = DataFetcher()
    df = fetcher.load_data("NAS100_synthetic_30days.csv")
    if df is None:
        df = fetcher.generate_sample_data(days=30)

    ultra_bt = UltraBacktester(
        initial_balance=10000,
        lot_size=0.01,
        risk_reward_ratio=2.0,
        consolidation_periods=25,
        breakout_threshold=0.003,
        max_daily_trades=5,
        # All filters enabled with optimized settings
        use_trend_filter=True,
        trend_period=30,
        use_breakout_strength=True,
        min_breakout_strength=0.2,
        use_atr_stops=True,
        use_rsi_filter=True,
        rsi_overbought=70,
        rsi_oversold=30,
        use_consolidation_quality=True,
        min_touches=3,
        use_time_filter=True,
        use_false_breakout_filter=True,
        confirmation_bars=1,
        use_mtf_confirmation=True,
        higher_tf_period=200
    )

    results = ultra_bt.run_backtest(df)
    ultra_bt.print_results()
    ultra_bt.save_results('ultra_quick_test.json')

    return results


def main():
    """Main menu"""
    print()
    print("=" * 70)
    print(" " * 15 + "ULTRA-ENHANCED STRATEGY TESTING")
    print("=" * 70)
    print()
    print("Choose an option:")
    print()
    print("1. Test All 3 Versions (Basic → Enhanced → Ultra)")
    print("2. Quick Test Ultra Version Only")
    print("3. Exit")
    print()

    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        run_all_three()
    elif choice == "2":
        quick_ultra_test()
    elif choice == "3":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice")
        return

    print()
    again = input("Run another test? (y/n): ").strip().lower()
    if again == 'y':
        print()
        main()


if __name__ == "__main__":
    main()
