import os
import csv
import requests
from bs4 import BeautifulSoup
import time
import random
import re

class LondonSpeakerBureauScraper:
    def __init__(self):
        self.site_name = "London Speaker Bureau"
        self.base_url = "https://londonspeakerbureau.com"
        self.category_url = "https://londonspeakerbureau.com/speaker-categories/economics-finance/"
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ScrapedData', 'London')
        self.output_file = os.path.join(self.data_dir, 'london_speaker_bureau_speakers.csv')
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
            # Name - h1 contains a span with "Keynote Speaker"
            name_tag = soup.find('h1')
            if name_tag:
                # Remove span text
                span = name_tag.find('span')
                if span:
                    span.decompose()
                name = name_tag.get_text(strip=True)
            else:
                name = "N/A"

            # Role - Usually h2 after name
            role_tag = soup.find('h2', class_='mb-8') or soup.find('h2')
            role = role_tag.get_text(strip=True) if role_tag else "N/A"

            # Biography
            bio_section = soup.find(id='biography')
            if bio_section:
                bio_tag = bio_section.select_one('.custom-content div')
                bio = bio_tag.get_text('\n', strip=True) if bio_tag else "N/A"
            else:
                bio = "N/A"

            # Image
            img_tag = soup.select_one('#content-header img') or soup.select_one('section img')
            img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""

            # Topics
            topics = []
            topic_tags = soup.select('li.speaker-tag a')
            for tag in topic_tags:
                topics.append(tag.get_text(strip=True))
            topics_str = ", ".join(topics) if topics else "N/A"

            # Popular Talks
            talks = []
            talk_tags = soup.select('li.p-4.break-inside-avoid.bg-white span')
            for tag in talk_tags:
                talks.append(tag.get_text(strip=True))
            talks_str = " | ".join(talks) if talks else "N/A"

            return {
                'Name': name,
                'Role/Designation': role,
                'Biography': bio,
                'Topics': topics_str,
                'Popular Talks': talks_str,
                'Image URL': img_url,
                'Email ID': "enquiries@londonspeakerbureau.com", # Default contact
                'Contact Number': "+44 208 748 9595", # Default contact
                'Source URL': profile_url
            }
        except Exception as e:
            print(f"Error extracting details from {profile_url}: {e}")
            return None

    def get_profile_links_from_page(self, soup):
        """Extracts all profile links from a listing page soup"""
        links = []
        # Profiles are in .speaker-list.card-link a
        for a in soup.select('.speaker-list.card-link a[href]'):
            url = a['href']
            if not url.startswith('http'):
                url = self.base_url + url
            if '/speaker-profile/' in url:
                links.append(url)
        return list(set(links)) # Unique links

    def scrape(self):
        print(f"\n{'='*70}")
        print(f"  {self.site_name} Scraper (Economics & Finance)")
        print(f"{'='*70}\n")
        
        current_url = self.category_url
        all_profile_links = []
        page_num = 1

        while current_url:
            print(f"Scanning listing page {page_num}: {current_url}")
            soup = self.get_soup(current_url)
            if not soup:
                break
            
            links = self.get_profile_links_from_page(soup)
            all_profile_links.extend(links)
            print(f"  Found {len(links)} links (Total: {len(all_profile_links)})")
            
            # Find next page
            next_tag = soup.find('link', rel='next')
            if next_tag and 'href' in next_tag.attrs:
                current_url = next_tag['href']
                page_num += 1
                time.sleep(1) # Small delay between page scans
            else:
                current_url = None

        print(f"\nFound total {len(all_profile_links)} unique speaker profiles.")
        
        speakers_data = []
        for i, link in enumerate(all_profile_links):
            print(f"[{i+1}/{len(all_profile_links)}] Processing...")
            data = self.extract_speaker_details(link)
            if data:
                speakers_data.append(data)
                print(f"    ✓ {data['Name']}")
            
            # Periodic saving in case of failure
            if len(speakers_data) % 10 == 0:
                self.save_to_csv(speakers_data)
            
            # Random delay to be polite
            time.sleep(random.uniform(1, 2))

        # Final save
        self.save_to_csv(speakers_data)
        print(f"\n✓ Scraping complete. Total speakers: {len(speakers_data)}")
        return speakers_data

    def save_to_csv(self, data):
        if not data:
            return
        keys = ['Name', 'Role/Designation', 'Biography', 'Topics', 'Popular Talks', 'Image URL', 'Email ID', 'Contact Number', 'Source URL']
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)

def main():
    scraper = LondonSpeakerBureauScraper()
    return scraper.scrape()

if __name__ == "__main__":
    main()
