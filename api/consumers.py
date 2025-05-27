import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("caseflow", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("caseflow", self.channel_name)

    async def activeclaim(self, event):
        await self.send(text_data=json.dumps(event))
