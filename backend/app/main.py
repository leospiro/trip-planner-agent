from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import trip, xhs

app = FastAPI(
    title="Smart Trip Planner API",
    description="An API for generating personalized travel plans using AI Agents.",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip.router, prefix="/api/trip", tags=["Trip Planning"])
app.include_router(xhs.router, prefix="/api/xhs", tags=["XiaoHongShu"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Trip Planner API"}
