"""Debug script to understand why backtest finds no trades"""

from data_fetcher import DataFetcher
from backtester import Backtester
import pandas as pd

# Generate data
fetcher = DataFetcher()
df = fetcher.load_data("NAS100_synthetic_30days.csv")

if df is None:
    df = fetcher.generate_sample_data(days=5)

# Create backtester
bt = Backtester(
    initial_balance=10000,
    lot_size=0.01,
    risk_reward_ratio=2.0,
    consolidation_periods=20,
    breakout_threshold=0.0015
)

print("Analyzing first 500 bars...\n")

consolidation_count = 0
for i in range(100, min(500, len(df))):
    is_consol, high, low, box_range = bt.identify_consolidation(df, i)

    if is_consol:
        consolidation_count += 1
        current_price = df.iloc[i]['close']
        signal = bt.detect_breakout(df, i, high, low)

        if signal or consolidation_count <= 3:  # Show first 3 or any with signal
            print(f"Bar {i}: Consolidation found!")
            print(f"  High: {high:.2f}, Low: {low:.2f}, Range: {box_range:.2f}")
            print(f"  Current Price: {current_price:.2f}")
            print(f"  Signal: {signal if signal else 'None'}")
            print()

print(f"\nTotal consolidations found: {consolidation_count}")
print(f"Breakout threshold: {bt.breakout_threshold} (0.15%)")
print(f"\nTrying with higher threshold (0.5%)...")

# Try with higher threshold
bt2 = Backtester(
    initial_balance=10000,
    lot_size=0.01,
    risk_reward_ratio=2.0,
    consolidation_periods=20,
    breakout_threshold=0.005  # 0.5% instead of 0.15%
)

print("\nRunning backtest with 0.5% threshold...")
results = bt2.run_backtest(df.head(1000))  # Just first 1000 bars for speed
bt2.print_results()
