from django.core.management.base import BaseCommand
import logging


class Command(BaseCommand):
    help = 'Test logging configuration and output levels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Test specific logging level'
        )

    def handle(self, *args, **options):
        # Get loggers
        logger = logging.getLogger(__name__)
        django_logger = logging.getLogger('django')
        db_logger = logging.getLogger('django.db.backends')
        apps_logger = logging.getLogger('apps')
        
        # Show current configuration
        from django.conf import settings
        self.stdout.write(
            self.style.SUCCESS('=== Current Logging Configuration ===')
        )
        self.stdout.write(f"LOG_LEVEL: {getattr(settings, 'LOG_LEVEL', 'Not Set')}")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        
        # Show effective levels
        loggers_to_check = [
            ('django', django_logger),
            ('django.db.backends', db_logger), 
            ('apps', apps_logger),
            ('command', logger)
        ]
        
        self.stdout.write("\\nEffective Logger Levels:")
        for name, log in loggers_to_check:
            self.stdout.write(f"  {name}: {logging.getLevelName(log.level)}")
        
        # Test specific level if provided
        if options['level']:
            level = options['level']
            self.stdout.write(f"\\n=== Testing {level} Level ===")
            
            # Test the specific level
            getattr(logger, level.lower())(f"Command logger {level} message")
            getattr(django_logger, level.lower())(f"Django logger {level} message")
            getattr(apps_logger, level.lower())(f"Apps logger {level} message")
            
            if level == 'DEBUG':
                getattr(db_logger, level.lower())(f"Database logger {level} message")
        else:
            # Test all levels
            self.stdout.write("\\n=== Testing All Levels ===")
            levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            
            for level in levels:
                self.stdout.write(f"\\n--- {level} ---")
                getattr(logger, level.lower())(f"Command {level} message")
                getattr(django_logger, level.lower())(f"Django {level} message")
                getattr(apps_logger, level.lower())(f"Apps {level} message")
                
                if level == 'DEBUG':
                    getattr(db_logger, level.lower())(f"DB {level} message")
        
        self.stdout.write("\\n=== Instructions ===")
        self.stdout.write("With LOG_LEVEL=WARNING, you should only see WARNING+ messages")
        self.stdout.write("To change: Edit LOG_LEVEL in your .env file")
        self.stdout.write("Available: DEBUG, INFO, WARNING, ERROR, CRITICAL")
