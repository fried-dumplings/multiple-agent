from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
)
from pydantic import BaseModel
from typing import Optional

# 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

# class Message(BaseModel, ChatCompletionMessageParam):
#     reasoning: Optional[str] = None

class OpenAIClient:
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash", # deepseek-chat
        # model_name: str = "deepseek-reasoner",
        # model_name: str = "deepseek-chat",
        # model_name: str = "qwen3:8b",
        # model_name: str = "deepseek-r1:8b",
        # model_name: str = "deepseek-r1:14b",
        # model_name: str = "qwen/qwen3-235b-a22b:free",
        max_tokens: int = 4 * 1024,
        temperature: float = 0.8,
    ):
        self.client = AsyncOpenAI(
            api_key="AIzaSyDesxyb0ruLlkHSo7e0OjVy83kPZM9eXd4", # google key
            # api_key="sk-1b61205135ff412180b78142fda8fcfa", # deepseek key
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            # base_url="https://api.deepseek.com",
            # base_url="http://localhost:11434/v1/",
            # api_key="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", # openrouter key
            # base_url="https://openrouter.ai/api/v1",
        )
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.temperature = temperature

    async def achat(
        self, messages: list[ChatCompletionMessageParam]
    ) -> ChatCompletionMessage:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=messages,
            # response_format={"type": "json_object"},
        )
        # print(f"response: {response}")
        return response.choices[0].message

    async def astream(self, messages: list[ChatCompletionMessageParam]):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
