from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from apps.ebay_notifications.models import EbayNotificationConfig


class Command(BaseCommand):
    help = 'Set up eBay marketplace account deletion notification configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--endpoint-url',
            type=str,
            help='The HTTPS endpoint URL for receiving eBay notifications'
        )
        parser.add_argument(
            '--verification-token',
            type=str,
            help='The verification token (32-80 characters, alphanumeric, underscore, hyphen only)'
        )
        parser.add_argument(
            '--generate-token',
            action='store_true',
            help='Generate a random verification token'
        )
    
    def handle(self, *args, **options):
        endpoint_url = options.get('endpoint_url')
        verification_token = options.get('verification_token')
        generate_token = options.get('generate_token')
        
        if not endpoint_url:
            self.stdout.write(
                self.style.ERROR('You must provide an endpoint URL with --endpoint-url')
            )
            return
        
        if not endpoint_url.startswith('https://'):
            self.stdout.write(
                self.style.ERROR('Endpoint URL must use HTTPS protocol')
            )
            return
        
        if generate_token:
            # Generate a 40-character random token
            verification_token = get_random_string(
                length=40,
                allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Generated verification token: {verification_token}')
            )
        
        if not verification_token:
            self.stdout.write(
                self.style.ERROR('You must provide a verification token with --verification-token or use --generate-token')
            )
            return
        
        if not (32 <= len(verification_token) <= 80):
            self.stdout.write(
                self.style.ERROR('Verification token must be between 32 and 80 characters')
            )
            return
        
        # Validate token characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
        if not all(c in allowed_chars for c in verification_token):
            self.stdout.write(
                self.style.ERROR('Verification token can only contain alphanumeric characters, underscore (_), and hyphen (-)')
            )
            return
        
        # Deactivate any existing configurations
        EbayNotificationConfig.objects.update(is_active=False)
        
        # Create new configuration
        config = EbayNotificationConfig.objects.create(
            endpoint_url=endpoint_url,
            verification_token=verification_token,
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created eBay notification configuration:')
        )
        self.stdout.write(f'  Endpoint URL: {config.endpoint_url}')
        self.stdout.write(f'  Verification Token: {config.verification_token}')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('Next steps:')
        )
        self.stdout.write('1. Make sure your server is running and accessible at the endpoint URL')
        self.stdout.write('2. Go to https://developer.ebay.com/my/keys')
        self.stdout.write('3. Click "Notifications" next to your App ID')
        self.stdout.write('4. Select "Marketplace Account Deletion" radio button')
        self.stdout.write('5. Enter an alert email address')
        self.stdout.write('6. Enter your endpoint URL and verification token')
        self.stdout.write('7. Click Save - eBay will send a challenge code to verify your endpoint')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('Your endpoint is ready to handle eBay challenge codes and deletion notifications!')
        )
