import hashlib
import json
import requests
from django.core.management.base import BaseCommand
from apps.ebay_notifications.models import EbayNotificationConfig


class Command(BaseCommand):
    help = 'Test the eBay marketplace account deletion endpoint'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--challenge-code',
            type=str,
            default='test123',
            help='Challenge code to test with (default: test123)'
        )
        parser.add_argument(
            '--send-notification',
            action='store_true',
            help='Send a test deletion notification'
        )
    
    def handle(self, *args, **options):
        challenge_code = options.get('challenge_code')
        send_notification = options.get('send_notification')
        
        # Get the active configuration
        config = EbayNotificationConfig.objects.filter(is_active=True).first()
        if not config:
            self.stdout.write(
                self.style.ERROR('No active eBay notification configuration found. Run setup_ebay_notifications first.')
            )
            return
        
        self.stdout.write(f'Testing endpoint: {config.endpoint_url}')
        self.stdout.write(f'Verification token: {config.verification_token}')
        self.stdout.write('')
        
        if send_notification:
            self._test_notification(config)
        else:
            self._test_challenge(config, challenge_code)
    
    def _test_challenge(self, config, challenge_code):
        """Test the challenge code verification"""
        self.stdout.write('Testing challenge code verification...')
        
        try:
            # Send GET request with challenge code
            url = f"{config.endpoint_url}?challenge_code={challenge_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                challenge_response = data.get('challengeResponse')
                
                # Calculate expected response
                hash_input = challenge_code + config.verification_token + config.endpoint_url
                expected_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                self.stdout.write(f'Response status: {response.status_code}')
                self.stdout.write(f'Challenge response: {challenge_response}')
                self.stdout.write(f'Expected response: {expected_response}')
                
                if challenge_response == expected_response:
                    self.stdout.write(self.style.SUCCESS('✓ Challenge verification test PASSED'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Challenge verification test FAILED - Hash mismatch'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Request failed with status: {response.status_code}'))
                self.stdout.write(f'Response: {response.text}')
                
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'✗ Request error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Unexpected error: {str(e)}'))
    
    def _test_notification(self, config):
        """Test a sample account deletion notification"""
        self.stdout.write('Testing account deletion notification...')
        
        # Sample notification payload
        payload = {
            "metadata": {
                "topic": "MARKETPLACE_ACCOUNT_DELETION",
                "schemaVersion": "1.0",
                "deprecated": False
            },
            "notification": {
                "notificationId": "test-notification-" + str(hash(config.endpoint_url))[:8],
                "eventDate": "2025-06-11T20:43:59.462Z",
                "publishDate": "2025-06-11T20:43:59.679Z",
                "publishAttemptCount": 1,
                "data": {
                    "username": "test_user_123",
                    "userId": "testUserId123",
                    "eiasToken": "dGVzdFRva2VuMTIz"  # base64 encoded "testToken123"
                }
            }
        }
        
        try:
            response = requests.post(
                config.endpoint_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            self.stdout.write(f'Response status: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Account deletion notification test PASSED'))
                self.stdout.write('Check the admin panel to see the logged notification.')
            else:
                self.stdout.write(self.style.ERROR(f'✗ Notification test FAILED - Status: {response.status_code}'))
                self.stdout.write(f'Response: {response.text}')
                
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'✗ Request error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Unexpected error: {str(e)}'))
