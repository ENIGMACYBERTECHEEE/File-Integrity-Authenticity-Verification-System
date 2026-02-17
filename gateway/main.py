"""
FastAPI Gateway - Main application entry point.
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import logging
import sys
from io import BytesIO

from config import config
from database import MongoDB
from gateway.dependencies import get_current_user, get_admin_user
from gateway.rate_limit import limiter, get_client_ip
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from services.orchestrator import service_orchestrator
from services.file_service import file_service
from services.verification_service import verification_service
from services.audit_service import audit_service
from services.auth_service import auth_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="File Integrity & Authenticity Verification Platform",
    description="Secure file integrity verification using SHA-256, RSA-2048, and AES-256-GCM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class VerifyBatchRequest(BaseModel):
    file_ids: List[str]


class AuditLogsQuery(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = 100


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting File Integrity & Authenticity Verification Platform")
    config.ensure_directories()
    MongoDB.connect()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application")
    MongoDB.disconnect()
    logger.info("Application shutdown complete")


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def health_check(request: Request):
    """System health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Authentication endpoints
@app.post("/api/v1/auth/register", tags=["Authentication"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def register(request: Request, data: RegisterRequest):
    """Register a new user."""
    try:
        result = service_orchestrator.register_and_setup_user(
            username=data.username,
            email=data.email,
            password=data.password
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/v1/auth/login", tags=["Authentication"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def login(request: Request, data: LoginRequest):
    """Authenticate user and get access token."""
    try:
        ip_address = get_client_ip(request)
        result = service_orchestrator.authenticate_user(
            username=data.username,
            password=data.password,
            ip_address=ip_address
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


# File endpoints
@app.post("/api/v1/files/upload", tags=["Files"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a file for integrity verification."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload file
        result = service_orchestrator.upload_and_verify_file(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user["_id"],
            username=current_user["username"],
            password=password,
            description=description,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/v1/files", tags=["Files"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def list_files(request: Request, current_user: dict = Depends(get_current_user)):
    """List all files for the current user."""
    try:
        files = file_service.list_user_files(current_user["_id"])
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve files"
        )


@app.get("/api/v1/files/{file_id}", tags=["Files"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def get_file_metadata(
    request: Request,
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get file metadata."""
    try:
        metadata = file_service.get_file_metadata(file_id, current_user["_id"])
        return metadata
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/api/v1/files/{file_id}/download", tags=["Files"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def download_file(
    request: Request,
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download a file."""
    try:
        result = file_service.download_file(
            file_id=file_id,
            user_id=current_user["_id"],
            username=current_user["username"]
        )
        
        return StreamingResponse(
            BytesIO(result["file_content"]),
            media_type=result["mime_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{result["filename"]}"'
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.delete("/api/v1/files/{file_id}", tags=["Files"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def delete_file(
    request: Request,
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a file."""
    try:
        result = file_service.delete_file(
            file_id=file_id,
            user_id=current_user["_id"],
            username=current_user["username"]
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Verification endpoints
@app.post("/api/v1/verify/{file_id}", tags=["Verification"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def verify_file(
    request: Request,
    file_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """Verify file integrity and authenticity. (Admin only)"""
    try:
        result = service_orchestrator.verify_and_audit_file(
            file_id=file_id,
            user_id=current_user["_id"],
            username=current_user["username"]
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.post("/api/v1/verify/batch", tags=["Verification"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def verify_batch(
    request: Request,
    data: VerifyBatchRequest,
    current_user: dict = Depends(get_admin_user)
):
    """Verify multiple files. (Admin only)"""
    try:
        result = verification_service.verify_batch(
            file_ids=data.file_ids,
            user_id=current_user["_id"],
            username=current_user["username"]
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch verification failed"
        )


# Audit endpoints
@app.get("/api/v1/audit/logs", tags=["Audit"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def get_audit_logs(
    request: Request,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs with optional filters."""
    try:
        # If user_id is not provided or user is not admin, show only their logs
        if not user_id or current_user.get("role") != "admin":
            user_id = current_user["_id"]
        
        logs = audit_service.get_logs(
            user_id=user_id,
            action=action,
            limit=limit
        )
        
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
