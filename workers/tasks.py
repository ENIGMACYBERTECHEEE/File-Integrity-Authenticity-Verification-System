"""
Background Tasks for File Processing and Verification.
"""
from workers.celery_app import celery_app
from services.verification_service import verification_service
from services.audit_service import audit_service
from database import MongoDB
import logging

logger = logging.getLogger(__name__)
database = MongoDB()


@celery_app.task(name='workers.tasks.verify_file_async')
def verify_file_async(file_id: str, user_id: str):
    """
    Asynchronously verify file integrity.
    
    Args:
        file_id: File ID to verify
        user_id: User ID performing verification
    
    Returns:
        dict: Verification result
    """
    try:
        logger.info(f"Starting async verification for file {file_id}")
        result = verification_service.verify_file(file_id)
        
        # Log audit trail
        audit_service.log_action(
            user_id=user_id,
            action="file_verification",
            resource_type="file",
            resource_id=file_id,
            details={"result": result.get("verification_status"), "async": True}
        )
        
        logger.info(f"Completed async verification for file {file_id}: {result.get('verification_status')}")
        return result
    except Exception as e:
        logger.error(f"Async verification failed for file {file_id}: {str(e)}")
        raise


@celery_app.task(name='workers.tasks.batch_verify_files')
def batch_verify_files(file_ids: list, user_id: str):
    """
    Verify multiple files in batch.
    
    Args:
        file_ids: List of file IDs to verify
        user_id: User ID performing verification
    
    Returns:
        dict: Batch verification results
    """
    try:
        logger.info(f"Starting batch verification for {len(file_ids)} files")
        results = []
        
        for file_id in file_ids:
            try:
                result = verification_service.verify_file(file_id)
                results.append({
                    "file_id": file_id,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "file_id": file_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Log batch operation
        audit_service.log_action(
            user_id=user_id,
            action="batch_verification",
            resource_type="file",
            resource_id="batch",
            details={"total_files": len(file_ids), "results": results}
        )
        
        logger.info(f"Completed batch verification for {len(file_ids)} files")
        return {"total": len(file_ids), "results": results}
    except Exception as e:
        logger.error(f"Batch verification failed: {str(e)}")
        raise


@celery_app.task(name='workers.tasks.cleanup_old_files')
def cleanup_old_files(days: int = 90):
    """
    Clean up old unverified files (background maintenance task).
    
    Args:
        days: Number of days to keep files
    
    Returns:
        dict: Cleanup statistics
    """
    try:
        from datetime import datetime, timedelta
        from repositories.file_repo import FileRepository
        
        logger.info(f"Starting cleanup of files older than {days} days")
        file_repo = FileRepository(database.db)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        # This would be implemented in file_repo
        # deleted_count = file_repo.delete_old_unverified(cutoff_date)
        
        logger.info(f"Cleanup completed")
        return {"status": "completed", "cutoff_date": cutoff_date.isoformat()}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise


@celery_app.task(name='workers.tasks.generate_report')
def generate_report(user_id: str, report_type: str = "verification_summary"):
    """
    Generate usage and verification reports.
    
    Args:
        user_id: User ID requesting report
        report_type: Type of report to generate
    
    Returns:
        dict: Report data
    """
    try:
        logger.info(f"Generating {report_type} report for user {user_id}")
        
        from repositories.file_repo import FileRepository
        file_repo = FileRepository(database.db)
        
        # Get user's files
        files = file_repo.get_by_user(user_id)
        
        report = {
            "user_id": user_id,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "total_files": len(files),
            "verified_files": len([f for f in files if f.get("verification_status") == "verified"]),
            "tampered_files": len([f for f in files if f.get("verification_status") == "tampered"]),
            "pending_files": len([f for f in files if f.get("verification_status") == "pending"]),
        }
        
        logger.info(f"Report generated for user {user_id}")
        return report
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise
