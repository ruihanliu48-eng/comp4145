import streamlit as st
import matplotlib.pyplot as plt
import trading_strategy as ts

st.set_page_config(page_title="MSFT Trading App", layout="wide")
st.title("MSFT Price Chart with Moving Averages and Trades")

# 获取老师代码算出来的交易记录
trades = ts.positions 

# 获取图表数据（为了画线，我们再调一下老师的函数）
df = ts.get_stock_data("MSFT")
df = ts.calculate_moving_averages(df)

# 绘制图表
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df.index, df['Close'], label='Close Price', alpha=0.5, color='gray')
ax.plot(df.index, df['MA50'], label='MA50', color='blue', linewidth=1.5)
ax.plot(df.index, df['MA200'], label='MA200', color='red', linewidth=1.5)

if not trades.empty:
    ax.scatter(trades['BuyDate'], trades['BuyPrice'], marker='^', color='green', s=80, label='Buy Point', zorder=5)
    sell_trades = trades.dropna(subset=['SellDate'])
    if not sell_trades.empty:
        ax.scatter(sell_trades['SellDate'], sell_trades['SellPrice'], marker='v', color='red', s=80, label='Sell Point', zorder=5)

ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.subheader("Detailed Trades")
st.dataframe(trades, use_container_width=True)