"""
eBay Parts Data Viewer
Analyzes and displays extracted eBay parts data
"""

import os
import json
import csv
import pandas as pd
from typing import List, Dict
from collections import Counter

def find_data_files():
    """Find all eBay data files in the current directory"""
    json_files = [f for f in os.listdir('.') if f.startswith('ebay_acura_ac_parts_') and f.endswith('.json')]
    csv_files = [f for f in os.listdir('.') if f.startswith('ebay_acura_ac_parts_') and f.endswith('.csv')]
    
    return sorted(json_files), sorted(csv_files)

def load_json_data(filename: str) -> List[Dict]:
    """Load parts data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def analyze_data(parts_data: List[Dict]):
    """Analyze the extracted parts data"""
    if not parts_data:
        print("No data to analyze")
        return
    
    print(f"Data Analysis for {len(parts_data)} parts:")
    print("=" * 50)
    
    # Basic statistics
    prices = [part['price'] for part in parts_data if part.get('price', 0) > 0]
    if prices:
        print(f"Price Range: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"Average Price: ${sum(prices)/len(prices):.2f}")
    
    # Conditions
    conditions = [part.get('condition', 'Unknown') for part in parts_data]
    condition_counts = Counter(conditions)
    print(f"\nConditions:")
    for condition, count in condition_counts.most_common():
        print(f"  {condition}: {count}")
    
    # Manufacturers
    manufacturers = [part.get('manufacturer') for part in parts_data if part.get('manufacturer')]
    if manufacturers:
        mfg_counts = Counter(manufacturers)
        print(f"\nManufacturers:")
        for mfg, count in mfg_counts.most_common():
            print(f"  {mfg}: {count}")
    else:
        print(f"\nManufacturers: None extracted")
    
    # Part numbers found
    part_numbers = [part.get('part_number') for part in parts_data if part.get('part_number')]
    print(f"\nPart Numbers: {len(part_numbers)} found out of {len(parts_data)} listings")
    
    # Part names
    part_names = [part.get('part_name') for part in parts_data if part.get('part_name')]
    if part_names:
        name_counts = Counter(part_names)
        print(f"\nPart Names:")
        for name, count in name_counts.most_common():
            print(f"  {name}: {count}")
    
    # Fitments
    total_fitments = sum(len(part.get('fitments', [])) for part in parts_data)
    parts_with_fitments = sum(1 for part in parts_data if part.get('fitments'))
    print(f"\nFitments: {total_fitments} total, {parts_with_fitments} listings have fitment data")
    
    # Data completeness
    print(f"\nData Completeness:")
    fields_to_check = ['part_name', 'part_number', 'manufacturer', 'fitments']
    for field in fields_to_check:
        if field == 'fitments':
            count = sum(1 for part in parts_data if part.get(field))
        else:
            count = sum(1 for part in parts_data if part.get(field))
        percentage = (count / len(parts_data)) * 100
        print(f"  {field}: {count}/{len(parts_data)} ({percentage:.1f}%)")

def show_sample_parts(parts_data: List[Dict], count: int = 5):
    """Show sample parts with extracted data"""
    print(f"\nSample Parts (showing {min(count, len(parts_data))}):")
    print("=" * 80)
    
    for i, part in enumerate(parts_data[:count], 1):
        print(f"\n{i}. {part.get('title', 'No title')[:70]}...")
        print(f"   Price: ${part.get('price', 0):.2f}")
        if part.get('shipping_cost'):
            print(f"   Shipping: ${part.get('shipping_cost', 0):.2f}")
        print(f"   Condition: {part.get('condition', 'Unknown')}")
        print(f"   Seller: {part.get('seller_username', 'Unknown')} ({part.get('seller_feedback_score', 0)} feedback)")
        print(f"   ")
        print(f"   Extracted Data:")
        print(f"     Part Name: {part.get('part_name', 'Not extracted')}")
        print(f"     Part Number: {part.get('part_number', 'Not extracted')}")
        print(f"     Manufacturer: {part.get('manufacturer', 'Not extracted')}")
        print(f"     Fitments: {len(part.get('fitments', []))} found")
        
        # Show first fitment as example
        fitments = part.get('fitments', [])
        if fitments:
            f = fitments[0]
            print(f"     Example Fitment: {f.get('year')} {f.get('make')} {f.get('model')} {f.get('trim')}")
        
        print(f"   URL: {part.get('item_url', '')}")

def show_fitments_analysis(parts_data: List[Dict]):
    """Analyze vehicle fitments found in the data"""
    print(f"\nFitments Analysis:")
    print("=" * 50)
    
    all_fitments = []
    for part in parts_data:
        all_fitments.extend(part.get('fitments', []))
    
    if not all_fitments:
        print("No fitments found in the data")
        return
    
    # Years covered
    years = [f.get('year') for f in all_fitments if f.get('year')]
    if years:
        print(f"Year Range: {min(years)} - {max(years)}")
    
    # Makes
    makes = [f.get('make') for f in all_fitments if f.get('make')]
    make_counts = Counter(makes)
    print(f"\nMakes:")
    for make, count in make_counts.most_common():
        print(f"  {make}: {count} fitments")
    
    # Models
    models = [f.get('model') for f in all_fitments if f.get('model')]
    model_counts = Counter(models)
    print(f"\nTop Models:")
    for model, count in model_counts.most_common(10):
        print(f"  {model}: {count} fitments")
    
    # Year-Make-Model combinations
    ymm_combinations = []
    for f in all_fitments:
        if f.get('year') and f.get('make') and f.get('model'):
            ymm_combinations.append(f"{f['year']} {f['make']} {f['model']}")
    
    ymm_counts = Counter(ymm_combinations)
    print(f"\nTop Year-Make-Model Combinations:")
    for ymm, count in ymm_counts.most_common(10):
        print(f"  {ymm}: {count} listings")

def export_summary_csv(parts_data: List[Dict], filename: str = None):
    """Export a summary CSV with key information"""
    if filename is None:
        filename = "ebay_parts_summary.csv"
    
    summary_data = []
    for part in parts_data:
        summary_data.append({
            'ebay_id': part.get('ebay_item_id', ''),
            'title': part.get('title', '')[:100],  # Truncate long titles
            'price': part.get('price', 0),
            'condition': part.get('condition', ''),
            'part_name': part.get('part_name', ''),
            'part_number': part.get('part_number', ''),
            'manufacturer': part.get('manufacturer', ''),
            'fitments_count': len(part.get('fitments', [])),
            'seller': part.get('seller_username', ''),
            'feedback': part.get('seller_feedback_score', 0),
            'url': part.get('item_url', '')
        })
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if summary_data:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
    
    print(f"\nSummary exported to: {filename}")

def main():
    """Main function to run the data viewer"""
    print("eBay Parts Data Viewer")
    print("=====================")
    
    # Find data files
    json_files, csv_files = find_data_files()
    
    if not json_files:
        print("No eBay data files found in current directory.")
        print("Expected files starting with 'ebay_acura_ac_parts_' and ending with '.json'")
        return
    
    print(f"\nFound {len(json_files)} JSON data files:")
    for i, filename in enumerate(json_files, 1):
        file_size = os.path.getsize(filename) / 1024  # KB
        print(f"  {i}. {filename} ({file_size:.1f} KB)")
    
    # Let user choose file or use most recent
    if len(json_files) == 1:
        selected_file = json_files[0]
        print(f"\nUsing: {selected_file}")
    else:
        print(f"\nSelect file (1-{len(json_files)}) or press Enter for most recent:")
        choice = input("> ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(json_files):
            selected_file = json_files[int(choice) - 1]
        else:
            selected_file = json_files[-1]  # Most recent
        
        print(f"Using: {selected_file}")
    
    # Load and analyze data
    parts_data = load_json_data(selected_file)
    
    if not parts_data:
        print("No data found in file or error loading data.")
        return
    
    # Run analysis
    analyze_data(parts_data)
    show_sample_parts(parts_data)
    show_fitments_analysis(parts_data)
    
    # Ask about exporting summary
    print("\n" + "=" * 50)
    export_choice = input("Export summary CSV? (y/n): ").lower()
    if export_choice in ['y', 'yes']:
        export_summary_csv(parts_data)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
