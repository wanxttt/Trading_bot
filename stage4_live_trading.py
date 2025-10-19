import time
import os
import requests
import pandas as pd
from ta.momentum import RSIIndicator

# === CONFIG ===
API_KEY = "e653825ad0bc447ea72f5596b702decd"
SYMBOL = "EUR/USD"
INTERVAL = "1min"
BASE_URL = "https://api.twelvedata.com/time_series"

BALANCE = 10000.0
POSITION = None
ENTRY_PRICE = 0.0
BASE_TRADE_SIZE = 10000
multiplier = 1
MAX_MULTIPLIER = 3

# === DASHBOARD STATS ===
total_trades = 0
wins = 0
losses = 0
total_profit = 0.0
last_signal = "HOLD"
last_rsi = 0.0
last_close = 0.0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_candles(symbol, interval, count=100):
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
    df = df.astype({"open":"float","high":"float","low":"float","close":"float"})
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime", inplace=True)
    return df

def calc_rsi(df, period=14):
    rsi = RSIIndicator(close=df["close"], window=period)
    df["rsi"] = rsi.rsi()
    return df

def get_signal(rsi):
    if rsi <= 30:
        return "BUY"
    elif rsi >= 70:
        return "SELL"
    return "HOLD"

def print_dashboard():
    clear_screen()
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_profit = (total_profit / total_trades) if total_trades > 0 else 0

    print("╔══════════════════════════════════════════════════════╗")
    print("║              💹 LIVE FOREX TRADING BOT               ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"  Symbol: {SYMBOL} ({INTERVAL})")
    print(f"  Last Candle: {last_close:.5f} | RSI: {last_rsi:.2f} | Signal: {last_signal}")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"  Balance      : ${BALANCE:.2f}")
    print(f"  Total Trades : {total_trades}")
    print(f"  Wins / Losses: {wins} / {losses}")
    print(f"  Win Rate     : {win_rate:.2f}%")
    print(f"  Avg Profit   : ${avg_profit:.2f}")
    print(f"  Trade Size   : {BASE_TRADE_SIZE * multiplier} units ({multiplier}x)")
    print("╚══════════════════════════════════════════════════════╝")
    if POSITION:
        print(f"📈 Currently holding {POSITION} from {ENTRY_PRICE:.5f}")
    else:
        print("💤 Waiting for trade signal...")

print(f"[START] Paper-Trading RSI bot for {SYMBOL} ({INTERVAL})")

df = get_candles(SYMBOL, INTERVAL)
df = calc_rsi(df)
last_time = df.iloc[-1]["datetime"]
print(f"[INIT] Latest candle {last_time}, RSI={df.iloc[-1]['rsi']:.2f}")

while True:
    time.sleep(10)
    new_df = get_candles(SYMBOL, INTERVAL, count=30)
    if new_df is None:
        continue
    new_df = calc_rsi(new_df)
    new_time = new_df.iloc[-1]["datetime"]
    new_close = new_df.iloc[-1]["close"]
    rsi_value = new_df.iloc[-1]["rsi"]
    signal = get_signal(rsi_value)

    if new_time != last_time:
        last_signal = signal
        last_rsi = rsi_value
        last_close = new_close

        TRADE_SIZE = BASE_TRADE_SIZE * multiplier

        if signal == "BUY" and POSITION is None:
            POSITION = "LONG"
            ENTRY_PRICE = new_close

        elif signal == "SELL" and POSITION == "LONG":
            profit = (new_close - ENTRY_PRICE) * TRADE_SIZE / ENTRY_PRICE
            BALANCE += profit
            total_trades += 1
            total_profit += profit

            if profit > 0:
                wins += 1
                multiplier = 1
            else:
                losses += 1
                multiplier = min(multiplier * 2, MAX_MULTIPLIER)

            POSITION = None
            ENTRY_PRICE = 0.0

        print_dashboard()
        last_time = new_time
    else:
        print_dashboard()
