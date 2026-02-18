"""
FastAPI Gateway - Main application entry point.
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
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
from gateway.websocket_manager import connection_manager
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from services.orchestrator import service_orchestrator
from services.file_service import file_service
from services.verification_service import verification_service
from services.audit_service import audit_service
from services.auth_service import auth_service
from services.webhook_service import webhook_manager
from services.monitoring_service import monitoring_service
from services.admin_service import admin_service
from repositories.file_repo import FileRepository

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
    """System health check endpoint with detailed metrics."""
    return monitoring_service.get_system_health()


# Monitoring endpoints
@app.get("/api/v1/monitoring/metrics", tags=["Monitoring"])
async def get_metrics(
    metric_type: Optional[str] = None,
    hours: int = 24,
    current_user: dict = Depends(get_admin_user)
):
    """Get system metrics (admin only)."""
    return monitoring_service.get_metrics_summary(metric_type, hours)


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


# Admin endpoints
@app.patch("/api/v1/admin/files/{file_id}/status", tags=["Admin"])
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def update_file_status(
    request: Request,
    file_id: str,
    status_update: dict,
    current_user: dict = Depends(get_admin_user)
):
    """Update file verification status (admin only)."""
    try:
        verification_status = status_update.get("verification_status")
        if verification_status not in ["verified", "tampered", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification status. Must be: verified, tampered, or pending"
            )
        
        # Update file status in database
        file_repo = FileRepository(database.db)
        file = file_repo.get_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Determine verified flag based on status
        verified = (verification_status == "verified")
        
        file_repo.update_verification_status(file_id, verification_status, verified)
        
        # Log the action
        audit_service.log_action(
            user_id=str(current_user["_id"]),
            action="admin_status_update",
            resource_type="file",
            resource_id=file_id,
            details={"new_status": verification_status}
        )
        
        return {
            "message": "File status updated successfully",
            "file_id": file_id,
            "verification_status": verification_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File status update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file status"
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


# WebSocket endpoints
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates.
    
    Args:
        websocket: WebSocket connection
        user_id: User ID for the connection
    """
    await connection_manager.connect(websocket, user_id)
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to File Integrity System"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo or process messages if needed
            await websocket.send_json({
                "type": "message_received",
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            })
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")


# Webhook endpoints
@app.post("/api/v1/webhooks/register", tags=["Webhooks"])
async def register_webhook(
    url: str,
    events: List[str],
    secret: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Register a webhook for event notifications."""
    try:
        webhook = webhook_manager.register_webhook(
            user_id=str(current_user["_id"]),
            url=url,
            events=events,
            secret=secret
        )
        return webhook
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook registration failed: {str(e)}"
        )


@app.get("/api/v1/webhooks", tags=["Webhooks"])
async def list_webhooks(current_user: dict = Depends(get_current_user)):
    """List all registered webhooks."""
    try:
        webhooks = webhook_manager.list_webhooks(str(current_user["_id"]))
        return {"webhooks": webhooks, "count": len(webhooks)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve webhooks"
        )


@app.delete("/api/v1/webhooks/{webhook_id}", tags=["Webhooks"])
async def delete_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a webhook."""
    try:
        success = webhook_manager.delete_webhook(webhook_id, str(current_user["_id"]))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )
        return {"message": "Webhook deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete webhook"
        )


# ═══════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/stats", tags=["Admin"])
async def get_admin_stats(
    admin_user: dict = Depends(get_admin_user)
):
    """Get comprehensive system statistics (Admin only)."""
    try:
        stats = admin_service.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system statistics"
        )


@app.get("/api/v1/admin/users", tags=["Admin"])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: dict = Depends(get_admin_user)
):
    """Get all users (Admin only)."""
    try:
        result = admin_service.get_all_users(skip=skip, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@app.get("/api/v1/admin/files", tags=["Admin"])
async def get_all_files(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    admin_user: dict = Depends(get_admin_user)
):
    """Get all files from all users (Admin only)."""
    try:
        result = admin_service.get_all_files(skip=skip, limit=limit, include_deleted=include_deleted)
        return result
    except Exception as e:
        logger.error(f"Error getting all files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get files"
        )


@app.get("/api/v1/admin/verifications", tags=["Admin"])
async def get_all_verifications(
    skip: int = 0,
    limit: int = 100,
    admin_user: dict = Depends(get_admin_user)
):
    """Get all verification records (Admin only)."""
    try:
        result = admin_service.get_all_verifications(skip=skip, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Error getting all verifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get verifications"
        )


class UserStatusUpdate(BaseModel):
    is_active: bool

@app.patch("/api/v1/admin/users/{user_id}/status", tags=["Admin"])
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    admin_user: dict = Depends(get_admin_user)
):
    """Activate or deactivate a user (Admin only)."""
    try:
        success = admin_service.update_user_status(user_id, status_update.is_active)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )


class UserRoleUpdate(BaseModel):
    role: str

@app.patch("/api/v1/admin/users/{user_id}/role", tags=["Admin"])
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    admin_user: dict = Depends(get_admin_user)
):
    """Update user role (Admin only)."""
    try:
        success = admin_service.update_user_role(user_id, role_update.role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User role updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@app.delete("/api/v1/admin/files/{file_id}", tags=["Admin"])
async def admin_delete_file(
    file_id: str,
    admin_user: dict = Depends(get_admin_user)
):
    """Permanently delete a file (Admin only)."""
    try:
        success = admin_service.delete_file_permanently(file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return {"message": "File permanently deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@app.get("/api/v1/admin/users/{user_id}/activity", tags=["Admin"])
async def get_user_activity(
    user_id: str,
    days: int = 7,
    admin_user: dict = Depends(get_admin_user)
):
    """Get user activity summary (Admin only)."""
    try:
        activity = admin_service.get_user_activity(user_id, days)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return activity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user activity"
        )


@app.get("/api/v1/admin/activity-timeline", tags=["Admin"])
async def get_activity_timeline(
    hours: int = 24,
    admin_user: dict = Depends(get_admin_user)
):
    """Get system activity timeline (Admin only)."""
    try:
        timeline = admin_service.get_activity_timeline(hours)
        return {"timeline": timeline, "hours": hours}
    except Exception as e:
        logger.error(f"Error getting activity timeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get activity timeline"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
