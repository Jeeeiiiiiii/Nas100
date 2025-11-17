"""
Data Fetcher for NAS100 Historical Data
Downloads free historical data for backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("yfinance not installed. Install with: pip install yfinance")


class DataFetcher:
    """Fetch historical market data for backtesting"""

    def __init__(self, symbol="NQ=F", data_dir="historical_data"):
        """
        Initialize data fetcher

        Parameters:
        - symbol: Yahoo Finance ticker (NQ=F for NASDAQ 100 futures)
        - data_dir: Directory to store downloaded data
        """
        self.symbol = symbol
        self.data_dir = data_dir

        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def download_data(self, start_date, end_date, interval="1m"):
        """
        Download historical data from Yahoo Finance

        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - interval: Data interval (1m, 5m, 15m, 1h, 1d)

        Returns:
        - DataFrame with OHLCV data
        """
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance is required. Install with: pip install yfinance")

        print(f"📥 Downloading {self.symbol} data from {start_date} to {end_date}...")
        print(f"   Interval: {interval}")

        try:
            # Download data
            df = yf.download(
                self.symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=True
            )

            if df.empty:
                print("❌ No data downloaded. Check symbol and date range.")
                return None

            # Standardize column names (remove multi-index if present)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Rename columns to match MT5 format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'tick_volume'
            })

            # Reset index to make datetime a column
            df = df.reset_index()
            df = df.rename(columns={'Datetime': 'time', 'Date': 'time'})

            # Ensure we have the required columns
            required_cols = ['time', 'open', 'high', 'low', 'close', 'tick_volume']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'tick_volume':
                        df['tick_volume'] = 1000  # Dummy volume if not available
                    else:
                        raise ValueError(f"Missing required column: {col}")

            df = df[required_cols]

            print(f"✅ Downloaded {len(df)} bars")
            print(f"   Date range: {df['time'].min()} to {df['time'].max()}")

            return df

        except Exception as e:
            print(f"❌ Error downloading data: {e}")
            return None

    def save_data(self, df, filename=None):
        """Save data to CSV file"""
        if df is None or df.empty:
            print("❌ No data to save")
            return False

        if filename is None:
            filename = f"{self.symbol}_{datetime.now().strftime('%Y%m%d')}.csv"

        filepath = os.path.join(self.data_dir, filename)

        try:
            df.to_csv(filepath, index=False)
            print(f"💾 Data saved to: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False

    def load_data(self, filename):
        """Load data from CSV file"""
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return None

        try:
            df = pd.read_csv(filepath)
            df['time'] = pd.to_datetime(df['time'])
            print(f"✅ Loaded {len(df)} bars from {filename}")
            return df
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None

    def get_available_files(self):
        """List available data files"""
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        if files:
            print(f"📁 Available data files:")
            for f in files:
                print(f"   - {f}")
        else:
            print("📁 No data files found")
        return files

    def download_recent_data(self, days=7, interval="1m"):
        """
        Download recent data for quick testing

        Parameters:
        - days: Number of days to download (max 7 for 1m interval)
        - interval: Data interval
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Note: Yahoo Finance limits 1m data to last 7 days
        if interval == "1m" and days > 7:
            print("⚠️  Warning: 1-minute data limited to last 7 days on Yahoo Finance")
            days = 7
            start_date = end_date - timedelta(days=days)

        df = self.download_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            interval=interval
        )

        if df is not None:
            filename = f"NAS100_recent_{days}days_{interval}.csv"
            self.save_data(df, filename)

        return df

    def generate_sample_data(self, days=30, interval_minutes=1):
        """
        Generate synthetic data for testing when real data unavailable

        This creates realistic-looking price data with:
        - Trend movements
        - Clear consolidation periods
        - Breakout patterns
        - Volatility
        """
        print(f"🎲 Generating synthetic data for {days} days...")

        # Calculate number of bars
        bars_per_day = int(24 * 60 / interval_minutes)
        total_bars = days * bars_per_day

        # Starting price around NAS100 typical range
        start_price = 16000

        # Generate base price with clear consolidation/breakout patterns
        np.random.seed(42)

        # Create price action with consolidation zones
        prices = [start_price]
        in_consolidation = False
        consol_duration = 0
        consol_price = start_price

        for i in range(1, total_bars):
            # Decide if we should enter/exit consolidation
            if not in_consolidation and np.random.rand() < 0.05:  # 5% chance to start consolidation
                in_consolidation = True
                consol_duration = np.random.randint(30, 100)  # 30-100 bars
                consol_price = prices[-1]

            if in_consolidation:
                # Stay in tight range during consolidation
                change = np.random.randn() * 5  # Small movement
                new_price = consol_price + change
                consol_duration -= 1

                if consol_duration <= 0:
                    # Breakout!
                    in_consolidation = False
                    # Strong move after consolidation
                    breakout_direction = 1 if np.random.rand() > 0.5 else -1
                    new_price = consol_price + (50 * breakout_direction) + np.random.randn() * 10
            else:
                # Trending / normal movement
                change = np.random.randn() * 15 + 1  # Slight upward bias
                new_price = prices[-1] + change

            prices.append(new_price)

        # Generate OHLC data from prices
        data = []
        base_time = datetime.now() - timedelta(days=days)

        for i in range(total_bars):
            close = prices[i]

            # Generate realistic OHLC
            open_price = prices[i-1] if i > 0 else close

            # High/Low based on intra-bar movement
            volatility = abs(np.random.randn()) * 10
            high = max(open_price, close) + volatility
            low = min(open_price, close) - volatility

            current_time = base_time + timedelta(minutes=i * interval_minutes)

            data.append({
                'time': current_time,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'tick_volume': int(np.random.randint(800, 1200))
            })

        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df)} bars of synthetic data")
        print(f"   With deliberate consolidation/breakout patterns for testing")

        # Save it
        filename = f"NAS100_synthetic_{days}days.csv"
        self.save_data(df, filename)

        return df


def main():
    """Example usage"""
    fetcher = DataFetcher()

    print("=" * 60)
    print("NAS100 Data Fetcher")
    print("=" * 60)
    print()

    # Show menu
    print("Choose an option:")
    print("1. Download recent data (last 7 days, 1-minute)")
    print("2. Download custom date range")
    print("3. Generate synthetic test data (30 days)")
    print("4. List available data files")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        fetcher.download_recent_data(days=7, interval="1m")

    elif choice == "2":
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        interval = input("Interval (1m/5m/15m/1h/1d) [1m]: ").strip() or "1m"

        df = fetcher.download_data(start, end, interval)
        if df is not None:
            filename = f"NAS100_{start}_to_{end}_{interval}.csv"
            fetcher.save_data(df, filename)

    elif choice == "3":
        days = input("Number of days [30]: ").strip() or "30"
        fetcher.generate_sample_data(days=int(days))

    elif choice == "4":
        fetcher.get_available_files()

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
