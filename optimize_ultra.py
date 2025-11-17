#!/usr/bin/env python3
"""
Ultra Strategy Optimizer
Finds the best parameter combination for all 10+ filters
"""

import pandas as pd
from ultra_backtester import UltraBacktester
from data_fetcher import DataFetcher
import itertools
from datetime import datetime

def load_data():
    """Load the synthetic data"""
    fetcher = DataFetcher()
    df = fetcher.load_data('NAS100_synthetic_30days.csv')
    print(f"✅ Loaded {len(df)} bars\n")
    return df

def optimize_ultra_strategy(df):
    """
    Optimize all ultra strategy parameters to maximize win rate
    while maintaining profitability
    """

    print("=" * 110)
    print("                           🔬 ULTRA STRATEGY OPTIMIZATION")
    print("=" * 110)
    print("\nTesting different parameter combinations to find the BEST settings...")
    print("This will test 100+ combinations - please wait...\n")

    # Parameter ranges to test
    # Core parameters
    risk_rewards = [2.0, 2.5, 3.0]
    consolidation_periods = [20, 25, 30]
    breakout_thresholds = [0.003, 0.004, 0.005]

    # Enhanced filter parameters
    trend_periods = [30, 50]
    min_breakout_strengths = [0.15, 0.20, 0.25]
    volume_multipliers = [1.1, 1.2]

    # Ultra filter parameters
    rsi_ranges = [(25, 75), (30, 70)]  # (oversold, overbought)
    min_touches = [2, 3]
    trading_hours = [(2, 20), (4, 18)]  # (start, end)
    confirmation_bars = [1, 2]

    results = []
    total_tests = (len(risk_rewards) * len(consolidation_periods) * len(breakout_thresholds) *
                   len(trend_periods) * len(min_breakout_strengths) * len(volume_multipliers) *
                   len(rsi_ranges) * len(min_touches) * len(trading_hours) * len(confirmation_bars))

    print(f"📊 Total combinations to test: {total_tests}")
    print("-" * 110)

    test_num = 0

    for rr, cp, bt in itertools.product(risk_rewards, consolidation_periods, breakout_thresholds):
        for tp, bs, vm in itertools.product(trend_periods, min_breakout_strengths, volume_multipliers):
            for rsi_range, mt, th, cb in itertools.product(rsi_ranges, min_touches, trading_hours, confirmation_bars):

                test_num += 1

                # Create backtester with these parameters
                backtester = UltraBacktester(
                    initial_balance=10000,
                    lot_size=0.01,
                    risk_reward_ratio=rr,
                    consolidation_periods=cp,
                    breakout_threshold=bt,
                    # Enhanced filters
                    use_trend_filter=True,
                    trend_period=tp,
                    use_breakout_strength=True,
                    min_breakout_strength=bs,
                    use_atr_stops=True,
                    volume_multiplier=vm,
                    # Ultra filters
                    use_rsi_filter=True,
                    rsi_oversold=rsi_range[0],
                    rsi_overbought=rsi_range[1],
                    use_consolidation_quality=True,
                    min_touches=mt,
                    use_time_filter=True,
                    trading_start_hour=th[0],
                    trading_end_hour=th[1],
                    use_false_breakout_filter=True,
                    confirmation_bars=cb,
                    use_mtf_confirmation=True,
                    use_trailing_stop=False
                )

                # Run backtest
                result = backtester.run_backtest(df, verbose=False)

                # Only consider if we have at least 20 trades
                if result['total_trades'] >= 20:
                    results.append({
                        'rr': rr,
                        'cp': cp,
                        'bt': bt,
                        'tp': tp,
                        'bs': bs,
                        'vm': vm,
                        'rsi_range': rsi_range,
                        'min_touches': mt,
                        'trading_hours': th,
                        'conf_bars': cb,
                        'total_trades': result['total_trades'],
                        'win_rate': result['win_rate'],
                        'return_pct': result['return_pct'],
                        'profit_factor': result['profit_factor'],
                        'max_drawdown_pct': result['max_drawdown_pct'],
                        'avg_win': result['avg_win'],
                        'avg_loss': result['avg_loss']
                    })

                # Progress indicator
                if test_num % 50 == 0:
                    print(f"⏳ Progress: {test_num}/{total_tests} tests completed...")

    print(f"\n✅ Optimization complete! Tested {test_num} combinations")
    print(f"📊 Found {len(results)} valid results (with 20+ trades)\n")

    if not results:
        print("❌ No valid results found. Try widening parameter ranges.")
        return

    # Sort by win rate, then profit factor, then return
    results_sorted_by_winrate = sorted(results, key=lambda x: (x['win_rate'], x['profit_factor'], x['return_pct']), reverse=True)
    results_sorted_by_return = sorted(results, key=lambda x: (x['return_pct'], x['win_rate']), reverse=True)
    results_sorted_by_pf = sorted(results, key=lambda x: (x['profit_factor'], x['win_rate']), reverse=True)

    # Display top results
    print("=" * 110)
    print("                                  🏆 TOP 5 BY WIN RATE")
    print("=" * 110)
    print(f"{'Rank':<6} {'WR%':<8} {'Trades':<8} {'Return%':<10} {'PF':<8} {'Parameters':<60}")
    print("-" * 110)

    for i, r in enumerate(results_sorted_by_winrate[:5], 1):
        params = f"RR={r['rr']}, CP={r['cp']}, BT={r['bt']}, TP={r['tp']}, BS={r['bs']}, VM={r['vm']}, RSI={r['rsi_range']}, Touch={r['min_touches']}, Hours={r['trading_hours']}, Conf={r['conf_bars']}"
        print(f"{i:<6} {r['win_rate']:<8.2f} {r['total_trades']:<8} {r['return_pct']:<10.2f} {r['profit_factor']:<8.2f} {params}")

    print("\n" + "=" * 110)
    print("                                🎯 TOP 5 BY PROFIT FACTOR")
    print("=" * 110)
    print(f"{'Rank':<6} {'PF':<8} {'WR%':<8} {'Return%':<10} {'Trades':<8} {'Parameters':<60}")
    print("-" * 110)

    for i, r in enumerate(results_sorted_by_pf[:5], 1):
        params = f"RR={r['rr']}, CP={r['cp']}, BT={r['bt']}, TP={r['tp']}, BS={r['bs']}, VM={r['vm']}, RSI={r['rsi_range']}, Touch={r['min_touches']}, Hours={r['trading_hours']}, Conf={r['conf_bars']}"
        print(f"{i:<6} {r['profit_factor']:<8.2f} {r['win_rate']:<8.2f} {r['return_pct']:<10.2f} {r['total_trades']:<8} {params}")

    print("\n" + "=" * 110)
    print("                                 💰 TOP 5 BY RETURN %")
    print("=" * 110)
    print(f"{'Rank':<6} {'Return%':<10} {'WR%':<8} {'PF':<8} {'Trades':<8} {'Parameters':<60}")
    print("-" * 110)

    for i, r in enumerate(results_sorted_by_return[:5], 1):
        params = f"RR={r['rr']}, CP={r['cp']}, BT={r['bt']}, TP={r['tp']}, BS={r['bs']}, VM={r['vm']}, RSI={r['rsi_range']}, Touch={r['min_touches']}, Hours={r['trading_hours']}, Conf={r['conf_bars']}"
        print(f"{i:<6} {r['return_pct']:<10.2f} {r['win_rate']:<8.2f} {r['profit_factor']:<8.2f} {r['total_trades']:<8} {params}")

    # Show the BEST overall (balanced approach)
    print("\n" + "=" * 110)
    print("                              ⭐ RECOMMENDED BEST OVERALL SETTINGS")
    print("=" * 110)

    # Score each result: 40% win rate + 30% profit factor + 30% return
    for r in results:
        r['score'] = (r['win_rate'] * 0.4) + (r['profit_factor'] * 15) + (r['return_pct'] * 0.3)

    best_overall = sorted(results, key=lambda x: x['score'], reverse=True)[0]

    print(f"\n🏆 Best Balanced Configuration:")
    print(f"   Win Rate:        {best_overall['win_rate']:.2f}%")
    print(f"   Total Trades:    {best_overall['total_trades']}")
    print(f"   Return:          {best_overall['return_pct']:.2f}%")
    print(f"   Profit Factor:   {best_overall['profit_factor']:.2f}")
    print(f"   Max Drawdown:    {best_overall['max_drawdown_pct']:.2f}%")
    print(f"   Avg Win:         ${best_overall['avg_win']:.2f}")
    print(f"   Avg Loss:        ${best_overall['avg_loss']:.2f}")
    print()
    print("📝 Parameters to use:")
    print(f"   Risk:Reward:           {best_overall['rr']}")
    print(f"   Consolidation Period:  {best_overall['cp']}")
    print(f"   Breakout Threshold:    {best_overall['bt']}")
    print(f"   Trend Period (MA):     {best_overall['tp']}")
    print(f"   Min Breakout Strength: {best_overall['bs']}")
    print(f"   Volume Multiplier:     {best_overall['vm']}")
    print(f"   RSI Range:             {best_overall['rsi_range'][0]}-{best_overall['rsi_range'][1]}")
    print(f"   Min Touches:           {best_overall['min_touches']}")
    print(f"   Trading Hours:         {best_overall['trading_hours'][0]}:00-{best_overall['trading_hours'][1]}:00")
    print(f"   Confirmation Bars:     {best_overall['conf_bars']}")
    print()
    print("=" * 110)

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('score', ascending=False)
    results_df.to_csv('ultra_optimization_results.csv', index=False)
    print(f"\n💾 Full results saved to: ultra_optimization_results.csv")
    print()

def main():
    print("\n" + "=" * 110)
    print("                           🚀 ULTRA STRATEGY PARAMETER OPTIMIZER")
    print("=" * 110)
    print("\nThis will find the OPTIMAL combination of all filter parameters!")
    print("Target: Maximize win rate while maintaining profitability\n")

    # Load data
    df = load_data()

    # Run optimization
    optimize_ultra_strategy(df)

    print("\n✅ Optimization complete!")
    print("\n💡 Tip: Use the recommended settings in your ultra backtester for best results!")
    print()

if __name__ == "__main__":
    main()
