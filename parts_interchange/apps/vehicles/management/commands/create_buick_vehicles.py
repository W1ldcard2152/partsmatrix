from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle
from datetime import datetime


class Command(BaseCommand):
    help = 'Create Buick vehicle records by combining years, models, generations, trims, and engines including mid-cycle refreshes (facelifts)'

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
        
        # Get Buick make
        try:
            if not dry_run:
                buick_make = Make.objects.get(name='Buick')
            self.stdout.write('✓ Found Buick make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('Buick make not found. Run: python manage.py add_brands first'))
            return
        
        # Define Buick vehicle combinations by model and generation
        buick_vehicle_combinations = {
            'LaCrosse': {
                'generations': {
                    'First Gen': {
                        'years': (2005, 2009),
                        'trim_engine_mapping': {
                            'CX': ['3.8L V6 L36'],
                            'CXL': ['3.8L V6 L36'],
                            'CXS': ['3.6L V6 LY7'],
                        }
                    },
                    'Second Gen': {
                        'years': (2010, 2016),
                        'trim_engine_mapping': {
                            'CX': ['2.4L I4 LAF', '3.6L V6 LLT'],
                            'CXL': ['2.4L I4 LAF', '3.6L V6 LLT'],
                            'Premium': ['3.6L V6 LFX'],
                        }
                    },
                    'Third Gen': {
                        'years': (2017, 2019),
                        'trim_engine_mapping': {
                            'Base': ['2.5L I4 LCV'],
                            'Preferred': ['3.6L V6 LGX'],
                            'Essence': ['3.6L V6 LGX'],
                        }
                    }
                }
            },
            'Regal': {
                'generations': {
                    'Fourth Gen': { # Rebadged Opel Insignia
                        'years': (2011, 2013),
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 LAF'],
                            'Turbo': ['2.0L I4 LHU Turbo'],
                            'GS': ['2.0L I4 LHU Turbo'],
                        }
                    },
                    'Fourth Gen Facelift': {
                        'years': (2014, 2017),
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 LAF'],
                            'Turbo': ['2.0L I4 LTG Turbo'],
                            'GS': ['2.0L I4 LTG Turbo'],
                        }
                    },
                    'Fifth Gen': { # Regal Sportback/TourX
                        'years': (2018, 2020),
                        'trim_engine_mapping': {
                            'Sportback': ['2.0L I4 LTG Turbo'],
                            'TourX': ['2.0L I4 LTG Turbo'],
                        }
                    }
                }
            },
            'Enclave': {
                'generations': {
                    'First Gen': {
                        'years': (2008, 2012),
                        'trim_engine_mapping': {
                            'CX': ['3.6L V6 LLT'],
                            'CXL': ['3.6L V6 LLT'],
                        }
                    },
                    'First Gen Facelift': {
                        'years': (2013, 2017),
                        'trim_engine_mapping': {
                            'Convenience': ['3.6L V6 LFX'],
                            'Leather': ['3.6L V6 LFX'],
                            'Premium': ['3.6L V6 LFX'],
                        }
                    },
                    'Second Gen': {
                        'years': (2018, 2025),
                        'trim_engine_mapping': {
                            'Essence': ['3.6L V6 LGX'],
                            'Premium': ['3.6L V6 LGX'],
                            'Avenir': ['3.6L V6 LGX'],
                        }
                    }
                }
            },
            'Encore': {
                'generations': {
                    'First Gen': {
                        'years': (2013, 2016),
                        'trim_engine_mapping': {
                            'Base': ['1.4L I4 LUJ Turbo'],
                        }
                    },
                    'First Gen Facelift': {
                        'years': (2017, 2022),
                        'trim_engine_mapping': {
                            'Base': ['1.4L I4 LE2 Turbo'],
                        }
                    }
                }
            },
            'Encore GX': {
                'generations': {
                    'First Gen': {
                        'years': (2020, 2023),
                        'trim_engine_mapping': {
                            'Preferred': ['1.2L I3 LIH Turbo', '1.3L I3 L3T Turbo'],
                        }
                    },
                    'First Gen Facelift': {
                        'years': (2024, 2025),
                        'trim_engine_mapping': {
                            'Preferred': ['1.2L I3 LIH Turbo', '1.3L I3 L3T Turbo'],
                        }
                    }
                }
            },
            'Envision': {
                'generations': {
                    'First Gen': {
                        'years': (2016, 2020),
                        'trim_engine_mapping': {
                            'Preferred': ['2.5L I4 LCV', '2.0L I4 LTG Turbo'],
                        }
                    },
                    'Second Gen': {
                        'years': (2021, 2025),
                        'trim_engine_mapping': {
                            'Preferred': ['2.0L I4 LSY Turbo'],
                            'Essence': ['2.0L I4 LSY Turbo'],
                        }
                    }
                }
            },
            'Cascada': {
                'generations': {
                    'First Gen': {
                        'years': (2016, 2019),
                        'trim_engine_mapping': {
                            'Base': ['1.6L I4 LWC Turbo'],
                        }
                    }
                }
            },
            'Verano': {
                'generations': {
                    'First Gen': {
                        'years': (2012, 2017),
                        'trim_engine_mapping': {
                            'Base': ['2.4L I4 LEA'],
                            'Turbo': ['2.0L I4 LTG Turbo'],
                        }
                    }
                }
            },
            'Lucerne': {
                'generations': {
                    'First Gen': {
                        'years': (2006, 2011),
                        'trim_engine_mapping': {
                            'CX': ['3.8L V6 L36'],
                            'CXL': ['3.8L V6 L36', '4.6L V8 LH2'],
                            'CXL Special Edition': ['3.8L V6 L36'],
                            'Super': ['4.6L V8 LH2'],
                        }
                    }
                }
            },
            'Rendezvous': {
                'generations': {
                    'First Gen': {
                        'years': (2002, 2007),
                        'trim_engine_mapping': {
                            'CX': ['3.4L V6 LA1'],
                            'CXL': ['3.4L V6 LA1', '3.6L V6 LY7'],
                        }
                    }
                }
            },
            'Rainier': {
                'generations': {
                    'First Gen': {
                        'years': (2004, 2007),
                        'trim_engine_mapping': {
                            'CXL': ['4.2L I6 LL8'],
                            'CXL Plus': ['5.3L V8 LM4'],
                        }
                    }
                }
            },
            'Terraza': {
                'generations': {
                    'First Gen': {
                        'years': (2005, 2007),
                        'trim_engine_mapping': {
                            'CX': ['3.5L V6 LX9'],
                            'CXL': ['3.5L V6 LX9', '3.9L V6 LZ9'],
                        }
                    }
                }
            },
            'LeSabre': {
                'generations': {
                    'Eighth Gen': {
                        'years': (2000, 2005),
                        'trim_engine_mapping': {
                            'Custom': ['3.8L V6 L36'],
                            'Limited': ['3.8L V6 L36'],
                        }
                    }
                }
            },
            'Park Avenue': {
                'generations': {
                    'Second Gen': {
                        'years': (2000, 2005),
                        'trim_engine_mapping': {
                            'Base': ['3.8L V6 L36'],
                            'Ultra': ['3.8L V6 L67 Supercharged'],
                        }
                    }
                }
            },
            'Century': {
                'generations': {
                    'Sixth Gen': {
                        'years': (2000, 2005),
                        'trim_engine_mapping': {
                            'Custom': ['3.1L V6 LG8'],
                            'Limited': ['3.1L V6 LG8'],
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
                if model in buick_vehicle_combinations:
                    filtered_combinations[model] = buick_vehicle_combinations[model]
            buick_vehicle_combinations = filtered_combinations
        
        self.stdout.write(f'Creating vehicles for years: {min(years_range)}-{max(years_range)}')
        self.stdout.write(f'Processing {len(buick_vehicle_combinations)} models...')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each model
        for model_name, model_data in buick_vehicle_combinations.items():
            self.stdout.write(f'\n📋 Processing {model_name}:')
            
            if not dry_run:
                try:
                    model_obj = Model.objects.get(make__name='Buick', name=model_name)
                except Model.DoesNotExist:
                    self.stdout.write(f'  ❌ Model {model_name} not found - run add_buick_models first')
                    error_count += 1
                    continue
            
            # Process each generation
            for generation, gen_data in model_data['generations'].items():
                gen_display = f" {generation}" if generation else ""
                if 'Facelift' in generation:
                    gen_display += " 🔄"  # Highlight mid-cycle refreshes
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
                                    trim_obj = Trim.objects.get(name=trim_name)
                                    engine_obj = Engine.objects.get(name=engine_name)
                                    
                                    # Check if vehicle already exists
                                    existing = Vehicle.objects.filter(
                                        year=year,
                                        make=buick_make,
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
                                            make=buick_make,
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
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('BUICK VEHICLES SUMMARY (MID-CYCLE REFRESH SUPPORT)')
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
                for model_data in buick_vehicle_combinations.values()
                for gen_data in model_data['generations'].values()
            )
            self.stdout.write(f'📊 Would create approximately: {total_combinations} vehicle records')
        
        # Model insights
        self.stdout.write('\n🔍 BUICK VEHICLE INSIGHTS (MID-CYCLE REFRESH SUPPORT):')
        self.stdout.write('Buick Platform Evolution with Mid-Cycle Refreshes:')
        self.stdout.write('• Enclave: First Gen→First Gen Facelift→Second Gen')
        self.stdout.write('• Regal: Fourth Gen→Fourth Gen Facelift→Fifth Gen')
        
        self.stdout.write('\nMid-Cycle Refresh Significance:')
        self.stdout.write('• Parts Compatibility: Mid-cycle refreshes often require different:')
        self.stdout.write('  - Exterior styling (grilles, bumpers, lights)')
        self.stdout.write('  - Interior updates (infotainment, trim)')
        self.stdout.write('  - Powertrain refinements (engine/transmission updates)')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Verify vehicle records: Check admin panel for facelift generation accuracy')
        self.stdout.write('2. Parts compatibility: Mid-cycle refreshes will need separate fitment records')
        self.stdout.write('3. Add more models: Expand to other historical or future models as needed')
        self.stdout.write('4. Create fitments: Map parts to specific generations (e.g., First Gen vs First Gen Facelift)')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully created {created_count} Buick vehicle records with mid-cycle refresh support!')
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN complete - run without --dry-run to create vehicles')
            )
        elif created_count == 0:
            self.stdout.write(
                self.style.WARNING('\n⚠️  No new vehicles created - they may already exist')
            )

    def parse_years(self, year_string):
        """Parse year range string into list of years"""
        if '-' in year_string:
            start, end = map(int, year_string.split('-'))
            return list(range(start, end + 1))
        else:
            return [int(year_string)]
