# Brands management command dispatcher
from django.core.management.base import BaseCommand
import sys
import os

class Command(BaseCommand):
    help = 'Add vehicle brands - dispatcher command'
    
    def handle(self, *args, **options):
        # Import and execute the actual command
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'general'))
        from add_brands import Command as BrandsCommand
        
        brands_command = BrandsCommand()
        brands_command.handle(*args, **options)
