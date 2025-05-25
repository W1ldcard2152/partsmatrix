# Acura vehicle creation command dispatcher
from django.core.management.base import BaseCommand
import sys
import os

class Command(BaseCommand):
    help = 'Create Acura vehicles - dispatcher command'
    
    def handle(self, *args, **options):
        # Import and execute the actual command
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'acura'))
        from create_vehicles import Command as AcuraVehiclesCommand
        
        acura_command = AcuraVehiclesCommand()
        acura_command.handle(*args, **options)
