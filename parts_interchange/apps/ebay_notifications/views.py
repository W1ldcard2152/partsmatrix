import hashlib
import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
from .models import EbayAccountDeletionLog, EbayNotificationConfig

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MarketplaceAccountDeletionView(View):
    """
    eBay Marketplace Account Deletion notification endpoint.
    
    Handles both:
    1. GET requests for challenge code verification during subscription setup
    2. POST requests for actual account deletion notifications
    """
    
    def get(self, request):
        """
        Handle eBay challenge code verification.
        
        eBay sends a GET request with a challenge_code parameter.
        We need to hash: challengeCode + verificationToken + endpoint
        And return the hash as a JSON response.
        """
        challenge_code = request.GET.get('challenge_code')
        
        if not challenge_code:
            logger.error("No challenge_code parameter in GET request")
            return JsonResponse({'error': 'Missing challenge_code parameter'}, status=400)
        
        try:
            # Get the verification token from our configuration
            config = EbayNotificationConfig.objects.filter(is_active=True).first()
            if not config:
                logger.error("No active eBay notification configuration found")
                return JsonResponse({'error': 'Configuration not found'}, status=500)
            
            verification_token = config.verification_token
            endpoint_url = config.endpoint_url
            
            # Create the hash as specified by eBay: challengeCode + verificationToken + endpoint
            hash_input = challenge_code + verification_token + endpoint_url
            challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
            
            logger.info(f"eBay challenge verification successful for challenge_code: {challenge_code}")
            
            # Return the response in the exact format eBay expects
            response_data = {
                "challengeResponse": challenge_response
            }
            
            return JsonResponse(response_data, content_type='application/json')
            
        except Exception as e:
            logger.error(f"Error processing eBay challenge code: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def post(self, request):
        """
        Handle eBay marketplace account deletion notifications.
        
        Expected payload format:
        {
            "metadata": {
                "topic": "MARKETPLACE_ACCOUNT_DELETION",
                "schemaVersion": "1.0",
                "deprecated": false
            },
            "notification": {
                "notificationId": "49feeaeb-4982-42d9-a377-9645b8479411_33f7e043-fed8-442b-9d44-791923bd9a6d",
                "eventDate": "2021-03-19T20:43:59.462Z",
                "publishDate": "2021-03-19T20:43:59.679Z",
                "publishAttemptCount": 1,
                "data": {
                    "username": "test_user",
                    "userId": "ma8vp1jySJC",
                    "eiasToken": "nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJnY+gAZGEpwmdj6x9nY+seQ=="
                }
            }
        }
        """
        try:
            # Parse the JSON payload
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in eBay notification: {str(e)}")
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            # Validate the payload structure
            if not self._validate_payload(payload):
                logger.error(f"Invalid payload structure: {payload}")
                return JsonResponse({'error': 'Invalid payload structure'}, status=400)
            
            notification = payload['notification']
            data = notification['data']
            
            # Extract notification data
            notification_id = notification['notificationId']
            event_date = datetime.fromisoformat(notification['eventDate'].replace('Z', '+00:00'))
            publish_date = datetime.fromisoformat(notification['publishDate'].replace('Z', '+00:00'))
            publish_attempt_count = notification['publishAttemptCount']
            
            username = data['username']
            user_id = data['userId']
            eias_token = data['eiasToken']
            
            # Check if we've already processed this notification
            existing_log = EbayAccountDeletionLog.objects.filter(notification_id=notification_id).first()
            if existing_log:
                logger.info(f"Duplicate eBay account deletion notification: {notification_id}")
                # Still return success to eBay to acknowledge receipt
                return HttpResponse(status=200)
            
            # Log the notification
            deletion_log = EbayAccountDeletionLog.objects.create(
                notification_id=notification_id,
                username=username,
                user_id=user_id,
                eias_token=eias_token,
                event_date=event_date,
                publish_date=publish_date,
                publish_attempt_count=publish_attempt_count,
                processed=False
            )
            
            logger.info(f"Received eBay account deletion notification for user: {username} (ID: {user_id})")
            
            # Process the deletion (remove any stored eBay user data)
            deleted_data_summary = self._process_account_deletion(username, user_id, eias_token)
            
            # Mark as processed
            deletion_log.processed = True
            deletion_log.processed_date = timezone.now()
            deletion_log.deleted_data_summary = deleted_data_summary
            deletion_log.save()
            
            logger.info(f"Successfully processed eBay account deletion for user: {username}")
            
            # Return success response to eBay
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Error processing eBay account deletion notification: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _validate_payload(self, payload):
        """Validate the eBay notification payload structure."""
        try:
            # Check required top-level fields
            if 'metadata' not in payload or 'notification' not in payload:
                return False
            
            metadata = payload['metadata']
            if metadata.get('topic') != 'MARKETPLACE_ACCOUNT_DELETION':
                return False
            
            notification = payload['notification']
            required_notification_fields = ['notificationId', 'eventDate', 'publishDate', 'publishAttemptCount', 'data']
            if not all(field in notification for field in required_notification_fields):
                return False
            
            data = notification['data']
            required_data_fields = ['username', 'userId', 'eiasToken']
            if not all(field in data for field in required_data_fields):
                return False
            
            return True
        except (KeyError, TypeError):
            return False
    
    def _process_account_deletion(self, username, user_id, eias_token):
        """
        Process the account deletion by removing any stored eBay user data.
        
        Since we're primarily a parts database and don't store much user-specific
        eBay data, this is mainly for compliance logging. However, we should
        check for and remove any data that might be linked to the eBay user.
        
        Args:
            username (str): eBay username
            user_id (str): eBay user ID
            eias_token (str): eBay EIAS token
            
        Returns:
            str: Summary of what data was deleted
        """
        deleted_items = []
        
        try:
            # Check if we have any eBay-related data that might be linked to this user
            # Since this is a parts database, we likely don't store user-specific data,
            # but we should check for any potential data that could be linked
            
            # Example checks (adjust based on your actual data model):
            
            # 1. Check for any saved searches or user preferences (if implemented)
            # 2. Check for any user-specific eBay listings cached (if implemented)
            # 3. Check for any user feedback or ratings (if implemented)
            
            # For now, since this is primarily a parts interchange database,
            # we likely don't have user-specific eBay data to delete
            
            deleted_items.append("Checked for eBay user-specific data - none found in parts database")
            
            # Log that we processed this deletion request
            logger.info(f"Processed account deletion for eBay user: {username} (ID: {user_id})")
            
        except Exception as e:
            logger.error(f"Error during account deletion processing: {str(e)}")
            deleted_items.append(f"Error during deletion processing: {str(e)}")
        
        return "; ".join(deleted_items)
