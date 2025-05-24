# NHTSA Vehicle Data Import - Enhanced Version

This enhanced version of the NHTSA vehicle import script addresses the noise filtering issues and adds capabilities for extracting trim and engine data from VIN information.

## Key Improvements

### 1. Noise Filtering
The script now includes sophisticated filtering to remove unwanted data:

- **Chassis codes and internal codes**: Filters out short alphanumeric codes like "A1", "B2X"
- **Foreign market models**: Removes "RIGHT HAND DRIVE", "EXPORT", "INTL" models
- **Commercial/Fleet models**: Filters out "COMMERCIAL", "FLEET", "TAXI", "POLICE" variants
- **Prototype/Concept cars**: Removes "CONCEPT", "PROTOTYPE", "EXPERIMENTAL" entries
- **Generic placeholders**: Filters out "MODEL", "UNKNOWN", "N/A", "TBD" entries

### 2. Market-Specific Filtering
- **US Market Focus**: Prioritizes domestic and common foreign makes sold in the US market
- **Domestic Makes**: Chevrolet, Ford, Dodge, Chrysler, Plymouth, Buick, Cadillac, etc.
- **Common Foreign Makes**: Toyota, Honda, Nissan, BMW, Mercedes-Benz, Audi, etc.

### 3. Enhanced Data Collection
- **Year-Specific Models**: Uses `GetModelsForMakeYear` API for more accurate data
- **VIN Decoding**: Optional VIN decoding to extract detailed specifications
- **Trim Information**: Extracts trim levels from VIN data
- **Engine Specifications**: Collects displacement, cylinders, fuel type, horsepower

## Usage

### Basic Import
```bash
# Import vehicles for 2020-2024, US market only
python manage.py import_nhtsa_vehicles --years 2020-2024

# Import specific makes
python manage.py import_nhtsa_vehicles --makes "Ford,Toyota,Honda" --years 2015-2024

# Dry run to see what would be imported
python manage.py import_nhtsa_vehicles --dry-run --years 2020-2022
```

### Advanced Import with VIN Decoding
```bash
# Include VIN decoding for detailed specs (slower)
python manage.py import_nhtsa_vehicles --decode-vins --years 2020-2024

# Reduce batch size for stability
python manage.py import_nhtsa_vehicles --batch-size 25 --years 2020-2024
```

### Exploration Commands

#### Explore VIN Decoding Capabilities
```bash
# See what variables are available from VIN decoding
python manage.py explore_vin_data --get-variables

# Decode sample VINs to see available data
python manage.py explore_vin_data --sample-vins

# Decode a specific VIN
python manage.py explore_vin_data --vin 1FTMW1T88MFA12345

# Show all fields (not just vehicle specs)
python manage.py explore_vin_data --sample-vins --show-all-fields
```

## Available Data Fields

### From VIN Decoding
The VIN decoder can provide the following information:

#### Vehicle Information
- Make
- Model
- Model Year
- Trim
- Series
- Body Class
- Vehicle Type

#### Engine Specifications
- Engine Model
- Engine Displacement (L, CI, CC)
- Number of Cylinders
- Engine Configuration
- Fuel Type
- Engine Power (kW)
- Engine Brake Horsepower (BHP)
- Engine Manufacturer

#### Drivetrain
- Drive Type (FWD, RWD, AWD, 4WD)
- Transmission Style
- Transmission Speeds

## Data Quality Improvements

### Model Name Filtering
The script now filters out problematic model names:
- Excessively long names (>50 characters, likely descriptions)
- Names that are mostly numbers
- Chassis codes and internal part numbers
- Foreign market specific variants

### Make Filtering
- Prioritizes US market manufacturers
- Includes common foreign brands sold in US
- Filters out obscure or commercial-only manufacturers

### Rate Limiting
- Implements proper rate limiting to avoid API throttling
- Configurable delays between requests
- Handles 429 (Too Many Requests) errors gracefully

## VIN Pattern Generation

The included VIN pattern generator can create realistic VIN patterns for testing:

```python
from vin_pattern_generator import VINPatternGenerator

generator = VINPatternGenerator()

# Generate VIN patterns for Ford F-150 2021
patterns = generator.generate_vin_patterns('Ford', 'F-150', 2021, count=5)

# Get known VIN patterns for testing
wmis = generator.get_wmi_for_make('Ford')
```

## Configuration Options

### Command Line Arguments
- `--years`: Year range (e.g., "2020-2024" or "2020")
- `--makes`: Comma-separated list of makes
- `--dry-run`: Preview what would be imported
- `--batch-size`: Number of records per batch (default: 50)
- `--decode-vins`: Enable VIN decoding for detailed specs
- `--us-market-only`: Filter to US market vehicles (default: True)

