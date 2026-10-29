import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


@st.cache_data
def get_stock_data(ticker: str = "MSFT", period: str = "5y"):
    data = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    if data.empty:
        raise ValueError(f"No data returned for ticker: {ticker}")
    return data


def calculate_moving_averages(data: pd.DataFrame, short_window: int = 50, long_window: int = 200):
    result = data.copy()
    result["MA50"] = result["Close"].rolling(window=short_window).mean()
    result["MA200"] = result["Close"].rolling(window=long_window).mean()
    return result


def implement_strategy(data: pd.DataFrame, holding_days: int = 60, profit_target: float = 0.15):
    positions = []
    in_position = False
    buy_price = 0.0
    buy_date = None

    for date, row in data.iterrows():
        ma50 = row.get("MA50")
        ma200 = row.get("MA200")

        if pd.isna(ma50) or pd.isna(ma200):
            continue

        if not in_position and ma50 > ma200:
            in_position = True
            buy_price = float(row["Close"])
            buy_date = date
            positions.append(
                {
                    "BuyDate": buy_date,
                    "BuyPrice": buy_price,
                    "SellDate": None,
                    "SellPrice": None,
                    "Profit": None,
                    "Reason": None,
                }
            )
        elif in_position:
            current_price = float(row["Close"])
            days_held = (date - buy_date).days
            profit_pct = (current_price - buy_price) / buy_price

            if profit_pct >= profit_target or days_held >= holding_days:
                in_position = False
                positions[-1]["SellDate"] = date
                positions[-1]["SellPrice"] = current_price
                positions[-1]["Profit"] = round((current_price - buy_price) * 100, 2)
                positions[-1]["Reason"] = (
                    "Profit Target" if profit_pct >= profit_target else "Max Holding Period"
                )

    return pd.DataFrame(positions)


st.set_page_config(page_title="MSFT Trading App", layout="wide")
st.title("MSFT Price Chart with Moving Averages and Trades")

try:
    df = get_stock_data("MSFT", "5y")
    df = calculate_moving_averages(df)
    trades = implement_strategy(df)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df.index, df["Close"], label="Close Price", alpha=0.5, color="gray")
ax.plot(df.index, df["MA50"], label="MA50", color="blue", linewidth=1.5)
ax.plot(df.index, df["MA200"], label="MA200", color="red", linewidth=1.5)

if not trades.empty:
    ax.scatter(trades["BuyDate"], trades["BuyPrice"], marker="^", color="green", s=80, label="Buy Point", zorder=5)
    sell_trades = trades.dropna(subset=["SellDate"])
    if not sell_trades.empty:
        ax.scatter(sell_trades["SellDate"], sell_trades["SellPrice"], marker="v", color="red", s=80, label="Sell Point", zorder=5)

ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.subheader("Detailed Trades")
if trades.empty:
    st.info("No trades were generated for the selected period.")
else:
    st.dataframe(trades, use_container_width=True)
