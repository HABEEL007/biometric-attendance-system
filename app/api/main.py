import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import staff_routes, enrollment_routes, attendance_routes, camera_routes
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("central_backend", "central.log")

app = FastAPI(
    title="AI Biometric Attendance System (Central Gateway)",
    version="2.0",
    description="Central Orchestrator Backend linking face, iris, and liveness microservices."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-routers
app.include_router(staff_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(attendance_routes.router)
app.include_router(camera_routes.router)

@app.get("/")
def read_root():
    return {
        "title": "AI Biometric Attendance System - Central API Gateway",
        "version": "2.0",
        "documentation": "/docs",
        "status": "online"
    }

if __name__ == "__main__":
    logger.info(f"Starting Central Gateway API on {settings.CENTRAL_API_HOST}:{settings.CENTRAL_API_PORT}")
    uvicorn.run(app, host=settings.CENTRAL_API_HOST, port=settings.CENTRAL_API_PORT)
