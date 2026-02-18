"""
Monitoring and Metrics Service - System Health and Performance Monitoring.
"""
from typing import Dict
from datetime import datetime, timedelta
from database import MongoDB
import logging

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for system monitoring and metrics collection."""
    
    def __init__(self):
        self.database = MongoDB.get_database()
        self.metrics_collection = self.database.metrics
    
    def record_metric(self, metric_type: str, value: float, metadata: Dict = None):
        """
        Record a metric data point.
        
        Args:
            metric_type: Type of metric (e.g., 'file_upload', 'verification_time')
            value: Metric value
            metadata: Optional metadata
        """
        metric = {
            "type": metric_type,
            "value": value,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        self.metrics_collection.insert_one(metric)
    
    def get_system_health(self) -> Dict:
        """
        Get current system health status.
        
        Returns:
            dict: System health information
        """
        try:
            from repositories.file_repo import file_repository
            from repositories.user_repo import user_repository
            from gateway.websocket_manager import connection_manager
            
            # Get current hour stats
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_files = self.database.files.count_documents({
                "upload_date": {"$gte": one_hour_ago}
            })
            
            recent_verifications = self.database.verifications.count_documents({
                "timestamp": {"$gte": one_hour_ago}
            })
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_users": user_repository.count(),
                    "total_files": file_repository.count(),
                    "active_websocket_connections": connection_manager.get_total_connections(),
                    "connected_users": connection_manager.get_active_users_count(),
                    "uploads_last_hour": recent_files,
                    "verifications_last_hour": recent_verifications,
                    "database_connected": self.database is not None
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def get_metrics_summary(self, metric_type: str = None, hours: int = 24) -> Dict:
        """
        Get metrics summary for the specified time period.
        
        Args:
            metric_type: Optional metric type filter
            hours: Number of hours to look back
        
        Returns:
            dict: Metrics summary
        """
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            query = {"timestamp": {"$gte": cutoff}}
            
            if metric_type:
                query["type"] = metric_type
            
            metrics = list(self.metrics_collection.find(query).sort("timestamp", -1))
            
            if not metrics:
                return {"count": 0, "metrics": []}
            
            # Calculate statistics
            values = [m["value"] for m in metrics]
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            
            return {
                "count": len(metrics),
                "period_hours": hours,
                "metric_type": metric_type,
                "statistics": {
                    "average": avg_value,
                    "min": min_value,
                    "max": max_value
                },
                "latest_metrics": [
                    {
                        "type": m["type"],
                        "value": m["value"],
                        "timestamp": m["timestamp"].isoformat()
                    }
                    for m in metrics[:10]  # Last 10 metrics
                ]
            }
        except Exception as e:
            logger.error(f"Metrics summary failed: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_metrics(self, days: int = 30):
        """
        Clean up metrics older than specified days.
        
        Args:
            days: Number of days to retain
        
        Returns:
            int: Number of metrics deleted
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = self.metrics_collection.delete_many({
            "timestamp": {"$lt": cutoff}
        })
        logger.info(f"Cleaned up {result.deleted_count} old metrics")
        return result.deleted_count


# Global monitoring service instance
monitoring_service = MonitoringService()
