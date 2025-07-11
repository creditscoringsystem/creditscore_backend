from fastapi import FastAPI
from routers import users, admin

app = FastAPI(title="User Service")
app.include_router(users.router, tags=["users"])
app.include_router(admin.router, tags=["admin"])

@app.get("/ping")
async def ping():
    return {"msg": "pong"}