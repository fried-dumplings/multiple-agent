from llm.openai_cli import Message, OpenAIClient




class BaseAgent:
    async def __init__(self, prompt: str | None):
        self.messages = []
        mcp_tools = await self.get_mcp_tools()
        if prompt is not None:
            system_prompt = f"{prompt}/n{mcp_tools}"
            self.messages.append(Message(role="system", content=prompt))
        else
            self.messages.append(Message(role="system", content=mcp_tools))
        self.client = OpenAIClient()

    async def input(self, content: str):
        self.messages.append(Message(role="user", content=content))
        result = await self.client.astream(self.messages)
        

        # self.messages.append(Message(role="assistant", content=content))



    async def get_mcp_tools(self) -> str:
        pass


    async def output(self):
         
