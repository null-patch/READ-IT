from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.ws import router as websocket_router
from app.api.conversation import router as conversation_router


app = FastAPI(
    title="Read It! API",
    description="Backend API for Read It!",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(websocket_router)
app.include_router(conversation_router)

@app.get("/")
async def root():
    return {
        "app": "Read It!",
        "status": "online",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
