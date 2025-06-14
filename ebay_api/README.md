# eBay Parts Extractor

This script extracts automotive parts data from eBay Motors listings using the eBay Finding API. It's designed to extract the same data fields as the smart parser for seamless integration with the Parts Matrix database.

## Features

- Searches eBay Motors for Acura AC compressors and clutches over $50
- Extracts part names, numbers, manufacturers, and fitment information
- Uses the same data extraction patterns as the smart parser
- Outputs data in JSON and CSV formats
- Respects eBay API rate limits
- Comprehensive logging

## Setup

### 1. Get eBay API Credentials

1. Go to [eBay Developers Program](https://developer.ebay.com/)
2. Sign up for a developer account (free)
3. Create a new application
4. Get your App ID from the "Application Keys" section

### 2. Install Dependencies

```bash
# From the Parts Matrix root directory
pip install -r ebay_api/requirements.txt
```

### 3. Configure API Credentials

```bash
# Copy the example environment file
cp ebay_api/.env.example ebay_api/.env

# Edit the .env file and add your eBay App ID
EBAY_APP_ID=your-actual-app-id-here
```

### 4. Set Environment Variable (Alternative)

```bash
# Linux/Mac
export EBAY_APP_ID="your-app-id-here"

# Windows Command Prompt
set EBAY_APP_ID=your-app-id-here

# Windows PowerShell
$env:EBAY_APP_ID="your-app-id-here"
```

## Usage

### Basic Usage

```bash
# From the Parts Matrix root directory
cd ebay_api
python ebay_parts_extractor.py
```

### Output

The script will:
1. Search eBay for Acura AC compressors over $50
2. Extract part data using smart parser patterns
3. Display results in the console
4. Save data to timestamped JSON and CSV files

### Example Output Files

- `ebay_acura_ac_parts_20231210_143022.json` - Complete data in JSON format
- `ebay_acura_ac_parts_20231210_143022.csv` - Spreadsheet-friendly format

## Data Fields Extracted

The extractor attempts to extract the same data fields as the smart parser:

### Basic Information
- `ebay_item_id` - eBay listing ID
- `title` - Original eBay listing title
- `price` - Current price
- `shipping_cost` - Shipping cost (if available)
- `seller_username` - eBay seller username
- `seller_feedback_score` - Seller feedback rating
- `item_url` - Direct link to eBay listing
- `condition` - Item condition (New, Used, etc.)
- `location` - Seller location

### Extracted Part Data
- `part_name` - Cleaned part name (e.g., "AC Compressor")
- `part_number` - Extracted part number
- `manufacturer` - Detected manufacturer (Acura, Denso, Sanden, etc.)
- `description` - Part description
- `fitments` - Array of vehicle compatibility data
- `category` - Part category ("HVAC & Climate Control")

### eBay Specific Data
- `listing_type` - Auction or Fixed Price
- `time_left` - Time remaining for auction
- `watch_count` - Number of watchers

## Extraction Patterns

The script uses regex patterns similar to the smart parser to extract:

### Part Names
- Handles variations like "AC Compressor", "A/C Compressor", "Air Conditioning Compressor"
- Extracts clean part names from complex eBay titles

### Part Numbers
- Looks for patterns like `(12345-ABC-678)`, `Part #: 12345`, `SKU: 12345`
- Validates part numbers for reasonable length and alphanumeric content

### Manufacturers
- Maps common abbreviations to full manufacturer names
- Detects OEM manufacturers like Denso, Sanden, Valeo
- Recognizes vehicle manufacturers (Acura, Honda, etc.)

### Vehicle Fitments
- Extracts year ranges: "2005-2010 Acura TL"
- Handles single years: "2008 Acura MDX"
- Parses "Fits:" and "For:" declarations
- Generates individual fitment records for year ranges

## API Rate Limits

The script is configured to respect eBay's rate limits:
- 1-second delay between different search terms
- Uses eBay Finding API (5,000 calls/day for free accounts)
- Implements error handling for API failures

## Troubleshooting

### Common Issues

1. **"EBAY_APP_ID environment variable not set"**
   - Make sure you've set the environment variable or created a .env file
   - Verify your App ID is correct

2. **"No matching parts found"**
   - Check your internet connection
   - Verify the eBay App ID is valid
   - Try running again (listings change frequently)

3. **"Request error" or "JSON decode error"**
   - Network connectivity issues
   - eBay API temporarily unavailable
   - Rate limit exceeded (wait and retry)

### Debugging

Enable debug logging by modifying the script:

```python
logging.basicConfig(level=logging.DEBUG)
```

Check the log file `ebay_extractor.log` for detailed information.

## Integration with Parts Matrix

The extracted data is compatible with the Parts Matrix smart parser format:

```python
# Example: Load and process eBay data
import json
from ebay_parts_extractor import EbayPartsExtractor

# Load saved data
with open('ebay_acura_ac_parts_20231210_143022.json', 'r') as f:
    ebay_parts = json.load(f)

# Process each part
for part_data in ebay_parts:
    # Use same validation as smart parser
    if part_data['part_name'] and part_data['part_number']:
        # Ready for database import
        print(f"Valid part: {part_data['part_name']} - {part_data['part_number']}")
```

## Customization

### Search Different Categories

Change the category ID in the script:

```python
# AC Compressors & Clutches
category_id = "33654"

# All Car & Truck Parts
category_id = "6028" 

# Brake Parts
category_id = "179906"
```

### Search Different Brands

Modify the search terms:

```python
search_terms = [
    "Honda AC Compressor",
    "Toyota A/C Compressor", 
    "Ford Air Conditioning Compressor"
]
```

### Adjust Price Filters

```python
extractor.search_parts(
    keywords="AC Compressor",
    min_price=100.0,  # Minimum $100
    max_results=50
)
```

## eBay API Documentation

- [eBay Finding API Guide](https://developer.ebay.com/DevZone/finding/Concepts/MakingACall.html)
- [eBay Category IDs](https://pages.ebay.com/sellerinformation/news/categorychanges.html)
- [Rate Limits](https://developer.ebay.com/support/kb/article/5829)

## License

This tool is part of the Parts Matrix project and follows the same license terms.
