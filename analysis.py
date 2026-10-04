from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

ASSETS = {
    "XAUUSD": {"name": "الذهب", "ticker": "GC=F"},
    "EURUSD": {"name": "EUR/USD", "ticker": "EURUSD=X"},
    "GBPUSD": {"name": "GBP/USD", "ticker": "GBPUSD=X"},
    "USDJPY": {"name": "USD/JPY", "ticker": "JPY=X"},
    "AUDUSD": {"name": "AUD/USD", "ticker": "AUDUSD=X"},
}

TIMEFRAME_MAP = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "1h",
    "1d": "1d",
}


def safe_round(value, digits=2):
    try:
        return round(float(value), digits)
    except Exception:
        return 0.0


def compute_rsi(series, period=14):
    series = pd.Series(series).astype(float)
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    last = rsi.iloc[-1]
    return float(last) if not np.isnan(last) else 50.0


def get_market_snapshot(symbol="XAUUSD", timeframe="1h"):
    symbol = (symbol or "XAUUSD").upper()
    timeframe = (timeframe or "1h").lower()

    if symbol not in ASSETS:
        symbol = "XAUUSD"

    if timeframe not in TIMEFRAME_MAP:
        timeframe = "1h"

    asset = ASSETS[symbol]
    ticker = asset["ticker"]
    interval = TIMEFRAME_MAP[timeframe]

    hist = yf.Ticker(ticker).history(period="5d", interval=interval, auto_adjust=True)

    if hist is None or hist.empty:
        raise ValueError(f"لا توجد بيانات حقيقية لـ {symbol}")

    hist = hist.dropna()
    closes = hist["Close"].astype(float)

    if len(closes) < 2:
        raise ValueError(f"بيانات {symbol} غير كافية")

    last_price = float(closes.iloc[-1])
    prev_price = float(closes.iloc[-2])
    change_pct = ((last_price - prev_price) / prev_price) * 100 if prev_price else 0.0

    rsi = compute_rsi(closes, 14)
    ma_fast = float(closes.rolling(10).mean().iloc[-1])
    ma_slow = float(closes.rolling(30).mean().iloc[-1])

    if rsi < 38 and ma_fast >= ma_slow:
        signal = "BUY"
        trend = "صاعد"
    elif rsi > 62 and ma_fast <= ma_slow:
        signal = "SELL"
        trend = "هابط"
    else:
        signal = "WAIT"
        trend = "متذبذب / غير واضح"

    confidence = 85 if signal in ("BUY", "SELL") else 62

    volatility = float(closes.pct_change().abs().mean() * 100)
    spread = volatility * 0.15 + 0.0001

    if signal == "BUY":
        entry = last_price
        sl = last_price - (spread * 1.8)
        tp1 = last_price + (spread * 2.5)
        tp2 = last_price + (spread * 4.0)
    elif signal == "SELL":
        entry = last_price
        sl = last_price + (spread * 1.8)
        tp1 = last_price - (spread * 2.5)
        tp2 = last_price - (spread * 4.0)
    else:
        entry = last_price
        sl = last_price
        tp1 = last_price
        tp2 = last_price

    decimals = 2 if symbol in ("XAUUSD", "USDJPY") else 5

    return {
        "symbol": symbol,
        "asset": asset["name"],
        "timeframe": timeframe,
        "price": safe_round(last_price, decimals),
        "change": safe_round(change_pct, 2),
        "signal": signal,
        "confidence": confidence,
        "trend": trend,
        "rsi": safe_round(rsi, 1),
        "plan": {
            "entry": safe_round(entry, decimals),
            "sl": safe_round(sl, decimals),
            "tp1": safe_round(tp1, decimals),
            "tp2": safe_round(tp2, decimals),
        },
        "indicators": [
            f"RSI: {safe_round(rsi, 1)}",
            f"المتوسط السريع: {safe_round(ma_fast, decimals)}",
            f"المتوسط البطيء: {safe_round(ma_slow, decimals)}",
            f"الفريم: {timeframe}",
            f"التقلب: {safe_round(volatility, 3)}%",
        ],
        "summary": (
            f"تحليل حقيقي لـ {asset['name']} على فريم {timeframe}. "
            f"السعر الحالي {safe_round(last_price, decimals)}، "
            f"الإشارة الحالية {signal} بثقة تقديرية {confidence}%. "
            "البيانات مأخوذة مباشرة من السوق عبر Yahoo Finance."
        ),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def analyze_market(symbol="XAUUSD", timeframe="1h"):
    return get_market_snapshot(symbol=symbol, timeframe=timeframe)
