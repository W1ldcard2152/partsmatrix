#!/usr/bin/env python
"""Test just the parsing logic without Django"""

import re

def test_parsing():
    # Read the sample data
    with open('acura_parts_data.txt', 'r', encoding='utf-8') as f:
        raw_data = f.read()
    
    print("🧪 Testing Parsing Logic")
    print("=" * 40)
    
    # Test part name and number parsing
    def parse_part_name_and_number(raw_data):
        patterns = [
            r'^(.*?)\s*-\s*Acura\s*\((.*?)\)',
            r'(.*?)\s*-\s*Acura.*?(\d{5}-[A-Z0-9]+-\d{3})',
            r'(.*?)\s*.*?Part Number:\s*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_data, re.MULTILINE)
            if match:
                part_name = match.group(1).strip()
                part_number = match.group(2).strip()
                return part_name, part_number
        
        raise ValueError("Could not parse Part Name and Part Number from raw data.")
    
    # Test fitment data parsing
    def parse_fitment_data(raw_data):
        fitment_data = []
        
        # More flexible table finding
        patterns = [
            r'Vehicle Fitment\s*.*?Year\s*Make\s*Model\s*Body & Trim\s*Engine & Transmission\s*(.*?)(?=\n\n|\Z)',
            r'Year\s*Make\s*Model\s*Body & Trim\s*Engine & Transmission\s*(.*?)(?=\n\n|\Z)',
        ]
        
        table_content = None
        for pattern in patterns:
            fitment_match = re.search(pattern, raw_data, re.DOTALL | re.IGNORECASE)
            if fitment_match:
                table_content = fitment_match.group(1).strip()
                break
        
        if not table_content:
            return fitment_data
        
        print(f"Found table content:\n{table_content}\n")
        
        lines = table_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            print(f"Processing line: '{line}'")
            
            # More robust parsing patterns
            patterns = [
                r'^(\d{4})\s+(Acura)\s+([A-Z]+)\s+(.*?)\s+(.*?)$',
                r'^(\d{4})\t+(Acura)\t+([A-Z]+)\t+(.*?)\t+(.*?)$',
                r'^(\d{4})\s+(\w+)\s+(\w+)\s+(.*?)\s+(.*?)$',
            ]
            
            for i, pattern in enumerate(patterns):
                row_match = re.match(pattern, line)
                if row_match:
                    year = int(row_match.group(1))
                    make = row_match.group(2).strip()
                    model = row_match.group(3).strip()
                    body_trim = row_match.group(4).strip()
                    engine_trans = row_match.group(5).strip()
                    
                    print(f"  ✓ Matched with pattern {i+1}")
                    print(f"    Year: {year}")
                    print(f"    Make: {make}")
                    print(f"    Model: {model}")
                    print(f"    Body & Trim: {body_trim}")
                    print(f"    Engine & Trans: {engine_trans}")
                    
                    fitment_data.append({
                        'Year': year,
                        'Make': make,
                        'Model': model,
                        'Body & Trim': body_trim,
                        'Engine & Transmission': engine_trans,
                    })
                    break
            else:
                print(f"  ✗ No pattern matched")
        
        return fitment_data
    
    # Run tests
    try:
        part_name, part_number = parse_part_name_and_number(raw_data)
        print(f"✅ Part Name: {part_name}")
        print(f"✅ Part Number: {part_number}")
        
        fitment_data = parse_fitment_data(raw_data)
        print(f"\n✅ Found {len(fitment_data)} fitment entries:")
        
        for entry in fitment_data:
            print(f"  {entry['Year']} {entry['Make']} {entry['Model']} | {entry['Body & Trim']} | {entry['Engine & Transmission']}")
        
        print(f"\n🎉 Parsing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_parsing()
