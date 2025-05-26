# This goes in: parts_interchange/apps/vehicles/management/commands/create_bmw_vehicles.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.vehicles.models import Make, Model, Engine, Trim, Vehicle
from datetime import datetime


class Command(BaseCommand):
    help = 'Create BMW vehicle records by combining years, models, generations, trims, and engines including LCI refreshes'

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
        
        # Get BMW make
        try:
            if not dry_run:
                bmw_make = Make.objects.get(name='BMW')
            self.stdout.write('✓ Found BMW make')
        except Make.DoesNotExist:
            self.stdout.write(self.style.ERROR('BMW make not found. Run: python manage.py add_brands first'))
            return
        
        # Define BMW vehicle combinations by model and generation INCLUDING LCI refreshes
        bmw_vehicle_combinations = {
            '1 Series': {
                'generations': {
                    'E87': { # Hatchback (Europe)
                        'years': (2004, 2007),
                        'trim_engine_mapping': {
                            '118i': ['2.0L I4 N46'],
                            '120i': ['2.0L I4 N46'],
                            '125i': ['2.5L I6 N52'],
                        }
                    },
                    'E82/E88': { # Coupe/Convertible (Global)
                        'years': (2008, 2013),
                        'trim_engine_mapping': {
                            '128i': ['3.0L I6 N52'],
                            '135i': ['3.0L I6 N54 Twin-Turbo', '3.0L I6 N55 Single-Turbo'],
                            '1M Coupe': ['3.2L I6 S54'], # Corrected to S54
                        }
                    },
                    'F20': { # Hatchback (Europe)
                        'years': (2012, 2014),
                        'trim_engine_mapping': {
                            '118i': ['1.5L I3 B38 Turbo'],
                            '120i': ['2.0L I4 B48 Turbo'],
                            '125i': ['2.0L I4 B48 Turbo'],
                            'M135i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'F20 LCI': { # Hatchback (Europe)
                        'years': (2015, 2019),
                        'trim_engine_mapping': {
                            '118i': ['1.5L I3 B38 Turbo'],
                            '120i': ['2.0L I4 B48 Turbo'],
                            '125i': ['2.0L I4 B48 Turbo'],
                            'M140i': ['3.0L I6 B58 Single-Turbo'],
                        }
                    },
                    'F40': { # Hatchback (FWD, Europe)
                        'years': (2019, 2025),
                        'trim_engine_mapping': {
                            '118i': ['1.5L I3 B38 Turbo'],
                            '120i': ['2.0L I4 B48 Turbo'],
                            'M135i': ['2.0L I4 B48 Turbo'],
                        }
                    }
                }
            },
            '2 Series': {
                'generations': {
                    'F22/F23': { # Coupe/Convertible
                        'years': (2014, 2017),
                        'trim_engine_mapping': {
                            '228i': ['2.0L I4 N20 Turbo'],
                            '230i': ['2.0L I4 B46 Turbo'],
                            '235i': ['3.0L I6 N55 Single-Turbo'],
                            'M235i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'F22/F23 LCI': { # Coupe/Convertible
                        'years': (2018, 2021),
                        'trim_engine_mapping': {
                            '230i': ['2.0L I4 B46 Turbo'],
                            'M240i': ['3.0L I6 B58 Single-Turbo'],
                        }
                    },
                    'F45/F46': { # Active Tourer/Gran Tourer (FWD, Europe)
                        'years': (2014, 2017),
                        'trim_engine_mapping': {
                            '218i': ['1.5L I3 B38 Turbo'],
                            '220i': ['2.0L I4 B48 Turbo'],
                            '225i': ['2.0L I4 B48 Turbo'],
                            '225xe': ['1.5L I3 B38 Hybrid'],
                        }
                    },
                    'F44 Gran Coupe': { # FWD Gran Coupe
                        'years': (2020, 2025),
                        'trim_engine_mapping': {
                            '228i': ['2.0L I4 B46 Turbo'],
                            'M235i': ['2.0L I4 B48 Turbo'],
                        }
                    },
                    'G42': { # Coupe
                        'years': (2022, 2025),
                        'trim_engine_mapping': {
                            '230i': ['2.0L I4 B46 Turbo'],
                            'M240i': ['3.0L I6 B58 High Output'],
                        }
                    }
                }
            },
            '3 Series': {
                'generations': {
                    'E46': {
                        'years': (2000, 2006),
                        'trim_engine_mapping': {
                            '325i': ['2.5L I6 N52'],
                            '330i NA': ['3.0L I6 N52'],
                        }
                    },
                    'E90': {
                        'years': (2006, 2008),
                        'trim_engine_mapping': {
                            '325i': ['2.5L I6 N52'],
                            '330i': ['3.0L I6 N52'],
                            '335i': ['3.0L I6 N54 Twin-Turbo']
                        }
                    },
                    'E90 LCI': {
                        'years': (2009, 2011),
                        'trim_engine_mapping': {
                            '328i': ['3.0L I6 N52'],
                            '335i': ['3.0L I6 N55 Single-Turbo']
                        }
                    },
                    'F30': {
                        'years': (2012, 2015),
                        'trim_engine_mapping': {
                            '320i': ['2.0L I4 N20 Turbo'],
                            '328i': ['2.0L I4 N20 Turbo'],
                            '335i': ['3.0L I6 N55 Single-Turbo']
                        }
                    },
                    'F30 LCI': {
                        'years': (2016, 2018),
                        'trim_engine_mapping': {
                            '320i': ['2.0L I4 B46 Turbo'],
                            '330i': ['2.0L I4 B46 Turbo'],
                            '340i': ['3.0L I6 B58 Single-Turbo'],
                            '330e': ['2.0L I4 B46 Hybrid']
                        }
                    },
                    'G20': {
                        'years': (2019, 2022),
                        'trim_engine_mapping': {
                            '330i': ['2.0L I4 B46 Turbo'],
                            'M340i': ['3.0L I6 B58 High Output'],
                            '330e': ['2.0L I4 B46 Hybrid']
                        }
                    },
                    'G20 LCI': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            '330i': ['2.0L I4 B46 Turbo'],
                            'M340i': ['3.0L I6 B58 High Output'],
                            '330e': ['2.0L I4 B46 Hybrid']
                        }
                    }
                }
            },
            'M3': {
                'generations': {
                    'E46 M3': {
                        'years': (2000, 2006),
                        'trim_engine_mapping': {
                            'M3': ['3.2L I6 S54'],
                        }
                    },
                    'E90 M3': {
                        'years': (2007, 2013),
                        'trim_engine_mapping': {
                            'M3': ['4.0L V8 S65 High-Rev'],
                        }
                    },
                    'F80 M3': {
                        'years': (2014, 2020),
                        'trim_engine_mapping': {
                            'M3': ['3.0L I6 S55 Twin-Turbo'],
                            'M3 Competition': ['3.0L I6 S55 Twin-Turbo'],
                            'M3 CS': ['3.0L I6 S55 Twin-Turbo'],
                        }
                    },
                    'G80 M3': {
                        'years': (2021, 2025),
                        'trim_engine_mapping': {
                            'M3': ['3.0L I6 S58 Twin-Turbo'],
                            'M3 Competition': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    }
                }
            },
            '4 Series': {
                'generations': {
                    'F32': {
                        'years': (2014, 2016),
                        'trim_engine_mapping': {
                            '428i': ['2.0L I4 N20 Turbo'],
                            '435i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'F32 LCI': {
                        'years': (2017, 2020),
                        'trim_engine_mapping': {
                            '430i': ['2.0L I4 B46 Turbo'],
                            '440i': ['3.0L I6 B58 Single-Turbo'],
                        }
                    },
                    'G22': {
                        'years': (2021, 2025),
                        'trim_engine_mapping': {
                            '430i': ['2.0L I4 B46 Turbo'],
                            'M440i': ['3.0L I6 B58 High Output'],
                        }
                    }
                }
            },
            'M4': {
                'generations': {
                    'F82 M4': {
                        'years': (2014, 2020),
                        'trim_engine_mapping': {
                            'M4': ['3.0L I6 S55 Twin-Turbo'],
                            'M4 Competition': ['3.0L I6 S55 Twin-Turbo'],
                            'M4 CS': ['3.0L I6 S55 Twin-Turbo'],
                        }
                    },
                    'G82 M4': {
                        'years': (2021, 2025),
                        'trim_engine_mapping': {
                            'M4': ['3.0L I6 S58 Twin-Turbo'],
                            'M4 Competition': ['3.0L I6 S58 Twin-Turbo'],
                            'M4 CSL': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    }
                }
            },
            '5 Series': {
                'generations': {
                    'E39': {
                        'years': (2000, 2003),
                        'trim_engine_mapping': {
                            '525i': ['2.5L I6 N52'],
                            '530i NA': ['3.0L I6 N52'],
                        }
                    },
                    'E60': {
                        'years': (2004, 2007),
                        'trim_engine_mapping': {
                            '525i': ['2.5L I6 N52'],
                            '530i': ['3.0L I6 N52'],
                            '545i': ['4.4L V8 N62'],
                        }
                    },
                    'E60 LCI': {
                        'years': (2008, 2010),
                        'trim_engine_mapping': {
                            '528i': ['3.0L I6 N52'],
                            '535i': ['3.0L I6 N54 Twin-Turbo'],
                            '550i': ['4.4L V8 N62'],
                        }
                    },
                    'F10': {
                        'years': (2011, 2013),
                        'trim_engine_mapping': {
                            '528i': ['2.0L I4 N20 Turbo'],
                            '535i': ['3.0L I6 N55 Single-Turbo'],
                            '550i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F10 LCI': {
                        'years': (2014, 2016),
                        'trim_engine_mapping': {
                            '528i': ['2.0L I4 N20 Turbo'],
                            '535i': ['3.0L I6 N55 Single-Turbo'],
                            '550i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'G30': {
                        'years': (2017, 2020),
                        'trim_engine_mapping': {
                            '530i': ['2.0L I4 B46 Turbo'],
                            '540i': ['3.0L I6 B58 Single-Turbo'],
                            '530e': ['2.0L I4 B46 Hybrid'],
                            'M550i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    },
                    'G30 LCI': {
                        'years': (2021, 2023),
                        'trim_engine_mapping': {
                            '530i': ['2.0L I4 B46 Turbo'],
                            '540i': ['3.0L I6 B58 Single-Turbo'],
                            '530e': ['2.0L I4 B46 Hybrid'],
                            '545e': ['3.0L I6 B58 Hybrid'],
                            'M550i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    },
                    'G60': { # New generation
                        'years': (2024, 2025),
                        'trim_engine_mapping': {
                            '530i': ['2.0L I4 B48 Turbo'],
                            '540i': ['3.0L I6 B58 High Output'],
                            '550e': ['3.0L I6 B58 Hybrid'],
                            'M60i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'M5': {
                'generations': {
                    'E39 M5': {
                        'years': (2000, 2003),
                        'trim_engine_mapping': {
                            'M5': ['5.0L V8 S62'],
                        }
                    },
                    'E60 M5': {
                        'years': (2005, 2010),
                        'trim_engine_mapping': {
                            'M5 V10': ['5.0L V10 S85'],
                        }
                    },
                    'F10 M5': {
                        'years': (2011, 2017),
                        'trim_engine_mapping': {
                            'M5': ['4.4L V8 S63 Twin-Turbo'],
                            'M5 Competition': ['4.4L V8 S63 Twin-Turbo'],
                        }
                    },
                    'F90 M5': {
                        'years': (2018, 2025),
                        'trim_engine_mapping': {
                            'M5': ['4.4L V8 S63TU Twin-Turbo'],
                            'M5 Competition': ['4.4L V8 S63TU Twin-Turbo'],
                            'M5 CS': ['4.4L V8 S63TU Twin-Turbo'],
                        }
                    }
                }
            },
            '6 Series': {
                'generations': {
                    'E63': {
                        'years': (2004, 2007),
                        'trim_engine_mapping': {
                            '645Ci': ['4.4L V8 N62'],
                            '650i': ['4.8L V8 N62'],
                        }
                    },
                    'E63 LCI': {
                        'years': (2008, 2010),
                        'trim_engine_mapping': {
                            '650i': ['4.8L V8 N62'],
                        }
                    },
                    'F12': {
                        'years': (2011, 2014),
                        'trim_engine_mapping': {
                            '640i': ['3.0L I6 N55 Single-Turbo'],
                            '650i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F12 LCI': {
                        'years': (2015, 2018),
                        'trim_engine_mapping': {
                            '640i': ['3.0L I6 N55 Single-Turbo'],
                            '650i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'G32': { # Gran Turismo
                        'years': (2018, 2025),
                        'trim_engine_mapping': {
                            '640i': ['3.0L I6 B58 Single-Turbo'],
                        }
                    }
                }
            },
            'M6': {
                'generations': {
                    'E63 M6': {
                        'years': (2006, 2010),
                        'trim_engine_mapping': {
                            'M6': ['5.0L V10 S85'],
                        }
                    },
                    'F12 M6': {
                        'years': (2012, 2018),
                        'trim_engine_mapping': {
                            'M6': ['4.4L V8 S63 Twin-Turbo'],
                            'M6 Competition': ['4.4L V8 S63 Twin-Turbo'],
                        }
                    }
                }
            },
            '7 Series': {
                'generations': {
                    'E65': {
                        'years': (2002, 2005),
                        'trim_engine_mapping': {
                            '745i': ['4.4L V8 N62'],
                            '760i': ['6.0L V12 N73'],
                        }
                    },
                    'E65 LCI': {
                        'years': (2006, 2008),
                        'trim_engine_mapping': {
                            '750i': ['4.8L V8 N62'],
                            '760i': ['6.0L V12 N73'],
                        }
                    },
                    'F01': {
                        'years': (2009, 2012),
                        'trim_engine_mapping': {
                            '740i': ['3.0L I6 N54 Twin-Turbo'],
                            '750i': ['4.4L V8 N63 Twin-Turbo'],
                            '760i': ['6.0L V12 N74 Twin-Turbo'],
                        }
                    },
                    'F01 LCI': {
                        'years': (2013, 2015),
                        'trim_engine_mapping': {
                            '740i': ['3.0L I6 N55 Single-Turbo'],
                            '750i': ['4.4L V8 N63 Twin-Turbo'],
                            '760i': ['6.0L V12 N74 Twin-Turbo'],
                        }
                    },
                    'G11': {
                        'years': (2016, 2019),
                        'trim_engine_mapping': {
                            '740i': ['3.0L I6 B58 Single-Turbo'],
                            '750i': ['4.4L V8 N63TU Twin-Turbo'],
                            '745e': ['3.0L I6 B58 Hybrid'],
                            'M760i': ['6.6L V12 N74 Twin-Turbo'],
                        }
                    },
                    'G11 LCI': {
                        'years': (2020, 2022),
                        'trim_engine_mapping': {
                            '740i': ['3.0L I6 B58 Single-Turbo'],
                            '750i': ['4.4L V8 N63TU Twin-Turbo'],
                            '745e': ['3.0L I6 B58 Hybrid'],
                            'M760i': ['6.6L V12 N74 Twin-Turbo'],
                        }
                    },
                    'G70': { # New generation
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            '740i': ['3.0L I6 B58 High Output'],
                            '760i': ['4.4L V8 N63TU Twin-Turbo'],
                            'i7 xDrive60': ['eDrive60 Dual Motor Electric'],
                            'i7 M70': ['eDrive M70 Dual Motor Electric'],
                        }
                    }
                }
            },
            '8 Series': {
                'generations': {
                    'E31': {
                        'years': (2000, 2000), # Only 2000 for our range
                        'trim_engine_mapping': {
                            '840Ci': ['4.4L V8 N62'],
                            '850Ci': ['5.4L V12 M73'], # Placeholder for M73
                        }
                    },
                    'G14': {
                        'years': (2019, 2025),
                        'trim_engine_mapping': {
                            '840i': ['3.0L I6 B58 High Output'],
                            'M850i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'M8': {
                'generations': {
                    'F91 M8': {
                        'years': (2020, 2025),
                        'trim_engine_mapping': {
                            'M8': ['4.4L V8 S63TU Twin-Turbo'],
                            'M8 Competition': ['4.4L V8 S63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'X1': {
                'generations': {
                    'E84': {
                        'years': (2009, 2012),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'E84 LCI': {
                        'years': (2013, 2015),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'F48': {
                        'years': (2016, 2019),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 B46 Turbo'],
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                        }
                    },
                    'F48 LCI': {
                        'years': (2020, 2022),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 B46 Turbo'],
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                        }
                    },
                    'U11': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 B46 Turbo'],
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                            'iX1 xDrive30': ['eDrive40 Single Motor Electric'],
                        }
                    }
                }
            },
            'X2': {
                'generations': {
                    'F39': {
                        'years': (2018, 2020),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 B46 Turbo'],
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                            'M35i': ['2.0L I4 B48 Turbo'],
                        }
                    },
                    'F39 LCI': {
                        'years': (2021, 2023),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 B46 Turbo'],
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                            'M35i': ['2.0L I4 B48 Turbo'],
                        }
                    },
                    'U10': {
                        'years': (2024, 2025),
                        'trim_engine_mapping': {
                            'xDrive28i': ['2.0L I4 B46 Turbo'],
                            'M35i': ['2.0L I4 B48 Turbo'],
                            'iX2 xDrive30': ['eDrive40 Single Motor Electric'],
                        }
                    }
                }
            },
            'X3': {
                'generations': {
                    'E83': {
                        'years': (2004, 2006),
                        'trim_engine_mapping': {
                            '2.5i': ['2.5L I6 N52'],
                            '3.0i': ['3.0L I6 N52'],
                        }
                    },
                    'E83 LCI': {
                        'years': (2007, 2010),
                        'trim_engine_mapping': {
                            'xDrive30i': ['3.0L I6 N52'],
                        }
                    },
                    'F25': {
                        'years': (2011, 2014),
                        'trim_engine_mapping': {
                            'xDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'F25 LCI': {
                        'years': (2015, 2017),
                        'trim_engine_mapping': {
                            'xDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'G01': {
                        'years': (2018, 2021),
                        'trim_engine_mapping': {
                            'xDrive30i': ['2.0L I4 B46 Turbo'],
                            'M40i': ['3.0L I6 B58 High Output'],
                            'X3 M': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    },
                    'G01 LCI': {
                        'years': (2022, 2025),
                        'trim_engine_mapping': {
                            'xDrive30i': ['2.0L I4 B46 Turbo'],
                            'M40i': ['3.0L I6 B58 High Output'],
                            'X3 M': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    }
                }
            },
            'X4': {
                'generations': {
                    'F26': {
                        'years': (2014, 2018),
                        'trim_engine_mapping': {
                            'xDrive28i': ['2.0L I4 N20 Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'M40i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'G02': {
                        'years': (2019, 2021),
                        'trim_engine_mapping': {
                            'xDrive30i': ['2.0L I4 B46 Turbo'],
                            'M40i': ['3.0L I6 B58 High Output'],
                            'X4 M': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    },
                    'G02 LCI': {
                        'years': (2022, 2025),
                        'trim_engine_mapping': {
                            'xDrive30i': ['2.0L I4 B46 Turbo'],
                            'M40i': ['3.0L I6 B58 High Output'],
                            'X4 M': ['3.0L I6 S58 Twin-Turbo'],
                        }
                    }
                }
            },
            'X5': {
                'generations': {
                    'E53': {
                        'years': (2000, 2003),
                        'trim_engine_mapping': {
                            '3.0i': ['3.0L I6 N52'],
                            '4.4i': ['4.4L V8 N62'],
                        }
                    },
                    'E70': {
                        'years': (2007, 2010),
                        'trim_engine_mapping': {
                            'xDrive30i': ['3.0L I6 N52'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive48i': ['4.8L V8 N62'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'E70 LCI': {
                        'years': (2011, 2013),
                        'trim_engine_mapping': {
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F15': {
                        'years': (2014, 2017),
                        'trim_engine_mapping': {
                            'sDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F15 LCI': {
                        'years': (2018, 2018),
                        'trim_engine_mapping': {
                            'sDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'G05': {
                        'years': (2019, 2022),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 Single-Turbo'],
                            'xDrive45e': ['3.0L I6 B58 Hybrid'],
                            'M50i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    },
                    'G05 LCI': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 High Output'],
                            'xDrive50e': ['3.0L I6 B58 Hybrid'],
                            'M60i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'X6': {
                'generations': {
                    'E71': {
                        'years': (2008, 2011),
                        'trim_engine_mapping': {
                            'xDrive35i': ['3.0L I6 N54 Twin-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'E71 LCI': {
                        'years': (2012, 2014),
                        'trim_engine_mapping': {
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F16': {
                        'years': (2015, 2017),
                        'trim_engine_mapping': {
                            'sDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'F16 LCI': {
                        'years': (2018, 2019),
                        'trim_engine_mapping': {
                            'sDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive35i': ['3.0L I6 N55 Single-Turbo'],
                            'xDrive50i': ['4.4L V8 N63 Twin-Turbo'],
                        }
                    },
                    'G06': {
                        'years': (2020, 2022),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 Single-Turbo'],
                            'M50i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    },
                    'G06 LCI': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 High Output'],
                            'M60i': ['4.4L V8 N63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'X7': {
                'generations': {
                    'G07': {
                        'years': (2019, 2022),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 Single-Turbo'],
                            'M50i': ['4.4L V8 N63TU Twin-Turbo'],
                            'Alpina XB7': ['4.4L V8 S63TU Twin-Turbo'],
                        }
                    },
                    'G07 LCI': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'xDrive40i': ['3.0L I6 B58 High Output'],
                            'M60i': ['4.4L V8 N63TU Twin-Turbo'],
                            'Alpina XB7': ['4.4L V8 S63TU Twin-Turbo'],
                        }
                    }
                }
            },
            'Z4': {
                'generations': {
                    'E85/E86': {
                        'years': (2002, 2005),
                        'trim_engine_mapping': {
                            '2.5i': ['2.5L I6 N52'],
                            '3.0i': ['3.0L I6 N52'],
                        }
                    },
                    'E85/E86 LCI': {
                        'years': (2006, 2008),
                        'trim_engine_mapping': {
                            '3.0si': ['3.0L I6 N52'],
                            'M Roadster/Coupe': ['3.2L I6 S54'],
                        }
                    },
                    'E89': {
                        'years': (2009, 2012),
                        'trim_engine_mapping': {
                            'sDrive30i': ['3.0L I6 N52'],
                            'sDrive35i': ['3.0L I6 N54 Twin-Turbo'],
                            'sDrive35is': ['3.0L I6 N54 Twin-Turbo'],
                        }
                    },
                    'E89 LCI': {
                        'years': (2013, 2016),
                        'trim_engine_mapping': {
                            'sDrive28i': ['2.0L I4 N20 Turbo'],
                            'sDrive35i': ['3.0L I6 N55 Single-Turbo'],
                        }
                    },
                    'G29': {
                        'years': (2019, 2025),
                        'trim_engine_mapping': {
                            'sDrive30i': ['2.0L I4 B46 Turbo'],
                            'M40i': ['3.0L I6 B58 High Output'],
                        }
                    }
                }
            },
            'i3': {
                'generations': {
                    'I01': {
                        'years': (2014, 2017),
                        'trim_engine_mapping': {
                            'i3': ['eDrive40 Single Motor Electric'],
                            'i3 REx': ['eDrive40 Single Motor Electric', '1.5L I3 B38 Turbo'],
                        }
                    },
                    'I01 LCI': {
                        'years': (2018, 2022),
                        'trim_engine_mapping': {
                            'i3': ['eDrive40 Single Motor Electric'],
                            'i3 REx': ['eDrive40 Single Motor Electric', '1.5L I3 B38 Turbo'],
                        }
                    }
                }
            },
            'i8': {
                'generations': {
                    'I12/I15': {
                        'years': (2014, 2020),
                        'trim_engine_mapping': {
                            'i8': ['1.5L I3 B38 Hybrid'],
                        }
                    }
                }
            },
            'iX1': {
                'generations': {
                    'U11': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'iX1 xDrive30': ['eDrive40 Single Motor Electric'],
                        }
                    }
                }
            },
            'iX2': {
                'generations': {
                    'U10': {
                        'years': (2024, 2025),
                        'trim_engine_mapping': {
                            'iX2 xDrive30': ['eDrive40 Single Motor Electric'],
                        }
                    }
                }
            },
            'i4': {
                'generations': {
                    'G26': {
                        'years': (2022, 2025),
                        'trim_engine_mapping': {
                            'i4 eDrive35': ['eDrive40 Single Motor Electric'],
                            'i4 eDrive40': ['eDrive40 Single Motor Electric'],
                            'i4 M50': ['eDrive M60 Dual Motor Electric'],
                        }
                    }
                }
            },
            'i5': {
                'generations': {
                    'G60': {
                        'years': (2024, 2025),
                        'trim_engine_mapping': {
                            'i5 eDrive40': ['eDrive40 Single Motor Electric'],
                            'i5 M60': ['eDrive M60 Dual Motor Electric'],
                        }
                    }
                }
            },
            'i7': {
                'generations': {
                    'G70': {
                        'years': (2023, 2025),
                        'trim_engine_mapping': {
                            'i7 eDrive50': ['eDrive50 Dual Motor Electric'],
                            'i7 xDrive60': ['eDrive60 Dual Motor Electric'],
                            'i7 M70': ['eDrive M70 Dual Motor Electric'],
                        }
                    }
                }
            },
            'iX': {
                'generations': {
                    'I20': {
                        'years': (2022, 2025),
                        'trim_engine_mapping': {
                            'iX xDrive50': ['eDrive50 Dual Motor Electric'],
                            'iX M60': ['eDrive M60 Dual Motor Electric'],
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
                if model in bmw_vehicle_combinations:
                    filtered_combinations[model] = bmw_vehicle_combinations[model]
            bmw_vehicle_combinations = filtered_combinations
        
        self.stdout.write(f'Creating vehicles for years: {min(years_range)}-{max(years_range)}')
        self.stdout.write(f'Processing {len(bmw_vehicle_combinations)} models...')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process each model
        for model_name, model_data in bmw_vehicle_combinations.items():
            self.stdout.write(f'\n📋 Processing {model_name}:')
            
            if not dry_run:
                try:
                    model_obj = Model.objects.get(make__name='BMW', name=model_name)
                except Model.DoesNotExist:
                    self.stdout.write(f'  ❌ Model {model_name} not found - run add_bmw_models first')
                    error_count += 1
                    continue
            
            # Process each generation
            for generation, gen_data in model_data['generations'].items():
                gen_display = f" {generation}" if generation else ""
                if 'LCI' in generation:
                    gen_display += " 🔄"  # Highlight LCI refreshes
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
                                        make=bmw_make,
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
                                            make=bmw_make,
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
        self.stdout.write('BMW VEHICLES SUMMARY (LCI REFRESH SUPPORT)')
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
                for model_data in bmw_vehicle_combinations.values()
                for gen_data in model_data['generations'].values()
            )
            self.stdout.write(f'📊 Would create approximately: {total_combinations} vehicle records')
        
        # Model insights
        self.stdout.write('\n🔍 BMW VEHICLE INSIGHTS (LCI GENERATION SUPPORT):')
        self.stdout.write('BMW Platform Evolution with LCI Refreshes:')
        self.stdout.write('• 3 Series: E90/E90 LCI→F30/F30 LCI→G20/G20 LCI')
        self.stdout.write('• X3: E83/E83 LCI→F25/F25 LCI→G01/G01 LCI')
        self.stdout.write('• M3: E46→E90/E92→F80→G80 (separate M model line)')
        
        self.stdout.write('\nLCI Refresh Significance:')
        self.stdout.write('• Parts Compatibility: LCI generations often require different:')
        self.stdout.write('  - Headlights (halogen→xenon→LED→laser)')
        self.stdout.write('  - Body panels (updated styling, aerodynamics)')
        self.stdout.write('  - Interior components (iDrive system updates)')
        self.stdout.write('  - Electronic modules (updated software/hardware)')
        
        # Next steps
        self.stdout.write('\n📋 NEXT STEPS:')
        self.stdout.write('1. Verify vehicle records: Check admin panel for LCI generation accuracy')
        self.stdout.write('2. Parts compatibility: LCI refreshes will need separate fitment records')
        self.stdout.write('3. Add more models: Expand to 5 Series, 7 Series, X5, etc.')
        self.stdout.write('4. Create fitments: Map parts to specific generations (E90 vs E90 LCI)')
        
        if not dry_run and created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully created {created_count} BMW vehicle records with LCI generation support!')
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
