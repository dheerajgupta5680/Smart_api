# angel_websocket.py
import websocket
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def on_message(ws, message):
    data = json.loads(message)
    # Assuming data contains the token and last traded price (LTP)
    token = data['token']
    ltp = data['last_traded_price']
    check_alert_condition(token, ltp)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws, alert_details):
    # Subscribe to the token provided in alert_details
    ws.send(json.dumps({'action': 'subscribe', 'token': alert_details['token']}))

def start_angelone_websocket(alert_details):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://angelone.example.com/socket",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = lambda ws: on_open(ws, alert_details)
    ws.run_forever()

def check_alert_condition(token, ltp):
    # Here, include logic to check if the ltp matches the alert condition
    # If matched, send a message to the frontend
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "alert_group",  # This group name should match the group name used in AlertConsumer
        {
            "type": "alert.message",
            "message": f"{token} reached the target price: {ltp}"
        }
    )
    # Assuming you have logic here to close the WebSocket if the condition is met
