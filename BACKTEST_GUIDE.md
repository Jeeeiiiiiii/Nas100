# 🔬 Backtesting Guide

## What is Backtesting?

**Backtesting** means testing your trading strategy on historical data to see if it would have been profitable in the past. It's like a time machine for trading - you can see how your strategy would have performed without risking real money.

## ✅ Why Backtest First?

1. **Test without risk** - No real money needed
2. **See if strategy works** - Is it actually profitable?
3. **Find best settings** - Optimize parameters
4. **Build confidence** - Know what to expect
5. **Save money** - Avoid losing on bad strategies

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Install only what you need for backtesting (no MT5 required!)
pip install pandas numpy yfinance
```

**Note**: You DON'T need MetaTrader5 for backtesting!

### Step 2: Run Your First Backtest

```bash
python run_backtest.py
```

Choose option **1** for a quick test with synthetic data.

### Step 3: Review Results

The backtest will show you:
- ✅ Total profit/loss
- ✅ Win rate (% of winning trades)
- ✅ Number of trades
- ✅ Maximum drawdown (biggest loss period)
- ✅ Whether the strategy is profitable

## 📊 Backtest Modes

### Mode 1: Quick Test (Recommended for First Time)

```bash
python run_backtest.py
# Choose option 1
```

- Uses **synthetic data** (computer-generated, but realistic)
- Tests **30 days** of trading
- Uses **default settings**
- **No internet needed** after first run
- Perfect for learning how it works

**Output example:**
```
Initial Balance:  $10,000.00
Final Balance:    $10,450.00
Net Profit:       $450.00
Return:           4.50%
Win Rate:         52.00%
```

### Mode 2: Real Data Test

```bash
python run_backtest.py
# Choose option 2
```

- Downloads **real market data** from Yahoo Finance
- Tests last **7 days** (that's the limit for 1-minute data)
- More accurate results
- Requires internet connection

### Mode 3: Custom Test

```bash
python run_backtest.py
# Choose option 3
```

Test with your own settings:
- Initial balance
- Lot size
- Risk:Reward ratio
- Consolidation periods
- And more...

### Mode 4: Parameter Optimization

```bash
python run_backtest.py
# Choose option 4
```

Automatically tests different parameter combinations to find the best settings.

**Example output:**
```
Best Parameters Found:
  Risk:Reward Ratio:      2.5
  Consolidation Periods:  25
  Breakout Threshold:     0.0015
  Return:                 8.50%
```

## 📈 Understanding Results

### Key Metrics Explained

**1. Win Rate**
- Percentage of trades that were profitable
- **Good**: 45% or higher
- **Excellent**: 55% or higher

**2. Profit Factor**
- Total profits ÷ Total losses
- **Good**: 1.5 or higher
- **Excellent**: 2.0 or higher

**3. Return %**
- How much your account grew
- **Good**: Positive (any profit)
- **Excellent**: 5%+ per month

**4. Max Drawdown**
- Biggest drop from peak balance
- **Good**: Less than 20%
- **Warning**: Over 30% is risky

### What Makes a Good Strategy?

✅ **PROFITABLE Strategy:**
- Win rate: 45-55%
- Profit factor: 1.5+
- Positive returns
- Max drawdown: <20%
- At least 30 trades for reliability

❌ **NOT PROFITABLE Strategy:**
- Win rate: <40%
- Profit factor: <1.0
- Negative returns
- Inconsistent results

## 🎯 Next Steps Based on Results

### If Backtest Shows Profit ✅

1. **Run more backtests** with different time periods
2. **Try parameter optimization** to improve further
3. **Test with real market data**
4. **Then** consider MT5 demo account testing
5. **Never skip demo testing!**

### If Backtest Shows Loss ❌

1. **Try parameter optimization** (option 4)
2. **Adjust risk management** (lower lot size)
3. **Test different timeframes** (5m instead of 1m)
4. **Consider strategy modifications**
5. **Don't rush to live trading**

## 🛠️ Advanced Usage

### Running Backtests Programmatically

```python
from data_fetcher import DataFetcher
from backtester import Backtester

# Get data
fetcher = DataFetcher()
df = fetcher.generate_sample_data(days=30)

# Run backtest
backtester = Backtester(
    initial_balance=10000,
    lot_size=0.01,
    risk_reward_ratio=2.0
)

results = backtester.run_backtest(df)
backtester.print_results()
```

### Using Real Downloaded Data

```python
# Download once
fetcher = DataFetcher()
df = fetcher.download_recent_data(days=7, interval="1m")
fetcher.save_data(df, "my_data.csv")

