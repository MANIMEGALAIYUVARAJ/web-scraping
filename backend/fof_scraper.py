import os
import csv
import re
import requests
from bs4 import BeautifulSoup
import argparse

class FOFScraper:
    def __init__(self, local_mode=False):
        self.site_name = "Future of Finance"
        self.base_url = "https://www.futureoffinance.in/"
        self.target_url = "https://www.futureoffinance.in/speakers.html?utm_source"
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ScrapedData', 'FutureOfFinance')
        self.output_file = os.path.join(self.output_dir, 'fof_speakers.csv')
        self.debug_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fof_discovery.html')
        self.local_mode = local_mode

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def extract_speaker_data(self, item_soup):
        """Extract data from a speaker card for Future of Finance"""
        try:
            # Name
            name_tag = item_soup.find('h5', class_='fw-bold')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # Role and Company
            smalls = item_soup.find_all('small')
            role = "N/A"
            company = "N/A"
            if len(smalls) > 0:
                role = smalls[0].get_text(strip=True)
            if len(smalls) > 1:
                company = smalls[1].get_text(strip=True)

            # Image
            img_src = ""
            img_div = item_soup.find('div', class_='speaker-img')
            if img_div and img_div.get('style'):
                style = img_div.get('style')
                match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                if match:
                    img_path = match.group(1)
                    if img_path.startswith('http'):
                        img_src = img_path
                    else:
                        # Handle paths like '../img/logo.png' or 'speaker/Srini.png'
                        img_src = os.path.join(self.base_url, img_path.replace('../', '')).replace('\\', '/')

            return {
                'Name': name,
                'Role/Designation': role,
                'Company': company,
                'Bio': "N/A",
                'Email ID': "Not Public",
                'LinkedIn': "",
                'Twitter': "",
                'Facebook': "",
                'Image URL': img_src,
                'Source URL': self.target_url
            }
        except Exception as e:
            print(f"Error extracting speaker: {e}")
            return None

    def scrape(self):
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Scraper")
        print(f"{'='*70}\n")
        
        try:
            if self.local_mode and os.path.exists(self.debug_file):
                print(f"Reading from local file: {self.debug_file}")
                with open(self.debug_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                print(f"Fetching {self.target_url}...")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = requests.get(self.target_url, headers=headers, timeout=90)
                response.raise_for_status()
                content = response.text
                
                # Save debug file if not in local mode
                with open(self.debug_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all speaker items
            # We need to exclude commented out ones. BeautifulSoup's find_all won't find items inside comments.
            speaker_items = soup.find_all('div', class_='speaker-card')
            
            print(f"Found {len(speaker_items)} speaker items")
            
            speakers = []
            for item in speaker_items:
                data = self.extract_speaker_data(item)
                if data and data['Name'] != "N/A":
                    print(f"[#] {len(speakers)+1}: {data['Name']} ({data['Role/Designation']} @ {data['Company']})")
                    speakers.append(data)
            
            # Save to CSV
            keys = ['Name', 'Role/Designation', 'Company', 'Bio', 'Email ID', 'LinkedIn', 'Twitter', 'Facebook', 'Image URL', 'Source URL']
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(speakers)
            
            print(f"\n✓ Successfully saved {len(speakers)} speakers to {self.output_file}")
            return speakers
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Future of Finance Speaker Scraper')
    parser.add_argument('--local', action='store_true', help='Use local fof_discovery.html instead of fetching')
    args = parser.parse_args()
    
    scraper = FOFScraper(local_mode=args.local)
    return scraper.scrape()

if __name__ == "__main__":
    main()
