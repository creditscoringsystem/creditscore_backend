from fastapi import FastAPI
from routers import profile, security, preferences, consent

app = FastAPI(title="Profile Service API", version="1.0.0")

app.include_router(profile.router)
app.include_router(security.router)
app.include_router(preferences.router)
app.include_router(consent.router) 