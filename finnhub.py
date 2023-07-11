#https://pypi.org/project/websocket_client/
import websocket
import json
from kafka import KafkaProducer

hostname='10.148.0.8'
port='9092'
topic_name='forex'

producer = KafkaProducer(
    bootstrap_servers=hostname + ":" + port,
    value_serializer=lambda v: json.dumps(v).encode('ascii')
)

def process_trade_data(data):
    trades = json.loads(data)['data']
    for trade in trades:
        symbol = trade['s']
        price = trade['p']
        timestamp = trade['t']
        volume = trade['v']
        
        # Process the trade data as per your requirements
        # For example, you can print the values or store them in a data structure
    
        print(f"Symbol: {symbol}")
        print(f"Price: {price}")
        print(f"Timestamp: {timestamp}")
        print(f"Volume: {volume}")
        print("------------------")

def on_message(ws,message):
    print("++Rcv raw:", message)
    decoded_message = websocket._app_data_masker(message)
    print("++Rcv decoded:", decoded_message)
    
    # Process the received trade data
    process_trade_data(message)

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
