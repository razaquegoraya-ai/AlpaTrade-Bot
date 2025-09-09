# 🚀 AlpaTrade Bot - Professional Trading System

A comprehensive automated trading bot built with FastAPI and Alpaca API, featuring advanced technical analysis, sentiment analysis, and sophisticated risk management.

## ✨ **Project Status: COMPLETED** ✅

**All requested features have been successfully implemented and tested!**

---

## 🎯 **Implemented Features**

### **✅ Trading Strategies**
- **Stochastic Oscillator** with customizable periods and thresholds
- **Commodity Channel Index (CCI)** for trend analysis
- **Multi-timeframe analysis** (1D, 1H, 30Min, etc.)
- **Configurable strategy parameters** for fine-tuning

### **✅ Risk Management**
- **Stop-loss and trailing stop** orders
- **Capital allocation control** (% of balance per trade)
- **Maximum positions limit**
- **Real-time position monitoring**

### **✅ Automation Modes**
- **Auto**: Fully automated trading
- **Alert Only**: Generate signals without trading
- **Semi-Auto**: Manual confirmation required

### **✅ News & Sentiment Analysis**
- **Real-time news fetching** from multiple sources
- **VADER sentiment analysis** for trade filtering
- **Symbol-specific sentiment** tracking
- **Market sentiment** overview

### **✅ Web Dashboard**
- **Real-time account overview** (balance, P/L, positions)
- **Live market status** and trading hours
- **Strategy management** interface
- **Pending signals** with manual confirmation
- **Order history** and position tracking

---

## 🚀 **Quick Start Guide**

### **Step 1: Setup Environment**

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configure Alpaca API**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env file with your Alpaca credentials
# Get your API keys from: https://app.alpaca.markets/paper/dashboard/overview
```

**Required API Keys:**
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_SECRET_KEY`: Your Alpaca secret key
- `ALPACA_BASE_URL`: https://paper-api.alpaca.markets (for paper trading)

### **Step 3: Run the Application**

```bash
# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

### **Step 4: Access Dashboard**

Open your browser and navigate to: **`http://localhost:8000`**

---

## 📋 **Testing Without API Keys**

**You can test the system without Alpaca API keys:**

1. **Dashboard loads** with placeholder data
2. **UI functionality** works completely
3. **Strategy creation** and management works
4. **All features** are accessible and functional

**To get full functionality:**
- Sign up for free Alpaca paper trading account
- Get your API keys from the dashboard
- Add them to the `.env` file

---

## 🎮 **How to Use the Dashboard**

### **1. Dashboard Tab**
- View account overview, market status, and bot status
- Start/stop the trading bot
- Set up your watchlist

### **2. Positions Tab**
- Monitor current holdings
- View unrealized P/L
- Track position performance

### **3. Orders Tab**
- Review order history
- Monitor order status
- Track execution details

### **4. Strategies Tab**
- Create custom trading strategies
- Configure Stochastic and CCI parameters
- Set risk management rules

### **5. Signals Tab**
- Review pending trading signals
- Manually confirm or reject trades
- Monitor signal confidence levels

---

## ⚙️ **Configuration Examples**

### **Basic Strategy Configuration**
```json
{
  "name": "My First Strategy",
  "automation_mode": "alert_only",
  "capital_allocation_percent": 10.0,
  "stoch_k_period": 14,
  "stoch_d_period": 3,
  "cci_period": 20,
  "stop_loss_percent": 5.0
}
```

### **Watchlist Setup**
```
AAPL,MSFT,GOOGL,TSLA,AMZN,META,NVDA,SPY,QQQ
```

---

## 🔧 **API Endpoints**

### **Account & Trading**
- `GET /api/account` - Account information
- `GET /api/positions` - Current positions
- `GET /api/orders` - Order history
- `POST /api/orders` - Place new order

### **Strategy Management**
- `GET /api/strategies` - List strategies
- `POST /api/strategies` - Create strategy
- `DELETE /api/strategies/{name}` - Delete strategy

### **Bot Control**
- `GET /api/scheduler/status` - Bot status
- `POST /api/scheduler/start` - Start bot
- `POST /api/scheduler/stop` - Stop bot

### **Analysis**
- `GET /api/analyze/{symbol}` - Analyze symbol
- `GET /api/sentiment/{symbol}` - Get sentiment
- `GET /api/historical-data/{symbol}` - Price data

---

## 🛡️ **Safety Features**

### **Paper Trading by Default**
- Uses Alpaca paper trading environment
- No real money at risk during testing
- Same market data as live trading

### **Risk Controls**
- Position size limits
- Stop-loss protection
- Capital allocation controls
- Market hours restrictions

---

## 📞 **Support & Documentation**

### **For Issues:**
1. Check the troubleshooting section below
2. Review application logs
3. Verify API key configuration
4. Test with paper trading first

### **Logs Location:**
```bash
# View real-time logs
tail -f logs/trading_bot.log
```

---

## 🚨 **Important Notes**

⚠️ **This is a professional trading system. Always:**
- Start with paper trading
- Test strategies thoroughly
- Never risk more than you can afford to lose
- Understand the risks involved
- Consider consulting a financial advisor

---

## 🎉 **Ready to Trade!**

Your AlpaTrade Bot is fully functional and ready for use. The system includes:

✅ **Complete trading infrastructure**
✅ **Professional web dashboard**
✅ **Advanced technical analysis**
✅ **Risk management systems**
✅ **News sentiment integration**
✅ **Multiple automation modes**
✅ **Comprehensive API**

