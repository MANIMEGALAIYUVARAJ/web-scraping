import time
import re
from bs4 import BeautifulSoup
from base_scraper import BaseScraper, GenericListScraper, EmailAwareScraper, GenericEmailListScraper

class MilkenScraper(EmailAwareScraper):
    def scrape(self):
        print(f"Starting {self.site_name} scraper...")
        html = self.fetch(self.base_url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/events/future-finance-2026/speakers/' in href:
                full_url = href if href.startswith('http') else 'https://milkeninstitute.org' + href
                clean_url = full_url.split('#')[0].rstrip('/')
                if clean_url.count('/') >= 6 and not clean_url.endswith('/speakers'):
                    if clean_url not in links: links.append(clean_url)

        results = []
        for url in links:
            profile_html = self.fetch(url)
            if not profile_html: continue
            psoup = BeautifulSoup(profile_html, 'html.parser')
            
            name = psoup.find('h1').get_text(strip=True) if psoup.find('h1') else "N/A"
            role = psoup.find('div', class_='field--name-field-description').get_text(strip=True) if psoup.find('div', class_='field--name-field-description') else "N/A"
            desc = psoup.find('div', class_='bio-body').get_text(strip=True) if psoup.find('div', class_='bio-body') else "N/A"
            
            social = {'li': '', 'ig': '', 'tw': ''}
            s_cont = psoup.find('div', class_='bio-social-links') or psoup
            for sa in s_cont.find_all('a', href=True):
                shref = sa['href']
                if 'linkedin.com' in shref: social['li'] = shref
                elif 'instagram.com' in shref: social['ig'] = shref
                elif 'twitter.com' in shref or 'x.com' in shref: social['tw'] = shref
            
            # Use the helper from EmailAwareScraper, or keep existing specific logic if better
            # The existing logic was specific to typical mailto tags.
            # Let's try the helper first, or manual.
            email = "Not Public"
            e_tag = psoup.find('a', href=re.compile(r'^mailto:'))
            if e_tag: 
                email = e_tag['href'].replace('mailto:', '').split('?')[0]
            else:
                # Fallback to text search
                email = self.extract_email_from_soup(psoup)

            results.append({
                'Name': name,
                'Email ID': email,
                'Role/Designation': role,
                'Description': desc,
                'LinkedIn': social['li'],
                'Instagram': social['ig'],
                'Twitter': social['tw'],
                'Source URL': url
            })
            time.sleep(0.5)
        
        # Enforce strict filtering
        final_results = self.filter_results(results)
        self.save_to_csv(final_results)
        return final_results

def main():
    scrapers = [
        MilkenScraper('London', 'Milken Institute', 'https://milkeninstitute.org/events/future-finance-2026/speakers'),
        GenericEmailListScraper('London', 'Pay360', 'https://www.pay360event.com/speakers'),
    ]
    all_data = []
    for s in scrapers:
        try:
            data = s.scrape()
            if data: all_data.extend(data)
        except Exception as e:
            print(f"Failed to run {s.site_name}: {e}")
    return all_data

if __name__ == "__main__":
    main()
