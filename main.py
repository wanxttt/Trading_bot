import time
import requests
import pandas as pd

#  CONFIGURATION
API_KEY = "e653825ad0bc447ea72f5596b702decd"
SYMBOL = "EUR/USD"
INTERVAL = "1min"

# Twelve Data endpoint
BASE_URL = "https://api.twelvedata.com/time_series"

def get_latest_candle(symbol, interval):
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": 1
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "values" not in data:
        print("[ERROR]", data)
        return None, None

    candle = data["values"][0]
    time_stamp = candle["datetime"]
    close_price = float(candle["close"])
    return time_stamp, close_price


# MAIN LOOP
print(f"[START] Tracking {SYMBOL} candles ({INTERVAL})")

last_time, last_close = get_latest_candle(SYMBOL, INTERVAL)
if not last_time:
    print("Failed to fetch initial candle.")
    exit()

print(f"[INIT] Latest candle {last_time}, close={last_close}")

while True:
    time.sleep(10)
    new_time, new_close = get_latest_candle(SYMBOL, INTERVAL)

    if new_time and new_time != last_time:
        print(f"[NEW CANDLE] Time={new_time}, Close={new_close}")
        last_time = new_time
    else:
        print(f"[WAIT] No new candle yet (latest {last_time})")
