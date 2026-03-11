import os
import csv
import glob
import pandas as pd
from london_scraper import main as run_london
from india_scraper import main as run_india
from gartner_scraper import main as run_gartner
from bharat_2025_scraper import main as run_bharat_2025
from bharat_2023_scraper import main as run_bharat_2023
from fof_scraper import main as run_fof
from indian_speaker_bureau_scraper import main as run_isb
from london_speaker_bureau_scraper import main as run_lsb
# Import other scrapers as needed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data is kept in Backend/ScrapedData for consistent relative paths from here
DATA_DIR = os.path.join(BASE_DIR, 'ScrapedData')

def run_scrapers(selected_scrapers):
    """
    Runs the selected scrapers.
    """
    if 'london' in selected_scrapers:
        try:
            print("Running London Scraper...")
            run_london()
        except Exception as e:
            print(f"London scraper failed: {e}")

    if 'india' in selected_scrapers:
        try:
            print("Running India Scraper...")
            run_india()
        except Exception as e:
            print(f"India scraper failed: {e}")
    
    if 'gartner' in selected_scrapers:
        try:
            print("Running Gartner Scraper...")
            run_gartner()
        except Exception as e:
            print(f"Gartner scraper failed: {e}")
    
    if 'bharat_2023' in selected_scrapers:
        try:
            print("Running Bharat 2023 Scraper...")
            run_bharat_2023()
        except Exception as e:
            print(f"Bharat 2023 scraper failed: {e}")

    if 'future_of_finance' in selected_scrapers:
        try:
            print("Running Future of Finance Scraper...")
            run_fof()
        except Exception as e:
            print(f"Future of Finance scraper failed: {e}")
    
    if 'indian_speaker_bureau' in selected_scrapers:
        try:
            print("Running Indian Speaker Bureau Scraper...")
            run_isb()
        except Exception as e:
            print(f"Indian Speaker Bureau scraper failed: {e}")
    
    if 'london_speaker_bureau' in selected_scrapers:
        try:
            print("Running London Speaker Bureau Scraper...")
            run_lsb()
        except Exception as e:
            print(f"London Speaker Bureau scraper failed: {e}")
    
    # Add other scrapers here

def get_filtered_results(query, limit, scrapers):
    """
    Reads CSVs from the selected regions, filters by query, and returns results.
    """
    all_data = []

    # Map checkbox values to folder names in ScrapedData
    # Assuming 'london' -> 'London', 'india' -> 'India', 'gartner' -> 'UK'
    # Or we can just search all if strict mapping isn't crucial, but let's try to be specific
    
    regions = []
    if 'london' in scrapers: regions.append('London')
    if 'india' in scrapers: regions.append('India')
    if 'gartner' in scrapers: regions.append('UK')
    if 'bharat_2025' in scrapers: regions.append('BharatFintech2025')
    if 'bharat_2023' in scrapers: regions.append('BharatFintech2023')
    if 'future_of_finance' in scrapers: regions.append('FutureOfFinance')
    if 'indian_speaker_bureau' in scrapers: regions.append('IndianSpeakerBureau')
    if 'london_speaker_bureau' in scrapers: regions.append('London')
    
    for region in regions:
        region_path = os.path.join(DATA_DIR, region)
        if not os.path.exists(region_path):
            continue
            
        csv_files = glob.glob(os.path.join(region_path, '*.csv'))
        for file in csv_files:
            try:
                # Read CSV
                df = pd.read_csv(file)
                df['Source_Region'] = region # Add region info
                
                # Convert to dict
                data = df.to_dict(orient='records')
                all_data.extend(data)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    # Access fields safely
    # Standard keys from base_scraper: 'Name', 'Email ID', 'Role/Designation', 'Description', ...
    
    filtered_data = []
    query = query.lower().strip() if query else ""
    
    for row in all_data:
        # If query is empty, return all (up to limit)
        if not query:
            filtered_data.append(row)
            continue
            
        # Search in Name, Role, Description
        name = str(row.get('Name', '')).lower()
        role = str(row.get('Role/Designation', '')).lower()
        desc = str(row.get('Description', '')).lower()
        
        if query in name or query in role or query in desc:
            filtered_data.append(row)

    # Apply limit
    try:
        limit = int(limit)
    except:
        limit = 10
        
    return filtered_data[:limit]
