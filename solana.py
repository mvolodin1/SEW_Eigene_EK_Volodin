import time
import requests
from collections import deque

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "SOLUSDT"

CHECK_INTERVAL_SECONDS = 5   
WINDOW_SECONDS = 5 * 60     
THRESHOLD_PERCENT = 2.0        

TELEGRAM_TOKEN = "8402984439:AAFIm1az94sC1Ou5gz4dn9EuJ612nmfckpA"
TELEGRAM_CHAT_ID = "1327081785"

price_history = deque()

def get_solana_price_usd():
    resp = requests.get(BINANCE_URL, params={"symbol": SYMBOL}, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return float(data["price"])

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload, timeout=5)


def main():
    print("Starte Solana-Price-Watcher (Binance)...")
    

    while True:
        try:
            now = time.time()
            price = get_solana_price_usd()
            print(f"Aktueller SOL-Preis: {price:.2f} USD")

            price_history.append((now, price))

          
            while price_history and now - price_history[0][0] > WINDOW_SECONDS:
                price_history.popleft()

      
            if price_history and (now - price_history[0][0]) >= WINDOW_SECONDS:
                old_time, old_price = price_history[0]
                change_percent = (price - old_price) / old_price * 100

                if abs(change_percent) >= THRESHOLD_PERCENT:
                    direction = "gestiegen" if change_percent > 0 else "gefallen"
                    msg = (
                        f"Solana-Alarm!\n"
                        f"Preis in 5 Minuten um {change_percent:.2f}% {direction}\n"
                        f"Aktueller Preis: {price:.2f} USD"
                    )
                    print(msg)
                    send_telegram_message(msg)

          
                    time.sleep(60)

            time.sleep(CHECK_INTERVAL_SECONDS)

        except Exception as e:
            print("Fehler:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
