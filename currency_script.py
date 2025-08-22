import yfinance as yf
import requests
import datetime

# =========================================
# 🔹 Telegram bot setup
# =========================================
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GROUP_ID = os.getenv("GROUP_ID")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    requests.post(url, data={"chat_id": GROUP_ID, "text": message})

# =========================================
# 🔹 Currency pairs to monitor
# =========================================
pairs = {
    "MYR to JPY": "MYRJPY=X",
    "MYR to AUD": "MYRAUD=X",
    "MYR to CNY": "MYRCNY=X",
    "MYR to SGD": "MYRSGD=X",
    "MYR to USD": "MYRUSD=X",
    "MYR to TWD": "MYRTWD=X"
}

# =========================================
# 🔹 Function to check currencies
# =========================================

def check_currency():
    messages = []  # collect all currency alerts here
    today = datetime.date.today().strftime("%Y-%m-%d")  # current date

    for name, ticker_symbol in pairs.items():
        ticker = yf.Ticker(ticker_symbol)

        # Get last 1 month of daily data
        data = ticker.history(period="1mo", interval="1d")

        if not data.empty and len(data) >= 2:
            latest_price = data['Close'].iloc[-1]
            prev_price   = data['Close'].iloc[-2]  # yesterday
            monthly_avg  = data['Close'].mean()

            high_threshold = monthly_avg * 1.025  # +2.5%
            low_threshold  = monthly_avg * 0.975  # -2.5%

            # Determine monthly status
            if latest_price >= high_threshold:
                status = "🚨 HIGH 🚀"
            elif latest_price <= low_threshold:
                status = "🚨 LOW 📉"
            else:
                status = "Stable"

            # Compare with yesterday
            if latest_price > prev_price:
                day_change = f"⬆️ +{(latest_price - prev_price):.4f}"
            elif latest_price < prev_price:
                day_change = f"⬇️ {(latest_price - prev_price):.4f}"
            else:
                day_change = "➡️ No change"

            # Compare with monthly average
            diff_from_avg = latest_price - monthly_avg
            perc_from_avg = (diff_from_avg / monthly_avg) * 100
            if diff_from_avg > 0:
                avg_change = f"⬆️ +{diff_from_avg:.4f} ({perc_from_avg:.2f}%)"
            elif diff_from_avg < 0:
                avg_change = f"⬇️ {diff_from_avg:.4f} ({perc_from_avg:.2f}%)"
            else:
                avg_change = "➡️ At monthly avg"

            messages.append(
                f"{name}\n"
                f"Type: {status}\n"
                f"Latest: {latest_price:.4f}  |  Avg: {monthly_avg:.4f}\n"
                f"Change\n"
                f"vs Yesterday: {day_change}\n"
                f"vs Monthly Avg: {avg_change}"
            )

    # 🔹 Send everything in one message
    if messages:
        final_message = f"📊 Currency Alert Update: \n{today}\n\n" + "\n\n".join(messages)
        send_telegram(final_message)

# =========================================
# 🔹 Run the check
# =========================================
check_currency()
