"""
Webhook Manager Service - Event Publishing and Webhook Delivery.
"""
from typing import List, Dict, Optional
import logging
import requests
from datetime import datetime
from repositories.verification_repo import VerificationRepository
from database import MongoDB

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages webhook registrations and event delivery."""
    
    def __init__(self):
        self.database = MongoDB.get_database()
        self.webhooks_collection = self.database.webhooks
        
    def register_webhook(self, user_id: str, url: str, events: List[str], secret: Optional[str] = None) -> Dict:
        """
        Register a new webhook for user.
        
        Args:
            user_id: User ID
            url: Webhook endpoint URL
            events: List of event types to subscribe to
            secret: Optional secret for webhook signing
            
        Returns:
            dict: Webhook registration details
        """
        try:
            webhook = {
                "user_id": user_id,
                "url": url,
                "events": events,
                "secret": secret,
                "active": True,
                "created_at": datetime.utcnow(),
                "last_triggered": None,
                "total_deliveries": 0,
                "failed_deliveries": 0
            }
            
            result = self.webhooks_collection.insert_one(webhook)
            webhook["_id"] = str(result.inserted_id)
            
            logger.info(f"Registered webhook for user {user_id}: {url}")
            return webhook
        except Exception as e:
            logger.error(f"Webhook registration failed: {str(e)}")
            raise
    
    def publish_event(self, event_type: str, user_id: str, data: Dict) -> None:
        """
        Publish event to all registered webhooks.
        
        Args:
            event_type: Type of event (e.g., 'file.uploaded', 'file.verified')
            user_id: User ID
            data: Event data payload
        """
        try:
            # Find all webhooks subscribed to this event
            webhooks = self.webhooks_collection.find({
                "user_id": user_id,
                "events": event_type,
                "active": True
            })
            
            for webhook in webhooks:
                self._deliver_webhook(webhook, event_type, data)
                
        except Exception as e:
            logger.error(f"Event publishing failed: {str(e)}")
    
    def _deliver_webhook(self, webhook: Dict, event_type: str, data: Dict) -> None:
        """
        Deliver webhook to endpoint.
        
        Args:
            webhook: Webhook configuration
            event_type: Event type
            data: Event data
        """
        try:
            payload = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            headers = {"Content-Type": "application/json"}
            if webhook.get("secret"):
                # Add webhook signature if secret is configured
                import hmac
                import hashlib
                import json
                
                signature = hmac.new(
                    webhook["secret"].encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = signature
            
            response = requests.post(
                webhook["url"],
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Update webhook stats
            self.webhooks_collection.update_one(
                {"_id": webhook["_id"]},
                {
                    "$set": {"last_triggered": datetime.utcnow()},
                    "$inc": {
                        "total_deliveries": 1,
                        "failed_deliveries": 0 if response.status_code == 200 else 1
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook delivered successfully to {webhook['url']}")
            else:
                logger.warning(f"Webhook delivery failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Webhook delivery error: {str(e)}")
            self.webhooks_collection.update_one(
                {"_id": webhook["_id"]},
                {"$inc": {"failed_deliveries": 1}}
            )
    
    def list_webhooks(self, user_id: str) -> List[Dict]:
        """
        List all webhooks for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of webhooks
        """
        webhooks = list(self.webhooks_collection.find({"user_id": user_id}))
        for webhook in webhooks:
            webhook["_id"] = str(webhook["_id"])
        return webhooks
    
    def delete_webhook(self, webhook_id: str, user_id: str) -> bool:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
            user_id: User ID
            
        Returns:
            bool: True if deleted
        """
        from bson import ObjectId
        result = self.webhooks_collection.delete_one({
            "_id": ObjectId(webhook_id),
            "user_id": user_id
        })
        return result.deleted_count > 0


# Global webhook manager instance
webhook_manager = WebhookManager()
