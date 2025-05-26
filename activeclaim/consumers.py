import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("cases", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("cases", self.channel_name)

    async def case_update(self, event):
        await self.send(text_data=json.dumps(event))
