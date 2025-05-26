# This goes in: parts_interchange/apps/vehicles/management/commands/create_audi_vehicles_corrected.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle
from datetime import datetime


class Command(BaseCommand):
    help = 'Create Audi vehicle records - CORRECTED to treat S and RS models as separate models, not trims'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--years',
            type=str,
            default='2000-2025',
            help='Year range to create vehicles for (e.g., "2000-2025" or "2020")'
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of models to create (default: all)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        years_range = self.parse_years(options['years'])
        models_filter = options['models'].split(',') if options['models'] else None
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        # Get Audi make
        try:
            if not dry_run:
                audi_make = Make.objects.get(name='Audi')
            self.stdout.write('✓ Found Audi make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Audi make not found. Run: python manage.py add_brands first'))
            return
        
        # CORRECTED: S and RS models are now separate models, each with their own trim levels
        audi_vehicle_combinations = {
            # A-Series Base Models
            'A4': {
                'generations': {
                    'B8': {
                        'years': (2009, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo']
                        }
                    },
                    'B8.5': {
                        'years': (2013, 2016),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo']
                        }
                    },
                    'B9': {
                        'years': (2017, 2020),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI']
                        }
                    }
                }
            },
            
            # S4 as Separate Model
            'S4': {
                'generations': {
                    'B8': {
                        'years': (2010, 2012),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B8.5': {
                        'years': (2013, 2016),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B9': {
                        'years': (2018, 2020),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            },
            
            'A5': {
                'generations': {
                    'B8': {
                        'years': (2008, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo']
                        }
                    },
                    'B9': {
                        'years': (2017, 2020),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI']
                        }
                    }
                }
            },
            
            # S5 as Separate Model
            'S5': {
                'generations': {
                    'B8': {
                        'years': (2008, 2012),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B9': {
                        'years': (2018, 2020),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            },
            
            # RS5 as Separate Model
            'RS5': {
                'generations': {
                    'B9': {
                        'years': (2018, 2020),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['2.9L V6 TFSI Twin-Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['2.9L V6 TFSI Twin-Turbo'],
                            'Prestige': ['2.9L V6 TFSI Twin-Turbo']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['2.9L V6 TFSI Twin-Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['2.9L V6 TFSI Twin-Turbo'],
                            'Prestige': ['2.9L V6 TFSI Twin-Turbo']
                        }
                    }
                }
            },
            
            'A7': {
                'generations': {
                    'C7': {
                        'years': (2012, 2014),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'C8': {
                        'years': (2019, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            },
            
            # RS7 as Separate Model
            'RS7': {
                'generations': {
                    'C7': {
                        'years': (2014, 2018),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['4.0L V8 TFSI Twin-Turbo High Output'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['4.0L V8 TFSI Twin-Turbo High Output'],
                            'Prestige': ['4.0L V8 TFSI Twin-Turbo High Output']
                        }
                    },
                    'C8': {
                        'years': (2020, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['4.0L V8 TFSI Twin-Turbo High Output'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['4.0L V8 TFSI Twin-Turbo High Output'],
                            'Prestige': ['4.0L V8 TFSI Twin-Turbo High Output']
                        }
                    }
                }
            },
            
            'Q5': {
                'generations': {
                    '8R': {
                        'years': (2009, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo']
                        }
                    },
                    '8Y': {
                        'years': (2018, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI']
                        }
                    }
                }
            },
            
            # SQ5 as Separate Model
            'SQ5': {
                'generations': {
                    '8R': {
                        'years': (2014, 2017),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    '8Y': {
                        'years': (2018, 2025),
                        'trims': ['Premium Plus', 'Prestige'],
                        'engines': ['3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium Plus': ['3.0L V6 TFSI Turbo'],
                            'Prestige': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            }
        }
        
        # Filter models if specified
        if models_filter:
            models_filter = [m.strip() for m in models_filter]
            filtered_combinations = {}
            for model in models_filter:
                if model in audi_vehicle_combinations:
                    filtered_combinations[model] = audi_vehicle_combinations[model]
            audi_vehicle_combinations = filtered_combinations
        
        self.stdout.write(f'Creating vehicles for years: {min(years_range)}-{max(years_range)}')
        self.stdout.write(f'Processing {len(audi_vehicle_combinations)} models...')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each model
        for model_name, model_data in audi_vehicle_combinations.items():
            self.stdout.write(f'\\n📋 Processing {model_name}:')
            
            if not dry_run:
                try:
                    model_obj = Model.objects.get(make__name='Audi', name=model_name)
                except Model.DoesNotExist:
                    self.stdout.write(f'  ❌ Model {model_name} not found - run add_audi_models first')
                    error_count += 1
                    continue
            
            # Process each generation
            for generation, gen_data in model_data['generations'].items():
                gen_display = f" {generation}" if generation else ""
                if '.5' in generation:
                    gen_display += " 🔄"  # Highlight .5 refreshes
                self.stdout.write(f'  🔧 {model_name}{gen_display}:')
                
                start_year, end_year = gen_data['years']
                model_years = [y for y in years_range if start_year <= y <= end_year]
                
                if not model_years:
                    self.stdout.write(f'    ⏭️  No years in range {min(years_range)}-{max(years_range)}')
                    continue
                
                # Process each year
                for year in model_years:
                    # Process each trim/engine combination
                    for trim_name, engine_names in gen_data['trim_engine_mapping'].items():
                        for engine_name in engine_names:
                            
                            # Create vehicle record
                            if not dry_run:
                                try:
                                    # Get trim and engine objects
                                    try:
                                        trim_obj = Trim.objects.get(name=trim_name)
                                    except Trim.DoesNotExist:
                                        self.stdout.write(f'    ❌ Trim "{trim_name}" not found - run add_audi_trims_corrected first')
                                        error_count += 1
                                        continue
                                    
                                    try:
                                        engine_obj = Engine.objects.get(name=engine_name)
                                    except Engine.DoesNotExist:
                                        self.stdout.write(f'    ❌ Engine "{engine_name}" not found - run add_audi_engines first')  
                                        error_count += 1
                                        continue
                                    
                                    # Check if vehicle already exists
                                    existing = Vehicle.objects.filter(
                                        year=year,
                                        make=audi_make,
                                        model=model_obj,
                                        generation=generation,
                                        trim=trim_obj,
                                        engine=engine_obj
                                    ).exists()
                                    
                                    if existing:
                                        skipped_count += 1
                                        status = '- EXISTS'
                                    else:
                                        Vehicle.objects.create(
                                            year=year,
                                            make=audi_make,
                                            model=model_obj,
                                            generation=generation,
                                            trim=trim_obj,
                                            engine=engine_obj,
                                            is_active=True,
                                            notes=f'Generation: {generation}' if generation else ''
                                        )
                                        created_count += 1
                                        status = '✓ CREATED'
                                
                                except Exception as e:
                                    error_count += 1
                                    status = f'❌ ERROR: {str(e)}'
                            else:
                                status = '? DRY RUN'
                            
                            # Display vehicle
                            vehicle_display = f'{year} {model_name}{gen_display} {trim_name} {engine_name}'
                            self.stdout.write(f'    {status} {vehicle_display}')
        
        # Summary
        self.stdout.write('\\n' + '=' * 60)
        self.stdout.write('CORRECTED AUDI VEHICLES SUMMARY')
        self.stdout.write('=' * 60)
        
        if not dry_run:
            self.stdout.write(f'✓ Created: {created_count} vehicle records')
            self.stdout.write(f'- Existed: {skipped_count} vehicle records')
            self.stdout.write(f'❌ Errors: {error_count} records')
            self.stdout.write(f'📊 Total Processed: {created_count + skipped_count + error_count}')
        else:
            total_combinations = sum(
                len([y for y in years_range if gen_data['years'][0] <= y <= gen_data['years'][1]]) *
                sum(len(engines) for engines in gen_data['trim_engine_mapping'].values())
                for model_data in audi_vehicle_combinations.values()
                for gen_data in model_data['generations'].values()
            )
            self.stdout.write(f'📊 Would create approximately: {total_combinations} vehicle records')
        
        # Corrected model structure insights
        self.stdout.write('\\n🔍 CORRECTED MODEL STRUCTURE:')
        self.stdout.write('🔧 S and RS models are now separate models with their own trims!')
        self.stdout.write('')
        self.stdout.write('Examples of corrected structure:')
        self.stdout.write('• A4 Premium Plus 2.0T → A4 model with Premium Plus trim')
        self.stdout.write('• S4 Prestige 3.0T → S4 model with Prestige trim')
        self.stdout.write('• RS7 Premium Plus → RS7 model with Premium Plus trim')
        self.stdout.write('• SQ5 Prestige → SQ5 model with Prestige trim')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. ✅ Models correctly structured as separate entities')
        self.stdout.write('2. ✅ Each performance model gets its own trim levels') 
        self.stdout.write('3. 🔄 Create Fitment records: Parts → specific models (not trims)')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully created {created_count} CORRECTED Audi vehicle records!')
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  DRY RUN complete - run without --dry-run to create vehicles')
            )
        elif created_count == 0:
            self.stdout.write(
                self.style.WARNING('\\n⚠️  No new vehicles created - they may already exist')
            )

    def parse_years(self, year_string):
        """Parse year range string into list of years"""
        if '-' in year_string:
            start, end = map(int, year_string.split('-'))
            return list(range(start, end + 1))
        else:
            return [int(year_string)]
