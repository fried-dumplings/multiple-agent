from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Optional
# 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


class Message(BaseModel):
    role: str
    content: str
    reasoning: Optional[str] = None


class OpenAIClient:
    def __init__(
        self,
        model_name: str = "qwen/qwen3-235b-a22b:free",
        max_tokens: int = 4 * 1024,
        temperature: float = 0.8,
    ):
        self.client = AsyncOpenAI(
            api_key="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",
            base_url="https://openrouter.ai/api/v1",
        )
        self.model_name = model_name
        self.temperature = temperature

    async def achat(self, messages: list[Message]):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[m.dict(exclude={"reasoning"}) for m in messages],
        )
        return response.choices[0].message.content

    async def astream(self, messages: list[Message]):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[m.dict(exclude={"reasoning"}) for m in messages],
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
