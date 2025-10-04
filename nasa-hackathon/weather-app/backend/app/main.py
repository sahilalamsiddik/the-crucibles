from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Weather Likelihood API")
app.include_router(router)
