"""
Simple script to run backtests
No MT5, no broker, no credentials needed!
"""

from data_fetcher import DataFetcher
from backtester import Backtester
import sys


def run_quick_backtest():
    """Run a quick backtest with synthetic data"""
    print("=" * 70)
    print("🚀 NAS100 BREAKOUT STRATEGY - QUICK BACKTEST")
    print("=" * 70)
    print()

    # Create data fetcher
    fetcher = DataFetcher()

    # Generate synthetic data for testing
    print("Step 1: Generating test data...")
    df = fetcher.generate_sample_data(days=30, interval_minutes=1)

    if df is None or df.empty:
        print("❌ Failed to generate data")
        return

    print()
    print("Step 2: Running backtest...")
    print()

    # Create backtester with default settings
    backtester = Backtester(
        initial_balance=10000,
        lot_size=0.01,
        risk_reward_ratio=2.0,
        consolidation_periods=20,
        breakout_threshold=0.003,  # 0.3% - more realistic for testing
        max_daily_trades=5
    )

    # Run backtest
    results = backtester.run_backtest(df)

    # Print results
    backtester.print_results()

    # Save results
    backtester.save_results('backtest_results.json')
    backtester.export_trades_to_csv('backtest_trades.csv')

    return results


def run_real_data_backtest():
    """Run backtest with real downloaded data"""
    print("=" * 70)
    print("🚀 NAS100 BREAKOUT STRATEGY - REAL DATA BACKTEST")
    print("=" * 70)
    print()

    # Create data fetcher
    fetcher = DataFetcher()

    print("Step 1: Downloading real market data...")
    print("(Note: Yahoo Finance limits 1-minute data to last 7 days)")
    print()

    # Download recent data
    df = fetcher.download_recent_data(days=7, interval="1m")

    if df is None or df.empty:
        print("❌ Failed to download data. Using synthetic data instead...")
        print()
        df = fetcher.generate_sample_data(days=30)

    if df is None or df.empty:
        print("❌ No data available")
        return

    print()
    print("Step 2: Running backtest...")
    print()

    # Create backtester
    backtester = Backtester(
        initial_balance=10000,
        lot_size=0.01,
        risk_reward_ratio=2.0,
        consolidation_periods=20,
        breakout_threshold=0.003,  # 0.3% - more realistic for testing
        max_daily_trades=5
    )

    # Run backtest
    results = backtester.run_backtest(df)

    # Print results
    backtester.print_results()

    # Save results
    backtester.save_results('backtest_results_real.json')
    backtester.export_trades_to_csv('backtest_trades_real.csv')

    return results


def run_custom_backtest():
    """Run backtest with custom parameters"""
    print("=" * 70)
    print("🚀 NAS100 BREAKOUT STRATEGY - CUSTOM BACKTEST")
    print("=" * 70)
    print()

    # Get user inputs
    print("Configure your backtest:")
    print()

    initial_balance = float(input("Initial balance [$10000]: ") or "10000")
    lot_size = float(input("Lot size [0.01]: ") or "0.01")
    risk_reward = float(input("Risk:Reward ratio [2.0]: ") or "2.0")
    consol_periods = int(input("Consolidation periods [20]: ") or "20")
    breakout_threshold = float(input("Breakout threshold [0.003]: ") or "0.003")
    max_daily_trades = int(input("Max daily trades [5]: ") or "5")

    print()
    data_choice = input("Use (1) Synthetic data or (2) Real data? [1]: ") or "1"

    # Get data
    fetcher = DataFetcher()

    if data_choice == "2":
        print("\nDownloading real data...")
        df = fetcher.download_recent_data(days=7, interval="1m")
        if df is None or df.empty:
            print("Failed to download. Using synthetic data...")
            df = fetcher.generate_sample_data(days=30)
    else:
        days = int(input("Number of days to simulate [30]: ") or "30")
        df = fetcher.generate_sample_data(days=days)

    if df is None or df.empty:
        print("❌ No data available")
        return

    print()
    print("Running backtest...")
    print()

    # Create backtester
    backtester = Backtester(
        initial_balance=initial_balance,
        lot_size=lot_size,
        risk_reward_ratio=risk_reward,
        consolidation_periods=consol_periods,
        breakout_threshold=breakout_threshold,
        max_daily_trades=max_daily_trades
    )

    # Run backtest
    results = backtester.run_backtest(df)

    # Print results
    backtester.print_results()

    # Save results
    backtester.save_results('backtest_results_custom.json')
    backtester.export_trades_to_csv('backtest_trades_custom.csv')

    return results


