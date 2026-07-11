from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, hcp, interaction, chat, voice, agent
from .database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI HCP CRM")

# Configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(hcp.router)
app.include_router(interaction.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(agent.router)

@app.get("/")
def root():
    return {"message": "AI HCP CRM API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "sqlite", "groq": "connected"}

logger.info("🚀 Application startup complete!")