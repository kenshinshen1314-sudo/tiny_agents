from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LennyRPG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Placeholder imports - will be implemented in future phases
# from app.api.routes import games, ai
# app.include_router(games.router, prefix="/api/games", tags=["games"])
# app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/api/health")
def health():
    return {"status": "ok"}