# NAS100 Breakout Trading Bot

Automated trading bot based on consolidation breakout strategy for NAS100 (NASDAQ 100 Index).

## 🎯 Strategy Overview

This bot implements the **consolidation breakout strategy** as demonstrated in your mentor's trading screenshots:

- Identifies price consolidation zones (box patterns)
- Detects breakouts above/below consolidation
- Places trades with defined Stop Loss and Take Profit
- Uses volume confirmation for trade validation
- Implements proper risk management

## 📁 Project Files

```
nas100-bot/
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
├── requirements.txt             # Python dependencies
├── test_setup.py               # Setup verification script
├── config.py                   # Configuration settings
├── nas100_breakout_bot.py      # Basic trading bot
└── enhanced_bot.py             # Advanced bot with features
```

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Setup MT5
- Install MetaTrader 5
- Create a DEMO account
- Enable automated trading in settings

### 3. Configure Bot
Edit `config.py`:
```python
MT5_ACCOUNT = your_account_number
MT5_PASSWORD = "your_password"
MT5_SERVER = "YourBroker-Demo"
SYMBOL = "NAS100"  # Verify with your broker
LOT_SIZE = 0.01    # Start small!
```

### 4. Test Setup
```bash
python test_setup.py
```

### 5. Run Bot
```bash
# Basic version
python nas100_breakout_bot.py

# Or enhanced version with all features
python enhanced_bot.py
```

## 📊 Strategy Details

### From Your Mentor's Screenshots:

**Entry Logic:**
1. Bot identifies consolidation (tight price range)
2. Waits for price to break out of the range
3. Confirms with volume increase
4. Places trade in breakout direction

**Exit Logic:**
- **Stop Loss**: Placed opposite side of consolidation box
- **Take Profit**: Risk-Reward ratio of 1:2 (default)
- Can be adjusted in config.py

### Visual Representation:
```
Consolidation Phase:
     ┌─────────────┐ ← High Level (25,410)
     │   Range:    │
     │   50 points │
     └─────────────┘ ← Low Level (25,360)

Breakout Buy Signal:
     ← Price breaks above
     ┌─────────────┐ Entry: 25,411
     │             │ Stop Loss: 25,351 
     └─────────────┘ Take Profit: 25,531
```

## 🛡️ Risk Management

### CRITICAL RULES:

1. **ALWAYS START WITH DEMO**
   - Test for minimum 1 month
   - Never skip this step!

2. **Position Sizing**
   - Start: 0.01 lots
   - Risk: Maximum 2% per trade
   - Never risk money you can't afford to lose

3. **Daily Limits**
   - Max 5 trades per day (default)
   - Stop after 3 consecutive losses
   - Adjust in config.py

4. **Monitor Performance**
   - Target win rate: >45%
   - Risk-Reward: 1:2 minimum
   - Max drawdown: <20%

## 📈 Expected Performance

Based on the strategy:

| Metric | Target |
|--------|--------|
| Win Rate | 45-55% |
| Risk:Reward | 1:2 |
| Daily Trades | 3-7 |
| Daily Return | 1-3% |
| Max Drawdown | <20% |

**Note**: Past performance does not guarantee future results.

## 🔧 Configuration Options

### Basic Settings:
```python
SYMBOL = "NAS100"              # Trading instrument
LOT_SIZE = 0.01                # Position size
RISK_REWARD_RATIO = 2.0        # TP is 2x risk
```

### Strategy Parameters:
```python
CONSOLIDATION_PERIODS = 20     # Bars to identify range
BREAKOUT_THRESHOLD = 0.0015    # 0.15% for consolidation
```

### Operational:
```python
TRADING_START_HOUR = 0         # Start time (UTC)
TRADING_END_HOUR = 23          # End time (UTC)
MAX_DAILY_TRADES = 5           # Daily trade limit
CHECK_INTERVAL = 10            # Seconds between checks
```

## 📱 Features

### Basic Bot (`nas100_breakout_bot.py`):
- ✅ Consolidation detection
- ✅ Breakout identification
- ✅ Automated trading
- ✅ Stop Loss & Take Profit
- ✅ Basic logging

### Enhanced Bot (`enhanced_bot.py`):
- ✅ All basic features
- ✅ Advanced risk management
- ✅ Telegram notifications
- ✅ Trading hours control
- ✅ Daily trade limits
- ✅ Performance statistics
- ✅ Trade history logging
- ✅ Dynamic position sizing

## 🔍 Monitoring

