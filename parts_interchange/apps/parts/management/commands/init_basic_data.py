from django.core.management.base import BaseCommand
from apps.parts.models import Manufacturer, PartCategory


class Command(BaseCommand):
    help = 'Initialize the database with basic manufacturers and categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing basic data...'))
        
        # Create basic manufacturers
        manufacturers_data = [
            {'name': 'General Motors', 'abbreviation': 'GM', 'country': 'USA'},
            {'name': 'Ford Motor Company', 'abbreviation': 'FORD', 'country': 'USA'},
            {'name': 'Chrysler', 'abbreviation': 'CHRYSLER', 'country': 'USA'},
            {'name': 'Toyota', 'abbreviation': 'TOYOTA', 'country': 'Japan'},
            {'name': 'Honda', 'abbreviation': 'HONDA', 'country': 'Japan'},
            {'name': 'Nissan', 'abbreviation': 'NISSAN', 'country': 'Japan'},
            {'name': 'Volkswagen', 'abbreviation': 'VW', 'country': 'Germany'},
            {'name': 'BMW', 'abbreviation': 'BMW', 'country': 'Germany'},
            {'name': 'Mercedes-Benz', 'abbreviation': 'MB', 'country': 'Germany'},
            {'name': 'Audi', 'abbreviation': 'AUDI', 'country': 'Germany'},
        ]
        
        created_manufacturers = 0
        for mfg_data in manufacturers_data:
            manufacturer, created = Manufacturer.objects.get_or_create(
                abbreviation=mfg_data['abbreviation'],
                defaults=mfg_data
            )
            if created:
                created_manufacturers += 1
                self.stdout.write(f'Created manufacturer: {manufacturer.name}')
        
        # Create basic part categories
        categories_data = [
            {'name': 'Engine', 'description': 'Complete engines and engine assemblies'},
            {'name': 'Transmission', 'description': 'Manual and automatic transmissions'},
            {'name': 'Differential', 'description': 'Front and rear differentials'},
            {'name': 'Suspension', 'description': 'Suspension components and systems'},
            {'name': 'Brakes', 'description': 'Brake components and systems'},
            {'name': 'Electrical', 'description': 'Electrical components and wiring'},
            {'name': 'Body', 'description': 'Body panels and components'},
            {'name': 'Interior', 'description': 'Interior components and trim'},
            {'name': 'Exhaust', 'description': 'Exhaust system components'},
            {'name': 'Cooling', 'description': 'Cooling system components'},
            {'name': 'Fuel System', 'description': 'Fuel system components'},
            {'name': 'Air Intake', 'description': 'Air intake system components'},
        ]
        
        # Create main categories first
        created_categories = 0
        main_categories = {}
        
        for cat_data in categories_data:
            category, created = PartCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                created_categories += 1
                self.stdout.write(f'Created category: {category.name}')
            main_categories[cat_data['name']] = category
        
        # Create some subcategories
        subcategories_data = [
            {'name': 'Long Block', 'parent': 'Engine', 'description': 'Complete engine block with heads'},
            {'name': 'Short Block', 'parent': 'Engine', 'description': 'Engine block without heads'},
            {'name': 'Cylinder Head', 'parent': 'Engine', 'description': 'Individual cylinder heads'},
            {'name': 'Intake Manifold', 'parent': 'Engine', 'description': 'Intake manifolds'},
            {'name': 'Exhaust Manifold', 'parent': 'Engine', 'description': 'Exhaust manifolds'},
            {'name': 'Oil Pan', 'parent': 'Engine', 'description': 'Engine oil pans'},
            
            {'name': 'Automatic', 'parent': 'Transmission', 'description': 'Automatic transmissions'},
            {'name': 'Manual', 'parent': 'Transmission', 'description': 'Manual transmissions'},
            {'name': 'Transfer Case', 'parent': 'Transmission', 'description': 'Transfer cases for 4WD'},
            
            {'name': 'Front Axle', 'parent': 'Differential', 'description': 'Front differential assemblies'},
            {'name': 'Rear Axle', 'parent': 'Differential', 'description': 'Rear differential assemblies'},
            
            {'name': 'Struts', 'parent': 'Suspension', 'description': 'Strut assemblies'},
            {'name': 'Shocks', 'parent': 'Suspension', 'description': 'Shock absorbers'},
            {'name': 'Springs', 'parent': 'Suspension', 'description': 'Coil and leaf springs'},
        ]
        
        for subcat_data in subcategories_data:
            parent_category = main_categories.get(subcat_data['parent'])
            if parent_category:
                subcategory, created = PartCategory.objects.get_or_create(
                    name=subcat_data['name'],
                    parent_category=parent_category,
                    defaults={'description': subcat_data['description']}
                )
                if created:
                    created_categories += 1
                    self.stdout.write(f'Created subcategory: {parent_category.name} -> {subcategory.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized database:\n'
                f'- Created {created_manufacturers} manufacturers\n'
                f'- Created {created_categories} categories'
            )
        )
