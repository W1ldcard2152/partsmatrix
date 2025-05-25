# This goes in: parts_interchange/apps/vehicles/management/commands/create_acura_vehicles.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle
from datetime import datetime


class Command(BaseCommand):
    help = 'Create Acura vehicle records by combining years, models, generations, trims, and engines'

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
        
        # Get Acura make
        try:
            if not dry_run:
                acura_make = Make.objects.get(name='Acura')
            self.stdout.write('✓ Found Acura make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Acura make not found. Run: python manage.py add_brands first'))
            return
        
        # Define Acura vehicle combinations by model and generation
        acura_vehicle_combinations = {
            'Integra': {
                'generations': {
                    'Gen 3': {
                        'years': (1994, 2001),
                        'trims': ['LS', 'RS', 'GS', 'GS-R', 'Type R'],
                        'engines': ['1.8L I4 DOHC VTEC'],
                        'trim_engine_mapping': {
                            'LS': ['1.8L I4 DOHC VTEC'],  # B18B1 - 140hp
                            'RS': ['1.8L I4 DOHC VTEC'],  # B18B1 - 140hp  
                            'GS': ['1.8L I4 DOHC VTEC'],  # B18B1 - 140hp
                            'GS-R': ['1.8L I4 DOHC VTEC'],  # B18C1 - 170hp (same identifier)
                            'Type R': ['1.8L I4 DOHC VTEC']  # B18C5 - 195hp (same identifier)
                        }
                    },
                    'Gen 5': {
                        'years': (2023, 2025),
                        'trims': ['Base', 'A-Spec', 'Type-S'],
                        'engines': ['1.5L I4 DOHC VTEC Turbo', '2.0L I4 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['1.5L I4 DOHC VTEC Turbo'],
                            'A-Spec': ['1.5L I4 DOHC VTEC Turbo'],
                            'Type-S': ['2.0L I4 DOHC VTEC Turbo']
                        }
                    }
                }
            },
            'TL': {
                'generations': {
                    'Gen 2': {
                        'years': (1999, 2003),
                        'trims': ['2.5TL', '3.2TL', 'Type-S'],
                        'engines': ['2.5L I5 SOHC', '3.2L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            '2.5TL': ['2.5L I5 SOHC'],
                            '3.2TL': ['3.2L V6 SOHC VTEC'],
                            'Type-S': ['3.2L V6 SOHC VTEC']
                        }
                    },
                    'Gen 3': {
                        'years': (2004, 2008),
                        'trims': ['Base', 'Navigation', 'Type-S'],
                        'engines': ['3.2L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['3.2L V6 SOHC VTEC'],
                            'Navigation': ['3.2L V6 SOHC VTEC'],
                            'Type-S': ['3.2L V6 SOHC VTEC']
                        }
                    },
                    'Gen 4': {
                        'years': (2009, 2014),
                        'trims': ['Base', 'Technology', 'SH-AWD', 'Type-S'],
                        'engines': ['3.7L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['3.7L V6 SOHC VTEC'],
                            'Technology': ['3.7L V6 SOHC VTEC'],
                            'SH-AWD': ['3.7L V6 SOHC VTEC'],
                            'Type-S': ['3.7L V6 SOHC VTEC']
                        }
                    }
                }
            },
            'TLX': {
                'generations': {
                    'Gen 1': {
                        'years': (2015, 2020),
                        'trims': ['Base', 'Technology', 'A-Spec', 'Advance'],
                        'engines': ['2.4L I4 DOHC i-VTEC', '3.5L V6 SOHC i-VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 DOHC i-VTEC', '3.5L V6 SOHC i-VTEC'],
                            'Technology': ['2.4L I4 DOHC i-VTEC', '3.5L V6 SOHC i-VTEC'],
                            'A-Spec': ['2.4L I4 DOHC i-VTEC', '3.5L V6 SOHC i-VTEC'],
                            'Advance': ['3.5L V6 SOHC i-VTEC']
                        }
                    },
                    'Gen 2': {
                        'years': (2021, 2025),
                        'trims': ['Base', 'Technology', 'A-Spec', 'Advance', 'Type-S'],
                        'engines': ['2.0L I4 DOHC VTEC Turbo', '3.0L V6 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['2.0L I4 DOHC VTEC Turbo'],
                            'Technology': ['2.0L I4 DOHC VTEC Turbo'],
                            'A-Spec': ['2.0L I4 DOHC VTEC Turbo'],
                            'Advance': ['2.0L I4 DOHC VTEC Turbo'],
                            'Type-S': ['3.0L V6 DOHC VTEC Turbo']
                        }
                    }
                }
            },
            'MDX': {
                'generations': {
                    'Gen 1': {
                        'years': (2001, 2006),
                        'trims': ['Base', 'Touring', 'Navigation'],
                        'engines': ['3.5L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['3.5L V6 SOHC VTEC'],
                            'Touring': ['3.5L V6 SOHC VTEC'],
                            'Navigation': ['3.5L V6 SOHC VTEC']
                        }
                    },
                    'Gen 2': {
                        'years': (2007, 2013),
                        'trims': ['Base', 'Technology', 'Advance', 'Elite'],
                        'engines': ['3.7L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['3.7L V6 SOHC VTEC'],
                            'Technology': ['3.7L V6 SOHC VTEC'],
                            'Advance': ['3.7L V6 SOHC VTEC'],
                            'Elite': ['3.7L V6 SOHC VTEC']
                        }
                    },
                    'Gen 3': {
                        'years': (2014, 2020),
                        'trims': ['Base', 'Technology', 'Advance', 'Elite', 'Sport Hybrid'],
                        'engines': ['3.5L V6 SOHC i-VTEC', '3.5L V6 SOHC i-VTEC Hybrid'],
                        'trim_engine_mapping': {
                            'Base': ['3.5L V6 SOHC i-VTEC'],
                            'Technology': ['3.5L V6 SOHC i-VTEC'],
                            'Advance': ['3.5L V6 SOHC i-VTEC'],
                            'Elite': ['3.5L V6 SOHC i-VTEC'],
                            'Sport Hybrid': ['3.5L V6 SOHC i-VTEC Hybrid']
                        }
                    },
                    'Gen 4': {
                        'years': (2021, 2025),
                        'trims': ['Base', 'Technology', 'A-Spec', 'Advance', 'Type-S'],
                        'engines': ['3.5L V6 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['3.5L V6 DOHC VTEC Turbo'],
                            'Technology': ['3.5L V6 DOHC VTEC Turbo'],
                            'A-Spec': ['3.5L V6 DOHC VTEC Turbo'],
                            'Advance': ['3.5L V6 DOHC VTEC Turbo'],
                            'Type-S': ['3.5L V6 DOHC VTEC Turbo']
                        }
                    }
                }
            },
            'RDX': {
                'generations': {
                    'Gen 1': {
                        'years': (2007, 2012),
                        'trims': ['Base', 'Technology', 'Turbo'],
                        'engines': ['2.3L I4 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['2.3L I4 DOHC VTEC Turbo'],
                            'Technology': ['2.3L I4 DOHC VTEC Turbo'],
                            'Turbo': ['2.3L I4 DOHC VTEC Turbo']
                        }
                    },
                    'Gen 2': {
                        'years': (2013, 2018),
                        'trims': ['Base', 'Technology', 'AWD'],
                        'engines': ['3.5L V6 SOHC i-VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['3.5L V6 SOHC i-VTEC'],
                            'Technology': ['3.5L V6 SOHC i-VTEC'],
                            'AWD': ['3.5L V6 SOHC i-VTEC']
                        }
                    },
                    'Gen 3': {
                        'years': (2019, 2025),
                        'trims': ['Base', 'Technology', 'A-Spec', 'Advance'],
                        'engines': ['2.0L I4 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['2.0L I4 DOHC VTEC Turbo'],
                            'Technology': ['2.0L I4 DOHC VTEC Turbo'],
                            'A-Spec': ['2.0L I4 DOHC VTEC Turbo'],
                            'Advance': ['2.0L I4 DOHC VTEC Turbo']
                        }
                    }
                }
            },
            'RSX': {
                'generations': {
                    '': {  # Single generation
                        'years': (2002, 2006),
                        'trims': ['Base', 'Type-S'],
                        'engines': ['2.0L I4 DOHC i-VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['2.0L I4 DOHC i-VTEC'],  # K20A3 - 160hp
                            'Type-S': ['2.0L I4 DOHC i-VTEC']  # K20A2 - 210hp (same identifier)
                        }
                    }
                }
            },
            'TSX': {
                'generations': {
                    'Gen 1': {
                        'years': (2004, 2008),
                        'trims': ['Base', 'Navigation'],
                        'engines': ['2.4L I4 DOHC i-VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 DOHC i-VTEC'],
                            'Navigation': ['2.4L I4 DOHC i-VTEC']
                        }
                    },
                    'Gen 2': {
                        'years': (2009, 2014),
                        'trims': ['Base', 'Technology', 'Sport Wagon', 'V6'],
                        'engines': ['2.4L I4 DOHC i-VTEC', '3.5L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 DOHC i-VTEC'],
                            'Technology': ['2.4L I4 DOHC i-VTEC'],
                            'Sport Wagon': ['2.4L I4 DOHC i-VTEC'],
                            'V6': ['3.5L V6 SOHC VTEC']
                        }
                    }
                }
            },
            'ILX': {
                'generations': {
                    'Gen 1': {
                        'years': (2013, 2015),
                        'trims': ['Base', 'Hybrid', 'Dynamic'],
                        'engines': ['2.0L I4 SOHC i-VTEC', '1.5L I4 Hybrid'],
                        'trim_engine_mapping': {
                            'Base': ['2.0L I4 SOHC i-VTEC'],
                            'Hybrid': ['1.5L I4 Hybrid'],
                            'Dynamic': ['2.0L I4 SOHC i-VTEC']
                        }
                    },
                    'Gen 2': {
                        'years': (2016, 2022),
                        'trims': ['Base', 'Premium', 'Technology', 'A-Spec'],
                        'engines': ['2.4L I4 DOHC i-VTEC'],
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 DOHC i-VTEC'],
                            'Premium': ['2.4L I4 DOHC i-VTEC'],
                            'Technology': ['2.4L I4 DOHC i-VTEC'],
                            'A-Spec': ['2.4L I4 DOHC i-VTEC']
                        }
                    }
                }
            },
            'NSX': {
                'generations': {
                    'Gen 1': {
                        'years': (1991, 2005),
                        'trims': ['Coupe', 'Targa'],
                        'engines': ['3.0L V6 SOHC VTEC'],
                        'trim_engine_mapping': {
                            'Coupe': ['3.0L V6 SOHC VTEC'],
                            'Targa': ['3.0L V6 SOHC VTEC']
                        }
                    },
                    'Gen 2': {
                        'years': (2016, 2022),
                        'trims': ['Base', 'Type-S'],
                        'engines': ['3.5L V6 DOHC VTEC Hybrid'],
                        'trim_engine_mapping': {
                            'Base': ['3.5L V6 DOHC VTEC Hybrid'],
                            'Type-S': ['3.5L V6 DOHC VTEC Hybrid']
                        }
                    }
                }
            },
            'ADX': {
                'generations': {
                    '': {  # Single generation so far
                        'years': (2025, 2025),
                        'trims': ['Base', 'A-Spec Package'],
                        'engines': ['1.5L I4 DOHC VTEC Turbo'],
                        'trim_engine_mapping': {
                            'Base': ['1.5L I4 DOHC VTEC Turbo'],
                            'A-Spec Package': ['1.5L I4 DOHC VTEC Turbo']
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
                if model in acura_vehicle_combinations:
                    filtered_combinations[model] = acura_vehicle_combinations[model]
            acura_vehicle_combinations = filtered_combinations
        
        self.stdout.write(f'Creating vehicles for years: {min(years_range)}-{max(years_range)}')
        self.stdout.write(f'Processing {len(acura_vehicle_combinations)} models...')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each model
        for model_name, model_data in acura_vehicle_combinations.items():
            self.stdout.write(f'\\n📋 Processing {model_name}:')
            
            if not dry_run:
                try:
                    model_obj = Model.objects.get(make__name='Acura', name=model_name)
                except Model.DoesNotExist:
                    self.stdout.write(f'  ❌ Model {model_name} not found - run add_acura_models first')
                    error_count += 1
                    continue
            
            # Process each generation
            for generation, gen_data in model_data['generations'].items():
                gen_display = f" {generation}" if generation else ""
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
                                    trim_obj = Trim.objects.get(name=trim_name) if trim_name != 'Base' else Trim.objects.get(name='Base')
                                    engine_obj = Engine.objects.get(name=engine_name)
                                    
                                    # Check if vehicle already exists
                                    existing = Vehicle.objects.filter(
                                        year=year,
                                        make=acura_make,
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
                                            make=acura_make,
                                            model=model_obj,
                                            generation=generation,
                                            trim=trim_obj,
                                            engine=engine_obj,
                                            is_active=True
                                        )
                                        created_count += 1
                                        status = '✓ CREATED'
                                
                                except (Trim.DoesNotExist, Engine.DoesNotExist) as e:
                                    error_count += 1
                                    status = f'❌ ERROR: {str(e)}'
                            else:
                                status = '? DRY RUN'
                            
                            # Display vehicle
                            vehicle_display = f'{year} {model_name}{gen_display} {trim_name} {engine_name}'
                            self.stdout.write(f'    {status} {vehicle_display}')
        
        # Summary
        self.stdout.write('\\n' + '=' * 60)
        self.stdout.write('ACURA VEHICLES SUMMARY')
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
                for model_data in acura_vehicle_combinations.values()
                for gen_data in model_data['generations'].values()
            )
            self.stdout.write(f'📊 Would create approximately: {total_combinations} vehicle records')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Verify vehicle records: Check admin panel for accuracy')
        self.stdout.write('2. Start Parts app: python manage.py add_part_categories')
        self.stdout.write('3. Add actual parts: python manage.py add_parts --category alternator')
        self.stdout.write('4. Create fitments: Parts → Vehicle combinations')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully created {created_count} Acura vehicle records!')
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
