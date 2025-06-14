from django.core.management.base import BaseCommand
from apps.ebay_notifications.models import EbayNotificationConfig


class Command(BaseCommand):
    help = 'Show the current eBay notification configuration for copy/paste into eBay portal'
    
    def handle(self, *args, **options):
        config = EbayNotificationConfig.objects.filter(is_active=True).first()
        
        if not config:
            self.stdout.write(
                self.style.ERROR('No active eBay notification configuration found.')
            )
            self.stdout.write('Run: python manage.py setup_ebay_notifications --help')
            return
        
        self.stdout.write(self.style.SUCCESS('eBay Developer Portal Configuration'))
        self.stdout.write('=' * 50)
        self.stdout.write('')
        
        self.stdout.write('Go to: https://developer.ebay.com/my/keys')
        self.stdout.write('Click: "Notifications" next to your App ID')
        self.stdout.write('Select: "Marketplace Account Deletion" radio button')
        self.stdout.write('')
        
        self.stdout.write(self.style.WARNING('Configuration Values:'))
        self.stdout.write('=' * 25)
        self.stdout.write('')
        
        self.stdout.write('Alert Email:')
        self.stdout.write('  (Enter your email address for alerts)')
        self.stdout.write('')
        
        self.stdout.write('Marketplace account deletion notification endpoint:')
        self.stdout.write(f'  {config.endpoint_url}')
        self.stdout.write('')
        
        self.stdout.write('Verification token:')
        self.stdout.write(f'  {config.verification_token}')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('After entering these values, click "Save"'))
        self.stdout.write('eBay will immediately send a challenge code to verify your endpoint.')
        self.stdout.write('')
        
        self.stdout.write('Status: ', ending='')
        if hasattr(self, 'style'):
            self.stdout.write(self.style.SUCCESS('✓ Configuration ready'))
        else:
            self.stdout.write('Configuration ready')
