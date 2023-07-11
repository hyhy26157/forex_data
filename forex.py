#https://pypi.org/project/websocket_client/
import websocket

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"OANDA:AUD_CAD"}')
    ws.send('{"type":"subscribe","symbol":"OANDA:EUR_GBP"}')
    ws.send('{"type":"subscribe","symbol":"OANDA:AUD_NZD"}')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=cemknc2ad3ieeugka97gcemknc2ad3ieeugka980",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()