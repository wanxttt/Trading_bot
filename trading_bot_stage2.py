import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator

# === CONFIGURATION ===
API_KEY = "e653825ad0bc447ea72f5596b702decd"
SYMBOL = "EUR/USD"
INTERVAL = "1min"
BASE_URL = "https://api.twelvedata.com/time_series"

def get_candles(symbol, interval, count=100):
    """Fetch last N candles from Twelve Data."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": count,
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    if "values" not in data:
        print("[ERROR]", data)
        return None
    df = pd.DataFrame(data["values"])
    df = df.astype({"open":"float","high":"float","low":"float","close":"float"})
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime", inplace=True)   # Oldest → newest
    return df

def get_latest_candle(symbol, interval):
    """Fetch latest single candle."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": 1
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    if "values" not in data:
        print("[ERROR]", data)
        return None, None
    c = data["values"][0]
    return c["datetime"], float(c["close"])

def calculate_rsi(df, period=14):
    rsi = RSIIndicator(close=df["close"], window=period)
    df["rsi"] = rsi.rsi()
    return df

def get_signal(latest_rsi):
    if latest_rsi <= 30:
        return "BUY"
    elif latest_rsi >= 70:
        return "SELL"
    else:
        return "NO_SIGNAL"

# === MAIN LOOP ===
print(f"[START] RSI Tracker for {SYMBOL} ({INTERVAL})")

df = get_candles(SYMBOL, INTERVAL)
if df is None:
    exit()

df = calculate_rsi(df)
last_time = df.iloc[-1]["datetime"]
print(f"[INIT] Latest candle {last_time}, RSI={df.iloc[-1]['rsi']:.2f}")

while True:
    time.sleep(10)
    new_time, new_close = get_latest_candle(SYMBOL, INTERVAL)
    if new_time and pd.to_datetime(new_time) != last_time:
        # fetch full data again for fresh RSI
        df = get_candles(SYMBOL, INTERVAL)
        df = calculate_rsi(df)
        latest_rsi = df.iloc[-1]["rsi"]
        signal = get_signal(latest_rsi)
        print(f"[NEW CANDLE] {new_time} | Close={new_close:.5f} | RSI={latest_rsi:.2f} | Signal={signal}")
        last_time = pd.to_datetime(new_time)
    else:
        print(f"[WAIT] No new candle yet (latest {last_time})")
