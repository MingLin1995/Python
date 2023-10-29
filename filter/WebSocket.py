import websocket
import json


url = "wss://fstream.binance.com/ws/btcusdt@trade"  # BTCＵ本位合約交易，p為當下價格


def on_message(ws, message):
    print("確定收到合約交易資訊:")
    print(ws)
    data = json.loads(message)
    print(data)


# 建立WebSocket連接
ws = websocket.WebSocketApp(url, on_message=on_message)


# 啟動WebSocket連接
ws.run_forever()