def run_optimization():
    """Test multiple parameter combinations"""
    print("=" * 70)
    print("🔬 PARAMETER OPTIMIZATION")
    print("=" * 70)
    print()
    print("Testing different parameter combinations to find the best settings...")
    print()

    # Generate test data once
    fetcher = DataFetcher()
    df = fetcher.generate_sample_data(days=30)

    if df is None or df.empty:
        print("❌ Failed to generate data")
        return

    # Parameter ranges to test
    risk_rewards = [1.5, 2.0, 2.5, 3.0]
    consolidation_periods_list = [15, 20, 25, 30]
    breakout_thresholds = [0.002, 0.003, 0.004, 0.005]

    best_return = -float('inf')
    best_params = None
    all_results = []

    total_tests = len(risk_rewards) * len(consolidation_periods_list) * len(breakout_thresholds)
    current_test = 0

    print(f"Running {total_tests} different parameter combinations...")
    print()

    for rr in risk_rewards:
        for cp in consolidation_periods_list:
            for bt in breakout_thresholds:
                current_test += 1

                # Create backtester
                backtester = Backtester(
                    initial_balance=10000,
                    lot_size=0.01,
                    risk_reward_ratio=rr,
                    consolidation_periods=cp,
                    breakout_threshold=bt,
                    max_daily_trades=5
                )

                # Run backtest silently
                print(f"[{current_test}/{total_tests}] Testing: RR={rr}, CP={cp}, BT={bt}...", end=" ")

                results = backtester.run_backtest(df)

                # Store results
                params = {
                    'risk_reward': rr,
                    'consolidation_periods': cp,
                    'breakout_threshold': bt,
                    'return_pct': results['return_pct'],
                    'win_rate': results['win_rate'],
                    'total_trades': results['total_trades'],
                    'profit_factor': results['profit_factor'],
                    'max_drawdown_pct': results['max_drawdown_pct']
                }

                all_results.append(params)

                print(f"Return: {results['return_pct']:.2f}%")

                # Track best
                if results['return_pct'] > best_return and results['total_trades'] >= 10:
                    best_return = results['return_pct']
                    best_params = params

    print()
    print("=" * 70)
    print("🏆 OPTIMIZATION RESULTS")
    print("=" * 70)
    print()

    if best_params:
        print("Best Parameters Found:")
        print(f"  Risk:Reward Ratio:      {best_params['risk_reward']}")
        print(f"  Consolidation Periods:  {best_params['consolidation_periods']}")
        print(f"  Breakout Threshold:     {best_params['breakout_threshold']}")
        print()
        print("Performance with Best Parameters:")
        print(f"  Return:                 {best_params['return_pct']:.2f}%")
        print(f"  Win Rate:               {best_params['win_rate']:.2f}%")
        print(f"  Total Trades:           {best_params['total_trades']}")
        print(f"  Profit Factor:          {best_params['profit_factor']:.2f}")
        print(f"  Max Drawdown:           {best_params['max_drawdown_pct']:.2f}%")
    else:
        print("❌ No profitable parameter combination found")

    print()
    print("=" * 70)

    # Show top 5 results
    print()
    print("Top 5 Parameter Combinations:")
    print()
    sorted_results = sorted(all_results, key=lambda x: x['return_pct'], reverse=True)[:5]

    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. RR={result['risk_reward']}, CP={result['consolidation_periods']}, "
              f"BT={result['breakout_threshold']} → Return: {result['return_pct']:.2f}%")

    print()
    print("=" * 70)


def main():
    """Main menu"""
    print()
    print("=" * 70)
    print("          NAS100 BREAKOUT STRATEGY - BACKTESTING SYSTEM")
    print("=" * 70)
    print()
    print("No MT5 required! Test the strategy locally on your computer.")
    print()
    print("Choose a backtest mode:")
    print()
    print("1. Quick Test (synthetic data, 30 days, default settings)")
    print("2. Real Data Test (download recent market data)")
    print("3. Custom Test (choose your own parameters)")
    print("4. Parameter Optimization (find best settings)")
    print("5. Exit")
    print()

    choice = input("Enter your choice (1-5): ").strip()

    if choice == "1":
        run_quick_backtest()
    elif choice == "2":
        run_real_data_backtest()
    elif choice == "3":
        run_custom_backtest()
    elif choice == "4":
        run_optimization()
    elif choice == "5":
        print("\n👋 Goodbye!")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")
        return

    # Ask if they want to run another test
    print()
    again = input("Run another backtest? (y/n): ").strip().lower()
    if again == 'y':
        print()
        main()
    else:
        print("\n👋 Happy trading! Remember to test thoroughly before going live.")


if __name__ == "__main__":
    main()