### Console Output:
```
🚀 Starting NAS100 Breakout Bot...
Symbol: NAS100
Timeframe: 1-minute
Lot Size: 0.01
Risk:Reward = 1:2.0
--------------------------------------------------
📊 2024-11-17 10:30:00
Current Price: 25370.50
📦 Consolidation detected!
   High: 25410.00
   Low: 25360.00
   Range: 50.00

🔥 BREAKOUT DETECTED: BUY
✅ BUY order placed successfully!
Entry: 25411.00
TP: 25531.00
SL: 25351.00
```

### Log Files:
- `nas100_bot.log` - Detailed activity log
- `trade_history.json` - All trades recorded

## 🆘 Troubleshooting

### Common Issues:

**"MT5 initialization failed"**
- Ensure MT5 is running
- Enable automated trading in Tools → Options
- Check MT5 allows API connections

**"Invalid symbol"**
- Verify symbol name in MT5 Market Watch
- Common names: NAS100, US100, USTEC, US100.cash
- Update SYMBOL in config.py

**"Not enough money"**
- Reduce LOT_SIZE in config
- Check account balance
- Verify margin requirements

**No trades placed**
- Market may not be consolidating
- Adjust BREAKOUT_THRESHOLD
- Check trading hours settings

See `SETUP_GUIDE.md` for detailed troubleshooting.

## 📚 Documentation

- **SETUP_GUIDE.md** - Complete setup instructions
- **config.py** - All configuration options with comments
- **Code comments** - Detailed explanations in source files

## ⚠️ Disclaimers

1. **Trading Risk**
   - Forex trading involves substantial risk
   - Only trade with money you can afford to lose
   - Past performance ≠ future results

2. **No Guarantees**
   - This bot does not guarantee profits
   - Losses are part of trading
   - Your mentor's results may differ from yours

3. **Education Required**
   - Understand the strategy before using bot
   - Learn manual trading first
   - Automation is a tool, not a solution

4. **Demo First**
   - ALWAYS test with demo account
   - Minimum 1 month of testing
   - Verify profitability before going live

5. **Broker Risk**
   - Use only regulated brokers
   - Keep funds in separate accounts
   - Withdraw profits regularly

## 🎓 Learning Resources

- **Forex Basics**: babypips.com
- **MT5 Documentation**: mql5.com
- **Risk Management**: investopedia.com
- **Trading Psychology**: tradingpsychology.com

## 💡 Tips for Success

1. **Start Small**
   - Begin with 0.01 lots
   - Increase gradually with success
   - Never risk more than 2% per trade

2. **Keep Records**
   - Review trade history regularly
   - Analyze winning and losing trades
   - Adjust strategy as needed

3. **Be Patient**
   - Don't expect immediate profits
   - Give strategy time to work
   - Avoid over-optimization

4. **Stay Disciplined**
   - Follow your trading plan
   - Don't override the bot emotionally
   - Accept losses as part of the process

5. **Continuous Learning**
   - Study market conditions
   - Understand why trades win/lose
   - Improve strategy over time

## 🤝 Support

For issues or questions:

1. Check SETUP_GUIDE.md first
2. Review error logs
3. Verify all configuration settings
4. Test with demo account

## 📝 Version Info

- **Version**: 1.0
- **Strategy**: Consolidation Breakout
- **Market**: NAS100 (NASDAQ 100)
- **Timeframe**: 1-minute default (configurable)
- **Risk Management**: Built-in

## 🏆 Strategy Credits

This bot is based on the consolidation breakout strategy demonstrated by your trading mentor. The implementation includes:
- Pattern recognition from screenshots
- Entry/exit logic similar to "team hits" approach
- Risk management principles
- Volume confirmation techniques

---

## 🚦 Quick Start Checklist

Before running the bot, ensure you have:

- [ ] Installed MetaTrader 5
- [ ] Created demo account
- [ ] Installed Python 3.8+
- [ ] Installed required libraries (`pip install -r requirements.txt`)
- [ ] Edited config.py with your credentials
- [ ] Run test_setup.py successfully
- [ ] Verified symbol name in MT5
- [ ] Set lot size to 0.01
- [ ] Read SETUP_GUIDE.md
- [ ] Understood the strategy
- [ ] Ready to start with DEMO

---

**Remember: Success in trading comes from discipline, risk management, and continuous learning.**

**"The goal of a successful trader is to make the best trades. Money is secondary."** - Alexander Elder

---

*Built with Python 🐍 | Powered by MT5 📈 | Trade Responsibly 🛡️*
