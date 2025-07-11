from fastapi import FastAPI
from routers import auth

app = FastAPI(title="Auth Service")
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/ping")
async def ping():
    return {"msg": "pong"}