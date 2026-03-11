import requests
from bs4 import BeautifulSoup
import csv
import time
import os

def get_speaker_links(base_url):
    print("Fetching speaker list...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # The speakers seem to be listed in a grid or alphabet list.
        # Based on the read_url_content, the links are in chunks 93-95.
        # Let's find all links and filter by the URL pattern.
        speaker_links = []
        # Try to find the container first if possible, otherwise look at all links
        container = soup.find('div', class_='region-content') or soup
        links = container.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # Pattern: /events/future-finance-2026/speakers/name
            if '/events/future-finance-2026/speakers/' in href:
                full_url = href if href.startswith('http') else 'https://milkeninstitute.org' + href
                # Exclude main page, glossary, and duplicates
                clean_url = full_url.split('#')[0].rstrip('/')
                if clean_url.count('/') >= 6 and clean_url not in speaker_links:
                    if not clean_url.endswith('/speakers'):
                        speaker_links.append(clean_url)
        
        print(f"Found {len(speaker_links)} potential speaker links.")
        return speaker_links
    except Exception as e:
        print(f"Error fetching speaker links: {e}")
        return []

def scrape_speaker_profile(url):
    print(f"Scraping {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Based on the browser screenshot in Step 1:
        # Name: h1
        name = soup.find('h1').get_text(strip=True) if soup.find('h1') else "N/A"
        
        # Role: .field--name-field-description
        role_div = soup.find('div', class_='field--name-field-description')
        role = role_div.get_text(strip=True) if role_div else "N/A"
        
        # Description: .bio-body
        bio_div = soup.find('div', class_='bio-body')
        description = bio_div.get_text(strip=True) if bio_div else "N/A"
        
        social_links = {
            'linkedin': '',
            'instagram': '',
            'twitter': ''
        }
        
        # Social links: .bio-social-links a
        # Also let's check for any link containing the social platform name
        social_container = soup.find('div', class_='bio-social-links') or soup
        links = social_container.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'linkedin.com' in href:
                social_links['linkedin'] = href
            elif 'instagram.com' in href:
                social_links['instagram'] = href
            elif 'twitter.com' in href or 'x.com' in href:
                social_links['twitter'] = href
        
        # Email: Sites often don't display it to avoid spam. Search for mailto:
        email = "N/A"
        email_tag = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        if email_tag:
            email = email_tag['href'].replace('mailto:', '').split('?')[0]
        
        return {
            'name': name,
            'email id': email,
            'description': description,
            'linkedin': social_links['linkedin'],
            'instagram': social_links['instagram'],
            'twitter': social_links['twitter'],
            'role': role
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    base_url = "https://milkeninstitute.org/events/future-finance-2026/speakers"
    speaker_urls = get_speaker_links(base_url)
    
    if not speaker_urls:
        print("No speaker links found. Check selectors.")
        return

    all_data = []
    # Scrape all found speakers
    for url in speaker_urls:
        data = scrape_speaker_profile(url)
        if data:
            all_data.append(data)
        time.sleep(1) # Be respectful
        
    output_file = os.path.join(os.path.dirname(__file__), 'speakers_data.csv')
    
    keys = ['name', 'email id', 'description', 'linkedin', 'instagram', 'twitter', 'role']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)
        
    print(f"Successfully scraped {len(all_data)} speakers.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()

