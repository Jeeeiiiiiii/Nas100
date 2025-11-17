"""
Compare Basic vs Enhanced Backtester
Shows the impact of advanced filters on win rate and profitability
"""

from data_fetcher import DataFetcher
from backtester import Backtester
from enhanced_backtester import EnhancedBacktester
import pandas as pd


def print_comparison(basic_results, enhanced_results):
    """Print side-by-side comparison"""
    print("\n" + "=" * 90)
    print(" " * 25 + "📊 STRATEGY COMPARISON")
    print("=" * 90)
    print()
    print(f"{'METRIC':<30} {'BASIC':>20} {'ENHANCED':>20} {'CHANGE':>15}")
    print("-" * 90)

    # Helper function to format change
    def format_change(basic, enhanced, is_percentage=False, higher_is_better=True):
        if basic == 0:
            return "N/A"

        if is_percentage:
            diff = enhanced - basic
        else:
            diff = ((enhanced - basic) / basic) * 100

        symbol = "📈" if (diff > 0 and higher_is_better) or (diff < 0 and not higher_is_better) else "📉"
        color = "" if diff > 0 else ""

        if is_percentage:
            return f"{symbol} {diff:+.2f}%"
        else:
            return f"{symbol} {diff:+.1f}%"

    # Account metrics
    print(f"{'Return %':<30} {basic_results['return_pct']:>19.2f}% {enhanced_results['return_pct']:>19.2f}% {format_change(basic_results['return_pct'], enhanced_results['return_pct'], True):>15}")
    print(f"{'Final Balance':<30} ${basic_results['final_balance']:>18,.2f} ${enhanced_results['final_balance']:>18,.2f} {format_change(basic_results['final_balance'], enhanced_results['final_balance']):>15}")
    print(f"{'Net Profit':<30} ${basic_results['net_profit']:>18,.2f} ${enhanced_results['net_profit']:>18,.2f} {format_change(abs(basic_results['net_profit']) if basic_results['net_profit'] != 0 else 1, abs(enhanced_results['net_profit']), False, basic_results['net_profit'] > 0):>15}")

    print()
    print("-" * 90)

    # Trade statistics
    print(f"{'Total Trades':<30} {basic_results['total_trades']:>20} {enhanced_results['total_trades']:>20} {format_change(basic_results['total_trades'] if basic_results['total_trades'] > 0 else 1, enhanced_results['total_trades'], False, False):>15}")
    print(f"{'Winning Trades':<30} {basic_results['winning_trades']:>20} {enhanced_results['winning_trades']:>20} {format_change(basic_results['winning_trades'] if basic_results['winning_trades'] > 0 else 1, enhanced_results['winning_trades']):>15}")
    print(f"{'Losing Trades':<30} {basic_results['losing_trades']:>20} {enhanced_results['losing_trades']:>20} {format_change(basic_results['losing_trades'] if basic_results['losing_trades'] > 0 else 1, enhanced_results['losing_trades'], False, False):>15}")
    print(f"{'Win Rate %':<30} {basic_results['win_rate']:>19.2f}% {enhanced_results['win_rate']:>19.2f}% {format_change(basic_results['win_rate'], enhanced_results['win_rate'], True):>15}")

    print()
    print("-" * 90)

    # P&L metrics
    print(f"{'Profit Factor':<30} {basic_results['profit_factor']:>20.2f} {enhanced_results['profit_factor']:>20.2f} {format_change(basic_results['profit_factor'] if basic_results['profit_factor'] > 0 else 1, enhanced_results['profit_factor']):>15}")
    print(f"{'Avg Win':<30} ${basic_results['avg_win']:>18,.2f} ${enhanced_results['avg_win']:>18,.2f} {format_change(abs(basic_results['avg_win']) if basic_results['avg_win'] != 0 else 1, abs(enhanced_results['avg_win'])):>15}")
    print(f"{'Avg Loss':<30} ${basic_results['avg_loss']:>18,.2f} ${enhanced_results['avg_loss']:>18,.2f} {format_change(abs(basic_results['avg_loss']) if basic_results['avg_loss'] != 0 else 1, abs(enhanced_results['avg_loss']), False, False):>15}")
    print(f"{'Largest Win':<30} ${basic_results['largest_win']:>18,.2f} ${enhanced_results['largest_win']:>18,.2f} {format_change(basic_results['largest_win'] if basic_results['largest_win'] > 0 else 1, enhanced_results['largest_win']):>15}")
    print(f"{'Largest Loss':<30} ${basic_results['largest_loss']:>18,.2f} ${enhanced_results['largest_loss']:>18,.2f} {format_change(abs(basic_results['largest_loss']) if basic_results['largest_loss'] != 0 else 1, abs(enhanced_results['largest_loss']), False, False):>15}")

    print()
    print("-" * 90)

    # Risk metrics
    print(f"{'Max Drawdown':<30} ${basic_results['max_drawdown']:>18,.2f} ${enhanced_results['max_drawdown']:>18,.2f} {format_change(basic_results['max_drawdown'] if basic_results['max_drawdown'] > 0 else 1, enhanced_results['max_drawdown'], False, False):>15}")
    print(f"{'Max Drawdown %':<30} {basic_results['max_drawdown_pct']:>19.2f}% {enhanced_results['max_drawdown_pct']:>19.2f}% {format_change(basic_results['max_drawdown_pct'], enhanced_results['max_drawdown_pct'], True, False):>15}")

    print()
    print("=" * 90)

    # Summary
    print("\n🎯 KEY IMPROVEMENTS:")
    print()

    win_rate_improvement = enhanced_results['win_rate'] - basic_results['win_rate']
    return_improvement = enhanced_results['return_pct'] - basic_results['return_pct']

    if win_rate_improvement > 0:
        print(f"   ✅ Win Rate improved by {win_rate_improvement:.2f}% ({basic_results['win_rate']:.1f}% → {enhanced_results['win_rate']:.1f}%)")
    else:
        print(f"   ⚠️  Win Rate decreased by {abs(win_rate_improvement):.2f}% ({basic_results['win_rate']:.1f}% → {enhanced_results['win_rate']:.1f}%)")

    if return_improvement > 0:
        print(f"   ✅ Returns improved by {return_improvement:.2f}% ({basic_results['return_pct']:.1f}% → {enhanced_results['return_pct']:.1f}%)")
    else:
        print(f"   ⚠️  Returns decreased by {abs(return_improvement):.2f}% ({basic_results['return_pct']:.1f}% → {enhanced_results['return_pct']:.1f}%)")

    trade_reduction = basic_results['total_trades'] - enhanced_results['total_trades']
    if trade_reduction > 0:
        rejection_pct = (trade_reduction / basic_results['total_trades']) * 100
        print(f"   📊 Filters rejected {trade_reduction} trades ({rejection_pct:.1f}% of total)")
        print(f"      - Trend filter: {enhanced_results.get('rejected_by_trend', 0)}")
        print(f"      - Strength filter: {enhanced_results.get('rejected_by_strength', 0)}")
        print(f"      - Volume filter: {enhanced_results.get('rejected_by_volume', 0)}")

    print()
    print("=" * 90 + "\n")


