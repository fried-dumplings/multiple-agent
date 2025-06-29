from fastapi import APIRouter
from llm.openai_cli import OpenAIClient

router = APIRouter()


@router.get("/health")
async def health_check() -> None:
    client =  OpenAIClient()
    await client.achat()
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """
    return "no"