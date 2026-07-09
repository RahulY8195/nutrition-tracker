from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import goals, meals, recommendations, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AI Nutrition Tracker API", lifespan=lifespan)

app.include_router(meals.router)
app.include_router(goals.router)
app.include_router(summary.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    return {"message": "AI Nutrition Tracker API is running"}
