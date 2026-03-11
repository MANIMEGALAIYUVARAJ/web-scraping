import os
import csv
import requests
from bs4 import BeautifulSoup
import re
import time
import random

class BaseScraper:
    def __init__(self, region, site_name, base_url):
        self.region = region
        self.site_name = site_name
        self.base_url = base_url
        self.output_dir = os.path.join(os.path.dirname(__file__), 'ScrapedData', region)
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = os.path.join(self.output_dir, f"{site_name.lower().replace(' ', '_')}_speakers.csv")

    def fetch(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def save_to_csv(self, data):
        if not data:
            print(f"No data found for {self.site_name}")
            return
        
        keys = data[0].keys()
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved {len(data)} results for {self.site_name} to {self.output_file}")
        return data

    def filter_results(self, results):
        # Basic unique by name
        seen = set()
        final = []
        for r in results:
            name = r.get('Name', '')
            if name and name not in seen:
                final.append(r)
                seen.add(name)
        return final

class EmailAwareScraper(BaseScraper):
    def extract_email_from_soup(self, soup):
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return emails[0] if emails else "Not Public"

class GenericListScraper(BaseScraper):
    def scrape(self):
        # Default placeholder
        pass

class GenericEmailListScraper(EmailAwareScraper):
    def scrape(self):
        print(f"Starting generic scrape for {self.site_name}...")
        html = self.fetch(self.base_url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        
        # Very generic search for names/roles
        results = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            name = h.get_text(strip=True)
            if 3 < len(name) < 50:
                results.append({
                    'Name': name,
                    'Email ID': 'Not Public',
                    'Role/Designation': 'N/A',
                    'Bio': 'N/A',
                    'Description': 'N/A',
                    'Speaking Sessions': 'N/A',
                    'LinkedIn': '',
                    'Source URL': self.base_url
                })
        
        final = self.filter_results(results)
        self.save_to_csv(final)
        return final
