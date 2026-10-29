import pandas as pd
import numpy as np

def load_data(symbol="MSFT", file_path="stock_data.csv"):
    # 读取本地 CSV，筛选股票
    df = pd.read_csv(file_path)
    df = df[df['Symbol'] == symbol].copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def calculate_moving_averages(data, short_window=50, long_window=200):
    # 计算均线
    data['MA50'] = data['Close'].rolling(window=short_window).mean()
    data['MA200'] = data['Close'].rolling(window=long_window).mean()
    return data

def implement_strategy(data, holding_days=60, profit_target=0.15):
    positions = []
    in_position = False
    buy_price = 0
    buy_date = None

    for i in range(len(data)):
        date = data.index[i]
        row = data.iloc[i]
        ma50, ma200 = row['MA50'], row['MA200']
        
        if pd.isna(ma50) or pd.isna(ma200):
            continue

        # 金叉买入
        if not in_position and ma50 > ma200:
            in_position = True
            buy_price = row['Close']
            buy_date = date
            positions.append({
                'BuyDate': buy_date, 'BuyPrice': buy_price, 
                'SellDate': None, 'SellPrice': None, 'Profit': None, 'Reason': None
            })
            
        # 止盈或到期卖出
        elif in_position:
            days_held = (date - buy_date).days
            current_price = row['Close']
            profit_pct = (current_price - buy_price) / buy_price

            if profit_pct >= profit_target or days_held >= holding_days:
                in_position = False
                positions[-1]['SellDate'] = date
                positions[-1]['SellPrice'] = current_price
                positions[-1]['Profit'] = round((current_price - buy_price) * 100, 2)
                positions[-1]['Reason'] = 'Profit Target' if profit_pct >= profit_target else 'Max Holding Period'

    return pd.DataFrame(positions)

def analyze_results(trades_df):
    if trades_df.empty:
        return {"Total Trades": 0, "Win Rate": "0%", "Total Return": "0%"}

    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['SellPrice'] > trades_df['BuyPrice']])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    
    total_return = 1.0
    for _, row in trades_df.iterrows():
        if row['SellPrice'] is not None:
            total_return *= (row['SellPrice'] / row['BuyPrice'])
    
    return {
        "Total Trades": total_trades,
        "Win Rate": f"{win_rate:.2f}%",
        "Total Return": f"{(total_return - 1) * 100:.2f}%",
        "Winning Trades": winning_trades,
        "Losing Trades": total_trades - winning_trades
    }

def main(symbol="MSFT"):
    df = load_data(symbol)
    if df.empty:
        return None, None, None
    df = calculate_moving_averages(df)
    trades = implement_strategy(df)
    stats = analyze_results(trades)
    return trades, stats, df