# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alert_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("alert_group", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Process incoming data if necessary

    # Handler for sending alert messages to the frontend
    async def alert_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