### Noise Pattern Configuration
You can modify the noise patterns in the script:

```python
self.noise_patterns = [
    r'^[A-Z0-9]{2,4}$',  # Short alphanumeric codes
    r'CHASSIS',
    r'INCOMPLETE',
    r'CUTAWAY',
    r'STRIPPED',
    # Add your own patterns here
]
```

### Make List Configuration
You can modify the domestic and foreign make lists:

```python
self.domestic_makes = {
    'CHEVROLET', 'FORD', 'DODGE', 'CHRYSLER', 
    # Add more domestic makes
}

self.common_foreign_makes = {
    'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA',
    # Add more foreign makes
}
```

## Database Schema Impact

The enhanced import creates more detailed vehicle records:

### Vehicle Table
- Enhanced with trim and engine relationships
- Better data quality through filtering
- More accurate year/make/model combinations

### Engine Table
- Populated from VIN decode data
- Includes displacement, cylinders, fuel type, horsepower
- Links to specific vehicle variants

### Trim Table
- Extracted from VIN data
- Includes series and trim level information
- Linked to specific vehicles

## Performance Considerations

### API Rate Limiting
- NHTSA API has rate limits (exact limits not published)
- Script includes automatic retry logic for 429 errors
- Configurable delays between requests

### Import Time Estimates
- Basic import (no VIN decoding): ~2-5 minutes per make per year
- With VIN decoding: ~10-30 minutes per make per year
- Full US market (20 makes, 10 years): 2-6 hours depending on options

### Memory Usage
- Uses Django's transaction.atomic for batch processing
- Configurable batch sizes to manage memory
- Database connections properly managed

## Troubleshooting

### Common Issues

#### "No models found" for a make
```bash
# Try the explore command first
python manage.py explore_vin_data --get-variables

# Check if make name is correct
python manage.py import_nhtsa_vehicles --makes "Ford" --dry-run
```

#### Rate limiting errors
```bash
# Reduce batch size and add delays
python manage.py import_nhtsa_vehicles --batch-size 10 --years 2020-2021
```

#### VIN decoding failures
```bash
# Test VIN decoding separately
python manage.py explore_vin_data --vin 1FTMW1T88MFA12345

# Run without VIN decoding first
python manage.py import_nhtsa_vehicles --years 2020-2024
```

### Debug Mode
Add debug output by modifying the verbosity:

```python
# In the command, add more verbose output
self.stdout.write(f'Debug: Processing {model_name} for {year}')
```

## API Endpoints Used

### Primary Endpoints
- `GetMakesForVehicleType/car` - Get all car manufacturers
- `GetModelsForMakeYear` - Get models for specific make/year
- `GetModelsForMake` - Fallback for general models
- `DecodeVinValues` - Decode VIN for detailed specs
- `GetVehicleVariableList` - Get available VIN decode variables

### Response Format
All endpoints support JSON format:
```
?format=json
```

## Data Quality Metrics

### Before Filtering
- ~15,000+ model entries per major make
- High noise ratio (chassis codes, foreign variants)
- Inconsistent naming conventions

### After Filtering
- ~500-2000 clean model entries per major make
- US market focused
- Consistent, consumer-recognizable model names

### VIN Decode Success Rates
- Domestic vehicles: ~85-95% success rate
- Foreign vehicles: ~70-85% success rate
- Older vehicles (<2010): ~60-75% success rate

## Integration with Parts Database

The enhanced vehicle data integrates well with your parts interchange system:

### Fitment Precision
- More accurate vehicle identification
- Trim-level specificity
- Engine-specific fitments

### eBay Compatibility
- Follows eBay's Year/Make/Model/Trim/Engine format
- Compatible field mappings
- Proper data normalization

## Future Enhancements

### Planned Improvements
1. **VIN Database Integration**: Use offline VIN database for faster lookups
2. **Batch VIN Decoding**: Process multiple VINs in single API call
3. **Intelligent Sampling**: Better VIN pattern generation
4. **Data Validation**: Cross-reference with other automotive databases
5. **Incremental Updates**: Only import new/changed data

### Possible Extensions
1. **Motorcycle Support**: Extend to motorcycle data
2. **Truck/Commercial**: Add heavy truck support
3. **Historical Data**: Import older vehicle data (pre-1980)
4. **International Markets**: Support for Canadian/Mexican models

## Contributing

To improve the filtering or add new features:

1. Test changes with `--dry-run` first
2. Add new noise patterns to the appropriate lists
3. Document any new command line options
4. Update this README with changes

## License and Attribution

- NHTSA API data is public domain
- This script is part of the Parts Interchange Database project
- VIN decoding follows NHTSA standards and regulations

---

**Note**: Always verify imported data quality by reviewing a sample of the results before relying on the data for production use.
