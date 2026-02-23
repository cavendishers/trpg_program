from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import character, game, scenario, session


def create_app() -> FastAPI:
    app = FastAPI(title="AI TRPG", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(scenario.router)
    app.include_router(character.router)
    app.include_router(session.router)
    app.include_router(game.router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/api/saves")
    async def list_all_saves():
        from backend.core.game_engine import GameEngine
        return {"saves": GameEngine.list_all_saves()}

    @app.delete("/api/saves/{filename}")
    async def delete_save(filename: str):
        from backend.core.game_engine import SAVES_DIR
        from fastapi import HTTPException
        path = SAVES_DIR / filename
        if not path.exists():
            raise HTTPException(404, "Save file not found")
        path.unlink()
        return {"status": "deleted", "filename": filename}

    return app


app = create_app()