**Start with paper trading and gradually move to live trading once you're comfortable with the system!**

## Usage Guide

### Setting Up Your First Strategy

1. **Access the Dashboard**: Go to the Strategies tab
2. **Create Strategy**: Click "Add Strategy" and configure:
   - **Name**: Unique strategy identifier
   - **Automation Mode**: Choose auto/alert-only/semi-auto
   - **Capital Allocation**: % of account per trade (1-100%)
   - **Indicator Settings**: Adjust Stochastic and CCI periods
   - **Risk Management**: Set stop-loss percentage

### Configuring Watchlist

1. **Set Watchlist**: Click "Set Watchlist" button
2. **Add Symbols**: Enter comma-separated symbols (e.g., `AAPL,MSFT,GOOGL`)
3. **Save**: The bot will monitor these symbols for signals

### Understanding Signals

The bot generates signals based on:
- **Stochastic Oversold/Overbought**: K and D lines crossing thresholds
- **CCI Extremes**: Values above/below ±100
- **Volume Confirmation**: Increased trading volume
- **News Sentiment**: Positive sentiment for buy signals

### Risk Management

- **Stop Loss**: Automatic exit at configured loss percentage
- **Position Sizing**: Based on capital allocation percentage
- **Max Positions**: Limits concurrent open positions
- **Market Hours**: Only trades during market hours

## API Endpoints

### Account & Trading
- `GET /api/account` - Account information
- `GET /api/positions` - Current positions
- `GET /api/orders` - Order history
- `POST /api/orders` - Place new order
- `DELETE /api/orders/{id}` - Cancel order

### Strategy Management
- `GET /api/strategies` - List strategies
- `POST /api/strategies` - Create strategy
- `DELETE /api/strategies/{name}` - Delete strategy

### Bot Control
- `GET /api/scheduler/status` - Bot status
- `POST /api/scheduler/start` - Start bot
- `POST /api/scheduler/stop` - Stop bot
- `GET /api/pending-signals` - Pending signals
- `POST /api/pending-signals/{id}/confirm` - Confirm signal

### Analysis
- `GET /api/analyze/{symbol}` - Analyze symbol
- `GET /api/sentiment/{symbol}` - Get sentiment
- `GET /api/historical-data/{symbol}` - Price data

## Configuration Options

### Strategy Parameters

```python
{
    "name": "My Strategy",
    "automation_mode": "semi_auto",  # auto, alert_only, semi_auto
    "capital_allocation_percent": 10.0,  # 1-100%
    "max_positions": 5,

    # Stochastic Settings
    "stoch_k_period": 14,
    "stoch_d_period": 3,
    "stoch_overbought": 80.0,
    "stoch_oversold": 20.0,

    # CCI Settings
    "cci_period": 20,
    "cci_overbought": 100.0,
    "cci_oversold": -100.0,

    # Risk Management
    "stop_loss_percent": 5.0,
    "trailing_stop_percent": 3.0,

    # Timeframes
    "timeframes": "1D,1H",

    # News Filter
    "enable_news_filter": true,
    "min_sentiment_score": -0.1
}
```

## Safety Features

### Paper Trading
- **Default Configuration**: Uses Alpaca paper trading
- **No Real Money**: Test strategies safely
- **Real Market Data**: Same data as live trading

### Risk Controls
- **Position Limits**: Maximum number of concurrent positions
- **Capital Limits**: Percentage-based position sizing
- **Stop Losses**: Automatic loss protection
- **Market Hours**: Only trades during market hours

### Monitoring
- **Real-time Dashboard**: Monitor all activities
- **Logging**: Comprehensive activity logs
- **Alerts**: Email/SMS notifications (configurable)

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify Alpaca credentials in `.env`
   - Check internet connection
   - Ensure API keys have trading permissions

2. **No Signals Generated**
   - Check if market is open
   - Verify watchlist is set
   - Review strategy parameters
   - Check indicator thresholds

3. **Orders Not Executing**
   - Verify account has sufficient buying power
   - Check if symbol is tradeable
   - Review automation mode settings

### Logs

Check application logs for detailed error information:
```bash
# View logs in real-time
tail -f logs/trading_bot.log
```

## Development

### Project Structure

```
AlpaTrade/
├── app/
│   ├── api/           # API routes
│   ├── static/        # Web assets
│   ├── templates/     # HTML templates
│   ├── alpaca_client.py    # Alpaca API wrapper
│   ├── indicators.py       # Technical indicators
│   ├── strategy.py         # Trading strategies
│   ├── sentiment.py        # News sentiment analysis
│   ├── scheduler.py        # Background scheduler
│   ├── models.py           # Data models
│   ├── config.py           # Configuration
│   └── main.py             # FastAPI app
├── requirements.txt
├── .env.example
└── README.md
```

### Adding New Indicators

1. Add indicator calculation in `indicators.py`
2. Update strategy logic in `strategy.py`
3. Add configuration options in `models.py`
4. Update dashboard UI

### Custom Strategies

Create new strategy classes inheriting from base strategy:

```python
class MyCustomStrategy:
    def analyze_symbol(self, symbol, data, timeframe):
        # Your custom logic here
        return TradingSignal(...)
```

## Disclaimer

⚠️ **Important**: This software is for educational and research purposes. Trading involves substantial risk of loss. Always:

- Start with paper trading
- Test strategies thoroughly
- Never risk more than you can afford to lose
- Understand the risks involved
- Consider consulting a financial advisor

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Create an issue in the repository
4. Join our community discussions

---

**Happy Trading! 🚀📈**
# AlpaTrade-Bot
