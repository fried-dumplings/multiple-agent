from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from web.api.router import api_router
from web.lifespan import lifespan_setup


def app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(title="multiple_agent", lifespan=lifespan_setup)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