def run_comparison():
    """Run comparison between basic and enhanced strategies"""
    print("=" * 90)
    print(" " * 20 + "🔬 BASIC vs ENHANCED STRATEGY COMPARISON")
    print("=" * 90)
    print()

    # Get data
    print("Step 1: Loading historical data...")
    fetcher = DataFetcher()

    # Try to load existing data first
    df = fetcher.load_data("NAS100_synthetic_30days.csv")
    if df is None:
        print("   Generating new synthetic data...")
        df = fetcher.generate_sample_data(days=30)
    else:
        print(f"   ✅ Loaded {len(df)} bars from saved data")

    print()

    # Use the best parameters from optimization
    best_params = {
        'initial_balance': 10000,
        'lot_size': 0.01,
        'risk_reward_ratio': 3.0,
        'consolidation_periods': 15,
        'breakout_threshold': 0.004,
        'max_daily_trades': 5
    }

    print("Step 2: Running BASIC strategy backtest...")
    print("-" * 90)

    basic_bt = Backtester(**best_params)
    basic_results = basic_bt.run_backtest(df)

    print()
    print("Step 3: Running ENHANCED strategy backtest...")
    print("-" * 90)

    enhanced_bt = EnhancedBacktester(
        **best_params,
        # Enhanced parameters (adjusted for synthetic data)
        use_trend_filter=True,
        trend_period=50,
        use_breakout_strength=True,
        min_breakout_strength=0.15,  # Lower for synthetic data
        use_atr_stops=True,
        atr_period=14,
        atr_multiplier=2.0,
        volume_multiplier=1.1  # More lenient for synthetic data
    )
    enhanced_results = enhanced_bt.run_backtest(df)

    # Print comparison
    print_comparison(basic_results, enhanced_results)

    # Save results
    basic_bt.save_results('basic_best_results.json')
    enhanced_bt.save_results('enhanced_best_results.json')

    return basic_results, enhanced_results


