# This would go in: parts_interchange/apps/vehicles/management/commands/add_brands.py

from django.core.management.base import BaseCommand
from apps.vehicles.models import Make

class Command(BaseCommand):
    help = 'Add the 32 Y2K+ vehicle brands to the database'

    def handle(self, *args, **options):
        brands = [
            ('Acura', 'Japan'),
            ('Audi', 'Germany'),
            ('BMW', 'Germany'),
            ('Buick', 'USA'),
            ('Cadillac', 'USA'),
            ('Chevrolet', 'USA'),
            ('Chrysler', 'USA'),
            ('Dodge', 'USA'),  # includes RAM
            ('Ford', 'USA'),
            ('Genesis', 'South Korea'),
            ('GMC', 'USA'),
            ('Honda', 'Japan'),
            ('Hummer', 'USA'),
            ('Hyundai', 'South Korea'),
            ('Infiniti', 'Japan'),
            ('Jaguar', 'UK'),
            ('Jeep', 'USA'),
            ('Kia', 'South Korea'),
            ('Land Rover', 'UK'),
            ('Lexus', 'Japan'),
            ('Lincoln', 'USA'),
            ('Mazda', 'Japan'),
            ('Mercedes-Benz', 'Germany'),
            ('Mini', 'Germany'),  # BMW-owned
            ('Mitsubishi', 'Japan'),
            ('Nissan', 'Japan'),
            ('Porsche', 'Germany'),
            ('Saturn', 'USA'),
            ('Subaru', 'Japan'),
            ('Toyota', 'Japan'),
            ('Volkswagen', 'Germany'),
            ('Volvo', 'Sweden'),
        ]

        created_count = 0
        for name, country in brands:
            make, created = Make.objects.get_or_create(
                name=name, 
                defaults={'country': country, 'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {name}")
            else:
                self.stdout.write(f"Exists: {name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} new brands')
        )