from flask import Flask, jsonify, request, render_template

from analysis import analyze_market
from db import init_db, seed_positions

app = Flask(__name__, template_folder="templates", static_folder="static")

init_db()
seed_positions()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "go-os-real-market"})


@app.get("/api/analyze")
def api_analyze():
    symbol = request.args.get("symbol", "XAUUSD").upper()
    timeframe = request.args.get("timeframe", "1h").lower()

    try:
        data = analyze_market(symbol, timeframe)

        import sqlite3

        conn = sqlite3.connect("forex.db")
        conn.execute(
            "INSERT INTO signals (symbol, timeframe, signal, confidence) VALUES (?, ?, ?, ?)",
            (symbol, timeframe, data["signal"], data["confidence"]),
        )
        conn.commit()
        conn.close()

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/positions")
def api_positions():
    import sqlite3

    conn = sqlite3.connect("forex.db")
    rows = conn.execute("SELECT * FROM positions ORDER BY id DESC").fetchall()
    conn.close()

    return jsonify(
        {
            "positions": [
                {
                    "id": r[0],
                    "symbol": r[1],
                    "side": r[2],
                    "entry": r[3],
                    "stop": r[4],
                    "target": r[5],
                    "status": r[6],
                }
                for r in rows
            ]
        }
    )


@app.post("/api/chat")
def api_chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    symbol = (payload.get("symbol") or "XAUUSD").upper()

    if not message:
        return jsonify({"reply": "اكتب سؤالاً أو اطلب تفسيراً للسوق."})

    msg = message.lower()
    if "شراء" in msg or "buy" in msg:
        reply = f"إشارة شراء محتملة على {symbol}. راجع الاتجاه والفريم ورأس المال قبل الدخول."
    elif "بيع" in msg or "sell" in msg:
        reply = f"إشارة بيع محتملة على {symbol}. تأكد من مقاومة السعر ووقف الخسارة قبل التنفيذ."
    elif "مخاطرة" in msg or "risk" in msg:
        reply = "إدارة المخاطر: لا تتجاوز 1-2% من رأس المال لكل صفقة، ويفضل استخدام Stop Loss واضح."
    elif "اتجاه" in msg or "trend" in msg:
        reply = f"اتجاه {symbol} يعتمد على السعر، المتوسط المتحرك، وRSI، وليس على مجرد حركة سريعة."
    else:
        reply = f"لـ {symbol} نوصي بمراجعة الاتجاه، التقلب، وقيمة RSI قبل اتخاذ القرار."

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