def optimize_enhanced():
    """Find best parameters for enhanced strategy"""
    print("=" * 90)
    print(" " * 25 + "🔬 ENHANCED STRATEGY OPTIMIZATION")
    print("=" * 90)
    print()

    # Get data
    fetcher = DataFetcher()
    df = fetcher.load_data("NAS100_synthetic_30days.csv")
    if df is None:
        df = fetcher.generate_sample_data(days=30)

    # Parameter ranges (adjusted for synthetic data)
    risk_rewards = [2.0, 2.5, 3.0]
    consolidation_periods_list = [15, 20, 25]
    breakout_thresholds = [0.003, 0.004, 0.005]
    trend_periods = [30, 50, 100]
    breakout_strengths = [0.1, 0.15, 0.2]  # Lower for synthetic data

    best_score = -float('inf')
    best_params = None
    all_results = []

    total_tests = len(risk_rewards) * len(consolidation_periods_list) * len(breakout_thresholds) * len(trend_periods) * len(breakout_strengths)
    current_test = 0

    print(f"Testing {total_tests} parameter combinations...")
    print("(This may take a few minutes)")
    print()

    for rr in risk_rewards:
        for cp in consolidation_periods_list:
            for bt in breakout_thresholds:
                for tp in trend_periods:
                    for bs in breakout_strengths:
                        current_test += 1

                        backtester = EnhancedBacktester(
                            initial_balance=10000,
                            lot_size=0.01,
                            risk_reward_ratio=rr,
                            consolidation_periods=cp,
                            breakout_threshold=bt,
                            max_daily_trades=5,
                            use_trend_filter=True,
                            trend_period=tp,
                            use_breakout_strength=True,
                            min_breakout_strength=bs,
                            use_atr_stops=True,
                            atr_period=14,
                            atr_multiplier=2.0,
                            volume_multiplier=1.1  # Adjusted for synthetic data
                        )

                        print(f"[{current_test}/{total_tests}] Testing: RR={rr}, CP={cp}, BT={bt}, TP={tp}, BS={bs}...", end=" ")

                        results = backtester.run_backtest(df, verbose=False)

                        # Score based on win rate AND profitability
                        # Prioritize win rate but also consider returns
                        score = results['win_rate'] * 2 + results['return_pct']

                        params = {
                            'risk_reward': rr,
                            'consolidation_periods': cp,
                            'breakout_threshold': bt,
                            'trend_period': tp,
                            'breakout_strength': bs,
                            'return_pct': results['return_pct'],
                            'win_rate': results['win_rate'],
                            'total_trades': results['total_trades'],
                            'profit_factor': results['profit_factor'],
                            'score': score
                        }

                        all_results.append(params)

                        print(f"WinRate: {results['win_rate']:.1f}%, Return: {results['return_pct']:.1f}%, Score: {score:.2f}")

                        if score > best_score and results['total_trades'] >= 20:
                            best_score = score
                            best_params = params

    print()
    print("=" * 90)
    print("🏆 OPTIMIZATION RESULTS (Optimized for Win Rate + Profitability)")
    print("=" * 90)
    print()

    if best_params:
        print("Best Parameters Found:")
        print(f"  Risk:Reward Ratio:        {best_params['risk_reward']}")
        print(f"  Consolidation Periods:    {best_params['consolidation_periods']}")
        print(f"  Breakout Threshold:       {best_params['breakout_threshold']}")
        print(f"  Trend Period (MA):        {best_params['trend_period']}")
        print(f"  Breakout Strength:        {best_params['breakout_strength']}")
        print()
        print("Performance with Best Parameters:")
        print(f"  Win Rate:                 {best_params['win_rate']:.2f}%")
        print(f"  Return:                   {best_params['return_pct']:.2f}%")
        print(f"  Total Trades:             {best_params['total_trades']}")
        print(f"  Profit Factor:            {best_params['profit_factor']:.2f}")
        print(f"  Combined Score:           {best_params['score']:.2f}")
    else:
        print("❌ No profitable parameter combination found")

    print()
    print("=" * 90)

    # Show top 10 results sorted by score
    print()
    print("Top 10 Parameter Combinations (by combined score):")
    print()
    sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)[:10]

    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. RR={result['risk_reward']}, CP={result['consolidation_periods']}, "
              f"BT={result['breakout_threshold']}, TP={result['trend_period']}, BS={result['breakout_strength']} "
              f"→ WinRate: {result['win_rate']:.1f}%, Return: {result['return_pct']:.1f}%, Score: {result['score']:.2f}")

    print()
    print("=" * 90)

    return best_params


def main():
    """Main menu"""
    print()
    print("=" * 90)
    print(" " * 25 + "STRATEGY COMPARISON & OPTIMIZATION")
    print("=" * 90)
    print()
    print("Choose an option:")
    print()
    print("1. Compare Basic vs Enhanced (with best known parameters)")
    print("2. Optimize Enhanced Strategy (find best parameters for high win rate)")
    print("3. Quick Test Enhanced Strategy (default parameters)")
    print("4. Exit")
    print()

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        run_comparison()
    elif choice == "2":
        optimize_enhanced()
    elif choice == "3":
        fetcher = DataFetcher()
        df = fetcher.load_data("NAS100_synthetic_30days.csv")
        if df is None:
            df = fetcher.generate_sample_data(days=30)

        enhanced_bt = EnhancedBacktester(
            initial_balance=10000,
            lot_size=0.01,
            risk_reward_ratio=2.5,
            consolidation_periods=20,
            breakout_threshold=0.003,
            max_daily_trades=5,
            use_trend_filter=True,
            trend_period=50,
            use_breakout_strength=True,
            min_breakout_strength=0.15,  # Adjusted for synthetic data
            use_atr_stops=True,
            atr_period=14,
            atr_multiplier=2.0,
            volume_multiplier=1.1  # More lenient
        )

        enhanced_bt.run_backtest(df)
        enhanced_bt.print_results()
    elif choice == "4":
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