# Load later
df = fetcher.load_data("my_data.csv")
backtester.run_backtest(df)
```

### Testing Different Timeframes

```python
# 5-minute bars (more reliable for backtesting)
df = fetcher.download_data("2024-01-01", "2024-12-31", interval="5m")

# 15-minute bars (even more stable)
df = fetcher.download_data("2024-01-01", "2024-12-31", interval="15m")

# Daily bars (long-term testing)
df = fetcher.download_data("2023-01-01", "2024-12-31", interval="1d")
```

## 💡 Tips for Better Backtesting

### 1. Test Multiple Time Periods
Don't just test one month. Try:
- Bull markets (prices going up)
- Bear markets (prices going down)
- Sideways markets (consolidation)
- Different seasons/years

### 2. Use Enough Data
- Minimum: 100 trades
- Good: 500+ trades
- Excellent: 1000+ trades

### 3. Be Realistic
- Include slippage (prices move while ordering)
- Account for spreads (broker fees)
- Don't over-optimize (curve fitting)

### 4. Walk-Forward Testing
1. Test on old data (e.g., Jan-Jun)
2. Optimize parameters
3. Verify on new data (e.g., Jul-Dec)
4. If it still works, strategy is robust!

## ⚠️ Common Mistakes

### ❌ Don't Do This:

1. **Over-optimization** - Finding settings that work perfectly on one dataset but fail on others
2. **Too little data** - Testing only 1 week and assuming it works
3. **Ignoring drawdowns** - Only looking at profits, not losses
4. **Skipping demo** - Going straight from backtest to live money
5. **Changing parameters constantly** - Stick with a strategy long enough to judge it

### ✅ Do This Instead:

1. **Test robustly** - Multiple timeframes, multiple periods
2. **Accept imperfection** - No strategy wins 100%
3. **Focus on consistency** - Steady gains > lucky wins
4. **Be patient** - Testing phase is crucial
5. **Keep learning** - Improve strategy based on results

## 📁 Output Files

After backtesting, you'll get:

```
backtest_results.json       # Detailed statistics
backtest_trades.csv         # Every trade recorded
```

### Analyzing Trade History

```python
import pandas as pd

# Load your trades
trades = pd.read_csv('backtest_trades.csv')

# Find best performing trades
winning_trades = trades[trades['win'] == True]
print(winning_trades.describe())

# Find what went wrong
losing_trades = trades[trades['win'] == False]
print(losing_trades.describe())
```

## 🎓 Learning Path

### Week 1: Understanding
- Run quick tests
- Understand the metrics
- Read the strategy code

### Week 2: Optimization
- Try different parameters
- Test various timeframes
- Find best settings

### Week 3: Validation
- Test on different data
- Verify consistency
- Build confidence

### Week 4: Preparation
- Set up MT5 demo account
- Prepare for live testing
- Review risk management

## 🤔 FAQ

**Q: Do I need MT5 for backtesting?**
A: No! Backtesting runs completely independently.

**Q: Is synthetic data realistic?**
A: It's good for initial testing. For serious validation, use real data.

**Q: How long should I backtest?**
A: At least 1-3 months of data, preferably 6-12 months.

**Q: If backtest is profitable, will live trading be too?**
A: Not guaranteed! Backtest → Demo → Live (in that order, always).

**Q: Can I backtest 24/7?**
A: Yes, backtesting is instant. Years of data tested in seconds.

**Q: What's a good return %?**
A: 2-5% per month is excellent for consistent strategies.

## 🚦 Decision Flowchart

```
┌─────────────────────┐
│  Run Backtest       │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ Profitable? │
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
    YES          NO
     │           │
     ▼           ▼
┌─────────┐  ┌─────────────┐
│Optimize │  │ Adjust      │
│Further  │  │ Parameters  │
└────┬────┘  └──────┬──────┘
     │              │
     ▼              │
┌─────────┐         │
│Test on  │         │
│Real Data│         │
└────┬────┘         │
     │              │
     ▼              │
┌─────────┐         │
│Still    │◄────────┘
│Good?    │
└────┬────┘
     │
    YES
     │
     ▼
┌──────────┐
│Try Demo  │
│Account   │
└──────────┘
```

## 📞 Need Help?

If backtest results don't make sense:
1. Check the code comments in `backtester.py`
2. Review `SETUP_GUIDE.md` for basics
3. Try the quick test first (option 1)
4. Start with default parameters

---

**Remember**: Backtesting is just the first step. Always follow:
**Backtest → Optimize → Demo Test → Small Live → Scale Up**

Never skip steps! 🛡️

---

*Happy Backtesting! 📊*
