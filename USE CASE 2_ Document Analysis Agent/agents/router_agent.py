from agents.base import MCPMessage, Agent

class RouterAgent(Agent):
    def __init__(self, name, knowledge_agent, rag_bot, finance_agent):
        super().__init__(name)
        self.knowledge_agent = knowledge_agent
        self.rag_bot = rag_bot
        self.finance_agent = finance_agent

    async def route(self, message: MCPMessage):
        command = message.command
        payload = message.payload
        query = payload.get("query", "").lower()

        if command == "upload_document":
            forward_msg = MCPMessage(
                sender=self.name,
                receiver=self.knowledge_agent.name,
                command="store_document",
                payload=payload
            )
            return await self.send(self.knowledge_agent, forward_msg)
        
        elif command == "user_query":
            forward_msg = MCPMessage(
            sender=self.name,
            receiver=self.rag_bot.name,
            command="query",
            payload=payload
            )
            return await self.send(self.rag_bot, forward_msg)
        
        elif command == "generate_report":
            forward_msg = MCPMessage(
            sender=self.name,
            receiver=self.finance_agent.name,
            command="generate_report",
            payload=payload
            )
            return await self.send(self.finance_agent, forward_msg)
 
        else:
            return {"error": f"Unrecognized command: {command}"}
