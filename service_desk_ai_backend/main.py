import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, tickets, notifications, chat, knowledge_base, reports, audit, password_reset

# Create all tables if they don't exist (useful for initial deployment)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ServiceDeskAI Backend",
    description="FastAPI backend providing role‑based authentication, ticketing, chat, knowledge base, reports, notifications and audit logging.",
    version="0.1.0",
)

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(knowledge_base.router, prefix="/api/knowledge", tags=["knowledge base"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(password_reset.router, prefix="/api/password-reset", tags=["password reset"])

# Root health check
@app.get("/")
async def health_check():
    return {"status": "ok"}
