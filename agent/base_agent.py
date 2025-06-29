from llm.openai_cli import Message, OpenAIClient




class BaseAgent:
    def __init__(self, prompt: str | None):
        self.messages = []
        if prompt is not None:
            self.messages.append(Message(role="system", content=prompt))
        self.client = OpenAIClient()

    async def input(self, input: str):
        res = await self.client.achat(self.messages)
        # res..
        pass

    async def callMCP():
      pass

    async def output(self):
        pass
