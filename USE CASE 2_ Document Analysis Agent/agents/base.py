import json
from datetime import datetime

class MCPMessage:
    def __init__(self, sender, receiver, command, payload, status="pending"):
        self.sender = sender
        self.receiver = receiver
        self.command = command
        self.payload = payload
        self.status = status
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "command": self.command,
            "payload": self.payload,
            "status": self.status,
            "timestamp": self.timestamp,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


class Agent:
    def __init__(self, name):
        self.name = name

    async def handle(self, message: MCPMessage):
        return await self.route(message)

    async def send(self, to_agent, message: MCPMessage):
        return await to_agent.handle(message)

    async def route(self, message: MCPMessage):
        raise NotImplementedError("Each agent must implement route().")
