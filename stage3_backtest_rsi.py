import requests
import pandas as pd
from ta.momentum import RSIIndicator

# === CONFIGURATION ===
API_KEY = "e653825ad0bc447ea72f5596b702decd"
SYMBOL = "EUR/USD"
INTERVAL = "1min"
INITIAL_BALANCE = 10000  # Starting capital in USD
BASE_URL = "https://api.twelvedata.com/time_series"


def get_historical_data(symbol, interval, count=500):
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": count
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    if "values" not in data:
        print("[ERROR]", data)
        return None
    df = pd.DataFrame(data["values"])
    df = df.astype({"open": "float", "high": "float", "low": "float", "close": "float"})
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime", inplace=True)
    return df


def calculate_rsi(df, period=14):
    rsi = RSIIndicator(close=df["close"], window=period)
    df["rsi"] = rsi.rsi()
    return df


def generate_signals(df):
    signals = []
    for i in range(len(df)):
        if df.loc[i, "rsi"] <= 30:
            signals.append("BUY")
        elif df.loc[i, "rsi"] >= 70:
            signals.append("SELL")
        else:
            signals.append("HOLD")
    df["signal"] = signals
    return df


def backtest(df, initial_balance):
    balance = initial_balance
    position = None
    entry_price = 0.0
    trades = []

    for i in range(1, len(df)):
        signal = df.loc[i, "signal"]
        price = df.loc[i, "close"]

        # Open position
        if signal == "BUY" and position is None:
            position = "LONG"
            entry_price = price
            trades.append((df.loc[i, "datetime"], "BUY", price))

        elif signal == "SELL" and position == "LONG":
            # Close long
            profit = (price - entry_price) * 10000 / entry_price  # approx pips value
            balance += profit
            trades.append((df.loc[i, "datetime"], "SELL", price, round(profit, 2)))
            position = None

    final_profit = balance - initial_balance
    profit_percent = (final_profit / initial_balance) * 100
    return trades, balance, profit_percent


# === RUN BACKTEST ===
print(f"[START] Backtesting RSI Strategy for {SYMBOL} ({INTERVAL})")
df = get_historical_data(SYMBOL, INTERVAL)
if df is None:
    exit()

df = calculate_rsi(df)
df = generate_signals(df)
trades, final_balance, profit_percent = backtest(df, INITIAL_BALANCE)

print(f"\n=== RESULTS ===")
print(f"Initial Balance: ${INITIAL_BALANCE}")
print(f"Final Balance:   ${final_balance:.2f}")
print(f"Net Profit:      {profit_percent:.2f}%")
print(f"Total Trades:    {len(trades)}\n")

print("Recent Trades:")
for t in trades[-5:]:
    print(t)
