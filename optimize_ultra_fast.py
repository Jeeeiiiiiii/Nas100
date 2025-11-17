#!/usr/bin/env python3
"""
Ultra Strategy Fast Optimizer
Focuses on most impactful parameters for quick optimization
"""

import pandas as pd
from ultra_backtester import UltraBacktester
from data_fetcher import DataFetcher
import itertools

def load_data():
    """Load the synthetic data"""
    fetcher = DataFetcher()
    df = fetcher.load_data('NAS100_synthetic_30days.csv')
    print(f"✅ Loaded {len(df)} bars\n")
    return df

def optimize_ultra_fast(df):
    """
    Fast optimization focusing on key parameters
    """

    print("=" * 110)
    print("                           ⚡ ULTRA STRATEGY FAST OPTIMIZATION")
    print("=" * 110)
    print("\nTesting key parameter combinations for maximum win rate...")
    print("This will test ~300 combinations - takes about 5 minutes\n")

    # Focus on most impactful parameters based on prior knowledge
    # Core parameters - most impact on results
    risk_rewards = [2.0, 2.5, 3.0]
    consolidation_periods = [20, 25, 30]
    breakout_thresholds = [0.003, 0.004, 0.005]

    # Enhanced filters - keep best known values, test fewer options
    trend_periods = [30, 50]  # Trend is critical
    min_breakout_strengths = [0.15, 0.20]  # Strength filter is important
    volume_multipliers = [1.1]  # 1.1 works well, keep it

    # Ultra filters - test key ones
    rsi_ranges = [(25, 75), (30, 70)]  # RSI boundaries
    min_touches = [2, 3]  # Quality filter
    trading_hours = [(2, 20)]  # Keep 2-20 as default (works well)
    confirmation_bars = [1, 2]  # False breakout protection

    results = []
    total_tests = (len(risk_rewards) * len(consolidation_periods) * len(breakout_thresholds) *
                   len(trend_periods) * len(min_breakout_strengths) * len(volume_multipliers) *
                   len(rsi_ranges) * len(min_touches) * len(trading_hours) * len(confirmation_bars))

    print(f"📊 Total combinations to test: {total_tests}")
    print("-" * 110)

    test_num = 0
    best_winrate_so_far = 0

    for rr, cp, bt in itertools.product(risk_rewards, consolidation_periods, breakout_thresholds):
        for tp, bs in itertools.product(trend_periods, min_breakout_strengths):
            for vm in volume_multipliers:
                for rsi_range, mt in itertools.product(rsi_ranges, min_touches):
                    for th in trading_hours:
                        for cb in confirmation_bars:

                            test_num += 1

                            # Create backtester
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

                            # Only consider if we have at least 15 trades (lowered from 20 for stricter filters)
                            if result['total_trades'] >= 15:
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

                                # Track best so far
                                if result['win_rate'] > best_winrate_so_far:
                                    best_winrate_so_far = result['win_rate']
                                    print(f"🎯 New best! Test #{test_num}: {result['win_rate']:.2f}% WR | {result['total_trades']} trades | RR={rr} CP={cp} BT={bt} TP={tp} BS={bs}")

                            # Progress indicator every 50 tests
                            if test_num % 50 == 0:
                                print(f"⏳ Progress: {test_num}/{total_tests} tests ({test_num*100//total_tests}% complete) | Best WR so far: {best_winrate_so_far:.2f}%")

    print(f"\n✅ Optimization complete! Tested {test_num} combinations")
    print(f"📊 Found {len(results)} valid results (with 15+ trades)\n")

    if not results:
        print("❌ No valid results found. Try widening parameter ranges.")
        return

    # Sort by win rate, then profit factor
    results_sorted_by_winrate = sorted(results, key=lambda x: (x['win_rate'], x['profit_factor']), reverse=True)
    results_sorted_by_pf = sorted(results, key=lambda x: (x['profit_factor'], x['win_rate']), reverse=True)

    # Display top results
    print("=" * 110)
    print("                                  🏆 TOP 10 BY WIN RATE")
    print("=" * 110)
    print(f"{'#':<4} {'WR%':<8} {'Trades':<8} {'Return%':<10} {'PF':<8} {'DD%':<8} {'RR':<6} {'CP':<6} {'BT':<8} {'TP':<6} {'BS':<8} {'RSI':<10} {'Touch':<7} {'Conf':<5}")
    print("-" * 110)

    for i, r in enumerate(results_sorted_by_winrate[:10], 1):
        print(f"{i:<4} {r['win_rate']:<8.2f} {r['total_trades']:<8} {r['return_pct']:<10.2f} {r['profit_factor']:<8.2f} {r['max_drawdown_pct']:<8.2f} {r['rr']:<6} {r['cp']:<6} {r['bt']:<8} {r['tp']:<6} {r['bs']:<8} {str(r['rsi_range']):<10} {r['min_touches']:<7} {r['conf_bars']:<5}")

    print("\n" + "=" * 110)
    print("                                  💪 TOP 10 BY PROFIT FACTOR")
    print("=" * 110)
    print(f"{'#':<4} {'PF':<8} {'WR%':<8} {'Return%':<10} {'Trades':<8} {'DD%':<8} {'RR':<6} {'CP':<6} {'BT':<8} {'TP':<6} {'BS':<8}")
    print("-" * 110)

    for i, r in enumerate(results_sorted_by_pf[:10], 1):
        print(f"{i:<4} {r['profit_factor']:<8.2f} {r['win_rate']:<8.2f} {r['return_pct']:<10.2f} {r['total_trades']:<8} {r['max_drawdown_pct']:<8.2f} {r['rr']:<6} {r['cp']:<6} {r['bt']:<8} {r['tp']:<6} {r['bs']:<8}")

    # Best overall recommendation
    print("\n" + "=" * 110)
    print("                              ⭐ RECOMMENDED BEST SETTINGS")
    print("=" * 110)

    # Score: 50% win rate + 30% profit factor + 20% return
    for r in results:
        r['score'] = (r['win_rate'] * 0.5) + (r['profit_factor'] * 15) + (r['return_pct'] * 0.2)

    best = sorted(results, key=lambda x: x['score'], reverse=True)[0]

    print(f"\n🏆 Optimal Configuration (Balanced for win rate + profitability):")
    print(f"\n📊 Performance Metrics:")
    print(f"   Win Rate:        {best['win_rate']:.2f}% {'🎯' if best['win_rate'] >= 50 else '⭐' if best['win_rate'] >= 45 else ''}")
    print(f"   Total Trades:    {best['total_trades']}")
    print(f"   Return:          {best['return_pct']:.2f}%")
    print(f"   Profit Factor:   {best['profit_factor']:.2f}")
    print(f"   Max Drawdown:    {best['max_drawdown_pct']:.2f}%")
    print(f"   Avg Win:         ${best['avg_win']:.2f}")
    print(f"   Avg Loss:        ${best['avg_loss']:.2f}")
    print(f"   Win/Loss Ratio:  {abs(best['avg_win']/best['avg_loss']):.2f}x")

    print(f"\n⚙️  Parameters to use:")
    print(f"   Risk:Reward Ratio:      {best['rr']}")
    print(f"   Consolidation Period:   {best['cp']}")
    print(f"   Breakout Threshold:     {best['bt']}")
    print(f"   Trend Period (MA):      {best['tp']}")
    print(f"   Min Breakout Strength:  {best['bs']}")
    print(f"   Volume Multiplier:      {best['vm']}")
    print(f"   RSI Range:              {best['rsi_range'][0]}-{best['rsi_range'][1]}")
    print(f"   Min Consolidation Touches: {best['min_touches']}")
    print(f"   Trading Hours:          {best['trading_hours'][0]}:00-{best['trading_hours'][1]}:00")
    print(f"   Confirmation Bars:      {best['conf_bars']}")

    print("\n" + "=" * 110)

    # Save results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('score', ascending=False)
    results_df.to_csv('ultra_fast_optimization_results.csv', index=False)
    print(f"\n💾 Full results saved to: ultra_fast_optimization_results.csv")

    # Show improvement advice
    print("\n" + "=" * 110)
    print("💡 OPTIMIZATION INSIGHTS:")
    print("=" * 110)

    if best['win_rate'] >= 50:
        print("   ✅ EXCELLENT! 50%+ win rate achieved!")
        print("   💡 Strategy is demo-ready. Consider testing on real data next.")
    elif best['win_rate'] >= 45:
        print("   ⭐ VERY GOOD! 45%+ win rate is solid.")
        print("   💡 Strategy is profitable. You can proceed to demo testing.")
    else:
        print("   🟡 GOOD but could be better.")
        print("   💡 Consider:")
        print("      - Increasing min_breakout_strength for stronger signals")
        print("      - Tightening RSI range (e.g., 30-70 instead of 25-75)")
        print("      - Requiring more confirmation bars (2 instead of 1)")

    print("=" * 110 + "\n")

def main():
    print("\n" + "=" * 110)
    print("                           ⚡ ULTRA STRATEGY FAST OPTIMIZER")
    print("=" * 110)
    print("\nQuick optimization of the most impactful filter parameters!")
    print("Estimated time: 5-7 minutes\n")

    df = load_data()
    optimize_ultra_fast(df)

    print("✅ Fast optimization complete!")
    print("💡 Use the recommended settings for maximum win rate!\n")

if __name__ == "__main__":
    main()
