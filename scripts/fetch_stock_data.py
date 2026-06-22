"""
Fetch stock data for memory industry leaders: SK Hynix, Samsung, Micron
Uses yfinance as fallback for Yahoo Finance data
"""
import json
import os
from datetime import datetime, timedelta
import sys

# Try to use yfinance directly, fallback to API
USE_YFINANCE = True

def fetch_yfinance_data(ticker, name):
    """Fetch stock data using yfinance library"""
    import yfinance as yf
    stock = yf.Ticker(ticker)
    # Get 6 months of history
    hist = stock.history(period="6mo")
    if hist.empty:
        return None
    
    latest = hist.iloc[-1]
    prev = hist.iloc[-2] if len(hist) > 1 else latest
    
    change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100 if prev['Close'] != 0 else 0
    
    # Build daily data points
    history_data = []
    for index, row in hist.iterrows():
        history_data.append({
            "date": index.strftime("%Y-%m-%d"),
            "close": round(row['Close'], 2),
            "open": round(row['Open'], 2),
            "high": round(row['High'], 2),
            "low": round(row['Low'], 2),
            "volume": int(row['Volume'])
        })
    
    return {
        "name": name,
        "ticker": ticker,
        "current_price": round(latest['Close'], 2),
        "previous_close": round(prev['Close'], 2),
        "change_pct": round(change_pct, 2),
        "change_amount": round(latest['Close'] - prev['Close'], 2),
        "high_52w": round(hist['High'].max(), 2),
        "low_52w": round(hist['Low'].min(), 2),
        "volume": int(latest['Volume']),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history": history_data
    }

def generate_fallback_data(name, ticker, base_price):
    """Generate realistic fallback data if API fails"""
    import random
    history = []
    price = base_price
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(180):
        date = start_date + timedelta(days=i)
        if date.weekday() >= 5:  # Skip weekends
            continue
        
        change = random.uniform(-0.03, 0.03)
        price = price * (1 + change)
        
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": round(price, 2),
            "open": round(price * (1 + random.uniform(-0.01, 0.01)), 2),
            "high": round(price * (1 + random.uniform(0, 0.02)), 2),
            "low": round(price * (1 + random.uniform(-0.02, 0)), 2),
            "volume": int(random.uniform(1000000, 50000000))
        })
    
    latest = history[-1]
    prev = history[-2] if len(history) > 1 else latest
    change_pct = ((latest['close'] - prev['close']) / prev['close']) * 100 if prev['close'] != 0 else 0
    
    return {
        "name": name,
        "ticker": ticker,
        "current_price": latest['close'],
        "previous_close": prev['close'],
        "change_pct": round(change_pct, 2),
        "change_amount": round(latest['close'] - prev['close'], 2),
        "high_52w": max(h['close'] for h in history),
        "low_52w": min(h['close'] for h in history),
        "volume": latest['volume'],
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history": history,
        "note": "Generated fallback data - real data unavailable"
    }

def main():
    stocks = [
        {"ticker": "000660.KS", "name": "SK Hynix", "base_price": 220000},  # Korean Won
        {"ticker": "005930.KS", "name": "Samsung Electronics", "base_price": 72000},
        {"ticker": "MU", "name": "Micron Technology", "base_price": 95},  # USD
    ]
    
    results = []
    
    for stock in stocks:
        try:
            print(f"Fetching data for {stock['name']} ({stock['ticker']})...")
            data = fetch_yfinance_data(stock['ticker'], stock['name'])
            if data:
                results.append(data)
                print(f"  ✓ Current: {data['current_price']} ({data['change_pct']:+.2f}%)")
            else:
                raise ValueError("Empty data")
        except Exception as e:
            print(f"  ✗ Error: {e}, using fallback")
            data = generate_fallback_data(stock['name'], stock['ticker'], stock['base_price'])
            results.append(data)
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": results
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/stock_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved stock data to data/stock_data.json")
    return output

if __name__ == "__main__":
    main()
