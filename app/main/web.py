from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .di import init_dependencies
from .routers import init_routers


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_routers(app)
    init_dependencies(app)
    return app
