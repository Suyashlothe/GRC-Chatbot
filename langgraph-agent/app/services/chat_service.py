from app.sql.sql_agent import sql_agent


class ChatService:

    async def process_message(self, message: str):
        return await sql_agent.run(message)