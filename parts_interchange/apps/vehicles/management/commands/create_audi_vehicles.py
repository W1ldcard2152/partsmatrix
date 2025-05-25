# This goes in: parts_interchange/apps/vehicles/management/commands/create_audi_vehicles.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle
from datetime import datetime


class Command(BaseCommand):
    help = 'Create Audi vehicle records by combining years, models, generations, trims, and engines including .5 refreshes'

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
        
        # Define Audi vehicle combinations by model and generation INCLUDING .5 refreshes
        audi_vehicle_combinations = {
            'A3': {
                'generations': {
                    '8L': {
                        'years': (1996, 2003),
                        'trims': ['1.8T', '1.8T quattro'],
                        'engines': ['1.8L I4 Turbo'],
                        'trim_engine_mapping': {
                            '1.8T': ['1.8L I4 Turbo'],
                            '1.8T quattro': ['1.8L I4 Turbo']
                        }
                    },
                    '8P': {
                        'years': (2006, 2013),
                        'trims': ['2.0T', '3.2 quattro', 'TDI'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.2L V6 FSI', '2.0L I4 TDI Turbo'],
                        'trim_engine_mapping': {
                            '2.0T': ['2.0L I4 TFSI Turbo'],
                            '3.2 quattro': ['3.2L V6 FSI'],
                            'TDI': ['2.0L I4 TDI Turbo']
                        }
                    },
                    '8V': {
                        'years': (2015, 2020),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S3'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo High Output'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo'],
                            'S3': ['2.0L I4 TFSI Turbo High Output']
                        }
                    },
                    '8Y': {
                        'years': (2021, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S3', 'RS3'],
                        'engines': ['1.4L I4 TFSI Turbo', '2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo High Output', '2.5L I5 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['1.4L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo'],
                            'S3': ['2.0L I4 TFSI Turbo High Output'],
                            'RS3': ['2.5L I5 TFSI Turbo']
                        }
                    }
                }
            },
            'A4': {
                'generations': {
                    'B5': {
                        'years': (1996, 2001),
                        'trims': ['1.8T', '1.8T quattro'],
                        'engines': ['1.8L I4 Turbo'],
                        'trim_engine_mapping': {
                            '1.8T': ['1.8L I4 Turbo'],
                            '1.8T quattro': ['1.8L I4 Turbo']
                        }
                    },
                    'B6': {
                        'years': (2002, 2005),
                        'trims': ['1.8T', '1.8T quattro'],
                        'engines': ['1.8L I4 Turbo'],
                        'trim_engine_mapping': {
                            '1.8T': ['1.8L I4 Turbo'],
                            '1.8T quattro': ['1.8L I4 Turbo']
                        }
                    },
                    'B7': {
                        'years': (2006, 2008),
                        'trims': ['2.0T', '3.2 quattro', 'S4'],
                        'engines': ['2.0L I4 FSI', '3.2L V6 FSI', '4.2L V8 FSI'],
                        'trim_engine_mapping': {
                            '2.0T': ['2.0L I4 FSI'],
                            '3.2 quattro': ['3.2L V6 FSI'],
                            'S4': ['4.2L V8 FSI']
                        }
                    },
                    'B8': {
                        'years': (2009, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S4'],
                        'engines': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo'],
                            'S4': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B8.5': {
                        'years': (2013, 2016),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S4'],
                        'engines': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium': ['1.8L I4 TFSI Turbo', '2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['2.0L I4 TFSI Turbo'],
                            'S4': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B9': {
                        'years': (2017, 2020),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S4'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'S4': ['3.0L V6 TFSI Turbo']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2023),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S4'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'S4': ['3.0L V6 TFSI Turbo']
                        }
                    },
                    'B10': {
                        'years': (2024, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S4'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'S4': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            },
            'A5': {
                'generations': {
                    'B8': {
                        'years': (2008, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S5'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged'],
                            'S5': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    'B8.5': {
                        'years': (2013, 2016),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S5', 'RS5'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged', '4.2L V8 FSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged'],
                            'S5': ['3.0L V6 TFSI Supercharged'],
                            'RS5': ['4.2L V8 FSI']
                        }
                    },
                    'B9': {
                        'years': (2017, 2020),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S5', 'RS5'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '3.0L V6 TFSI Turbo', '2.9L V6 TFSI Twin-Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'S5': ['3.0L V6 TFSI Turbo'],
                            'RS5': ['2.9L V6 TFSI Twin-Turbo']
                        }
                    },
                    'B9.5': {
                        'years': (2021, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'S5', 'RS5'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '3.0L V6 TFSI Turbo', '2.9L V6 TFSI Twin-Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'S5': ['3.0L V6 TFSI Turbo'],
                            'RS5': ['2.9L V6 TFSI Twin-Turbo']
                        }
                    }
                }
            },
            'Q5': {
                'generations': {
                    '8R': {
                        'years': (2009, 2012),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'SQ5'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged'],
                            'SQ5': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    '8R.5': {
                        'years': (2013, 2017),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'SQ5'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo', '3.0L V6 TFSI Supercharged'],
                            'Prestige': ['3.0L V6 TFSI Supercharged'],
                            'SQ5': ['3.0L V6 TFSI Supercharged']
                        }
                    },
                    '8Y': {
                        'years': (2018, 2021),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', '50 TFSI e', 'SQ5'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '2.0L I4 TFSI Hybrid', '3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            '50 TFSI e': ['2.0L I4 TFSI Hybrid'],
                            'SQ5': ['3.0L V6 TFSI Turbo']
                        }
                    },
                    '8Y.5': {
                        'years': (2022, 2025),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', '50 TFSI e', 'SQ5'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo 45 TFSI', '2.0L I4 TFSI Hybrid', '3.0L V6 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            'Prestige': ['2.0L I4 TFSI Turbo 45 TFSI'],
                            '50 TFSI e': ['2.0L I4 TFSI Hybrid'],
                            'SQ5': ['3.0L V6 TFSI Turbo']
                        }
                    }
                }
            },
            'TT': {
                'generations': {
                    '8N': {
                        'years': (2000, 2006),
                        'trims': ['1.8T', '1.8T quattro'],
                        'engines': ['1.8L I4 Turbo'],
                        'trim_engine_mapping': {
                            '1.8T': ['1.8L I4 Turbo'],
                            '1.8T quattro': ['1.8L I4 Turbo']
                        }
                    },
                    '8J': {
                        'years': (2008, 2010),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'TTS'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.2L V6 FSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['3.2L V6 FSI'],
                            'TTS': ['2.0L I4 TFSI Turbo High Output']
                        }
                    },
                    '8J.5': {
                        'years': (2011, 2015),
                        'trims': ['Premium', 'Premium Plus', 'Prestige', 'TTS'],
                        'engines': ['2.0L I4 TFSI Turbo', '3.2L V6 FSI'],
                        'trim_engine_mapping': {
                            'Premium': ['2.0L I4 TFSI Turbo'],
                            'Premium Plus': ['2.0L I4 TFSI Turbo'],
                            'Prestige': ['3.2L V6 FSI'],
                            'TTS': ['2.0L I4 TFSI Turbo High Output']
                        }
                    },
                    '8S': {
                        'years': (2016, 2018),
                        'trims': ['TT', 'TTS', 'TT RS'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo High Output', '2.5L I5 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'TT': ['2.0L I4 TFSI Turbo'],
                            'TTS': ['2.0L I4 TFSI Turbo High Output'],
                            'TT RS': ['2.5L I5 TFSI Turbo']
                        }
                    },
                    '8S.5': {
                        'years': (2019, 2023),
                        'trims': ['TT', 'TTS', 'TT RS'],
                        'engines': ['2.0L I4 TFSI Turbo', '2.0L I4 TFSI Turbo High Output', '2.5L I5 TFSI Turbo'],
                        'trim_engine_mapping': {
                            'TT': ['2.0L I4 TFSI Turbo'],
                            'TTS': ['2.0L I4 TFSI Turbo High Output'],
                            'TT RS': ['2.5L I5 TFSI Turbo']
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
                                        # If combined trim doesn't exist, try to create it
                                        if ' quattro' in trim_name:
                                            # Handle combined trims like "1.8T quattro"
                                            base_trim = trim_name.replace(' quattro', '')
                                            description = f'{base_trim} with all-wheel drive'
                                            trim_obj = Trim.objects.create(
                                                name=trim_name,
                                                description=description
                                            )
                                            self.stdout.write(f'    ✨ CREATED TRIM: {trim_name}')
                                        else:
                                            # Re-raise the exception if it's not a quattro variant
                                            raise
                                    
                                    engine_obj = Engine.objects.get(name=engine_name)
                                    
                                    # Check if vehicle already exists
                                    existing = Vehicle.objects.filter(
                                        year=year,
                                        make=audi_make,
                                        model=model_obj,
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
                                            trim=trim_obj,
                                            engine=engine_obj,
                                            is_active=True,
                                            notes=f'Generation: {generation}' if generation else ''
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
        self.stdout.write('AUDI VEHICLES SUMMARY (.5 REFRESH SUPPORT)')
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
        
        # Model insights
        self.stdout.write('\\n🔍 AUDI VEHICLE INSIGHTS (.5 GENERATION SUPPORT):')
        self.stdout.write('Platform Evolution with Mid-Cycle Refreshes:')
        self.stdout.write('• A4: B5→B6→B7→B8/B8.5→B9/B9.5→B10 (.5 refreshes every 3-4 years)')
        self.stdout.write('• A5: B8/B8.5→B9/B9.5 (significant .5 updates with RS5 introduction)')
        self.stdout.write('• Q5: 8R/8R.5→8Y/8Y.5 (.5 refresh includes updated infotainment)')
        self.stdout.write('• TT: 8N→8J/8J.5→8S/8S.5 (styling and interior updates in .5)')
        
        self.stdout.write('\\n.5 Refresh Significance:')
        self.stdout.write('• Parts Compatibility: .5 generations often require different:')
        self.stdout.write('  - Headlights (LED upgrades, matrix lighting)')
        self.stdout.write('  - Bumpers and trim pieces (styling updates)')
        self.stdout.write('  - Interior components (MMI system upgrades)')
        self.stdout.write('  - Electrical components (updated wiring harnesses)')
        
        self.stdout.write('\\nKey .5 Refresh Examples:')
        self.stdout.write('• B8.5 (2013-2016): New MMI, LED DRLs, updated grilles')
        self.stdout.write('• B9.5 (2021+): Digital cockpit updates, new bumpers')
        self.stdout.write('• 8R.5 Q5: Updated infotainment, exterior styling changes')
        self.stdout.write('• 8S.5 TT: Final styling updates before discontinuation')
        
        # Next steps
        self.stdout.write('\\n📋 NEXT STEPS:')
        self.stdout.write('1. Verify vehicle records: Check admin panel for .5 generation accuracy')
        self.stdout.write('2. Parts compatibility: .5 refreshes will need separate fitment records')
        self.stdout.write('3. Add more models: Expand to A6, A7, A8, Q7, Q8 with .5 support')
        self.stdout.write('4. Create fitments: Map parts to specific generations (B8 vs B8.5)')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\\n🎉 Successfully created {created_count} Audi vehicle records with .5 generation support!')
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
