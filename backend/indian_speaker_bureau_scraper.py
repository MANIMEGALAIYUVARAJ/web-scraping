import os
import csv
import re
import requests
from bs4 import BeautifulSoup
import time
import random

class IndianSpeakerBureauScraper:
    def __init__(self):
        self.site_name = "Indian Speaker Bureau"
        self.base_url = "https://www.indianspeakerbureau.com"
        self.category_url = "https://www.indianspeakerbureau.com/category/finance"
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ScrapedData', 'IndianSpeakerBureau')
        self.output_file = os.path.join(self.data_dir, 'indian_speaker_bureau_speakers.csv')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_soup(self, url):
        """Helper to get BeautifulSoup object from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_speaker_details(self, profile_url):
        """Extracts detailed information from a speaker's profile page"""
        print(f"  Scraping profile: {profile_url}")
        soup = self.get_soup(profile_url)
        if not soup:
            return None

        try:
            # Name
            name_tag = soup.find('h1', class_='heading-title')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"

            # Role
            role_tag = soup.select_one('.header-title-section h5')
            role = role_tag.get_text(strip=True) if role_tag else "N/A"

            # Biography
            bio_tag = soup.find(id='speaker-info')
            bio = bio_tag.get_text(strip=True) if bio_tag else "N/A"

            # Image
            img_tag = soup.select_one('#info img')
            img_url = img_tag['src'] if img_tag else ""
            if img_url and not img_url.startswith('http'):
                img_url = self.base_url + img_url

            # Topics/Positions
            topics_tag = soup.find('h3', class_='topic-subheading')
            topics = topics_tag.get_text(strip=True) if topics_tag else "N/A"

            return {
                'Name': name,
                'Role/Designation': role,
                'Biography': bio,
                'Topics': topics,
                'Image URL': img_url,
                'Email ID': "lets.speak@speakin.co",
                'Contact Number': "+91 96250 02763",
                'Source URL': profile_url
            }
        except Exception as e:
            print(f"Error extracting details from {profile_url}: {e}")
            return None

    def scrape(self):
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Scraper (Finance Category)")
        print(f"{'='*70}\n")
        
        soup = self.get_soup(self.category_url)
        if not soup:
            print("Failed to fetch category page.")
            return

        # Profile links are inside .carousel-item a[href*="speaker-profile"]
        profile_links = set()
        for a in soup.select('.carousel-item a[href*="speaker-profile"]'):
            url = a['href']
            if not url.startswith('http'):
                url = self.base_url + url
            profile_links.add(url)

        print(f"Found {len(profile_links)} speaker profile links.")
        
        speakers_data = []
        for i, link in enumerate(profile_links):
            print(f"[{i+1}/{len(profile_links)}] Processing...")
            data = self.extract_speaker_details(link)
            if data:
                speakers_data.append(data)
                print(f"    ✓ {data['Name']}")
            
            # Random delay to be polite
            time.sleep(random.uniform(1, 2))

        # Save to CSV
        if speakers_data:
            keys = ['Name', 'Role/Designation', 'Biography', 'Topics', 'Image URL', 'Email ID', 'Contact Number', 'Source URL']
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(speakers_data)
            print(f"\n✓ Successfully saved {len(speakers_data)} speakers to {self.output_file}")
            return speakers_data
        else:
            print("\nNo speaker data found.")

def main():
    scraper = IndianSpeakerBureauScraper()
    return scraper.scrape()

if __name__ == "__main__":
    main()
