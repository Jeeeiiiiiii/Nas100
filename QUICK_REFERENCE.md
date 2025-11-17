# NAS100 Bot - Quick Reference Card

## 🚀 Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py

# Run basic bot
python nas100_breakout_bot.py

# Run enhanced bot
python enhanced_bot.py
```

## ⚙️ Essential Config

```python
# config.py - Edit these first!
MT5_ACCOUNT = 12345678
MT5_PASSWORD = "your_password"
MT5_SERVER = "YourBroker-Demo"
SYMBOL = "NAS100"  # or "US100", "USTEC"
LOT_SIZE = 0.01
```

## 📊 Strategy at a Glance

```
1. Find consolidation box
2. Wait for breakout
3. Enter trade
4. Set SL at box opposite
5. Set TP at 2x risk
```

## 🎯 Key Levels

```
Entry Types:
BUY  = Break above high
SELL = Break below low

Stop Loss:
BUY  = Below box low
SELL = Above box high

Take Profit:
BUY  = Entry + (2 × Risk)
SELL = Entry - (2 × Risk)
```

## ⚡ Quick Checks

Before running:
- [ ] MT5 is open and running
- [ ] Using DEMO account
- [ ] config.py edited
- [ ] Lot size = 0.01
- [ ] Symbol name verified

## 🔥 Success Indicators

```
Good:
✅ Win rate > 45%
✅ Risk:Reward = 1:2
✅ 3-7 trades/day
✅ Consistent results

Bad:
❌ Win rate < 40%
❌ Many consecutive losses
❌ Drawdown > 20%
❌ Emotional trading
```

## 🛑 Emergency Stops

```
Stop Trading If:
• 3 losses in a row
• Daily loss > 5%
• Technical issues
• Unusual market behavior
• Feeling emotional
```

## 📱 Quick Stats

```
Target Performance:
Win Rate:     50-55%
Daily Trades: 3-7
Daily Return: 1-3%
Max Drawdown: <20%
Risk/Trade:   2%
```

## 🔧 Common Fixes

```
Error                  → Fix
─────────────────────────────────────
MT5 init failed       → Open MT5, enable API
Invalid symbol        → Check symbol name
Not enough money      → Lower lot size
No trades             → Adjust thresholds
Connection lost       → Check internet
```

## 📋 File Overview

```
File                    Purpose
───────────────────────────────────────────────
README.md              Main documentation
SETUP_GUIDE.md         Detailed setup
VISUAL_STRATEGY_GUIDE  Strategy explanation
config.py              All settings
nas100_breakout_bot.py Basic bot
enhanced_bot.py        Full-featured bot
test_setup.py          Verify installation
requirements.txt       Dependencies
```

## ⏱️ Typical Timeline

```
Day 1:  Setup & Installation
Day 2:  Test with demo
Week 1: Monitor & adjust
Week 2: Optimize settings
Week 4: Evaluate performance
Month 3: Consider live (if profitable)
```

## 💰 Position Sizing Guide

```
Balance    Lot Size    Risk/Trade
──────────────────────────────────
$100       0.01        $2
$500       0.01        $5
$1,000     0.02        $10
$2,500     0.05        $25
$5,000     0.10        $50
$10,000    0.20        $100
```

## 🎓 Key Principles

```
1. DEMO FIRST - Always!
2. Small Sizes - Start tiny
3. Risk Management - Never exceed 2%
4. Discipline - Follow the plan
5. Patience - Wait for setups
6. Record Keeping - Track everything
7. Continuous Learning - Improve always
```

## 🚨 Warning Signs

```
Stop and Review If:
• Losing streak > 3 trades
• Daily loss > 5%
• Win rate dropping
• Increased slippage
• Unusual spread widening
• Broker issues
• Platform freezing
```

## 📞 Support Checklist

```
Before asking for help:
□ Read SETUP_GUIDE.md
□ Checked error logs
□ Verified config.py
□ Tested with demo
□ Checked internet connection
□ Restarted MT5
□ Restarted bot
```

## 🎯 Daily Routine

```
Morning:
1. Check MT5 connection
2. Review overnight trades
3. Check market conditions
4. Start bot

During Day:
5. Monitor performance
6. Check for errors
7. Review trade entries

Evening:
8. Review daily stats
9. Log performance
10. Plan adjustments
```

## 🔐 Security Tips

```
✅ DO:
• Use strong passwords
• Enable 2FA where available
• Use demo account first
• Withdraw profits regularly
• Keep software updated

❌ DON'T:
• Share account credentials
• Use on public WiFi
• Leave bot unmonitored
• Risk more than you afford
• Override bot emotionally
```

## 📈 Performance Tracking

```
Daily Log:
Date: ___________
Trades: ___ Win: ___ Loss: ___
Win Rate: ___%
P&L: $_____
Notes: _________________
```

## 🌟 Pro Tips

```
• Let winners run to TP
• Cut losses at SL quickly
• Don't overtrade
• Quality > Quantity
• Trust the process
• Keep learning
• Stay disciplined
```

## 🏁 Final Checklist

```
Ready to Trade?
□ Understand the strategy
□ Demo account set up
□ MT5 properly configured
□ Bot tested successfully
□ Risk management clear
□ Trading plan written
□ Ready for losses
□ Committed to discipline
```

---

**Remember:**
- Demo first, always!
- Start small, scale slowly
- Risk management is key
- Discipline beats strategy
- Learning never stops

**Good luck! 🚀**

---

*For detailed information, see full documentation files.*
*Emergency? Stop the bot, review logs, check SETUP_GUIDE.md*
