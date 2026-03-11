import re
from bs4 import BeautifulSoup
from base_scraper import BaseScraper, GenericListScraper, EmailAwareScraper, GenericEmailListScraper

class BharatFintechScraper(EmailAwareScraper):
    def scrape(self):
        print(f"Starting {self.site_name} scraper...")
        html = self.fetch(self.base_url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        # Elementor names are often in headers with specific classes
        for h in soup.find_all(['h3', 'h4'], class_=re.compile(r'heading-title', re.I)):
            name = h.get_text(strip=True)
            if len(name) < 3 or len(name) > 40: continue
            if any(x in name.lower() for x in ['subscribe', 'contact', 'sponsor', 'about']): continue

            # Role/Designation is often in a div nearby
            role = "N/A"
            parent = h.find_parent('div', class_='elementor-widget-container')
            email = "Not Public"
            
            if parent:
                # Look for a sibling widget or child div that might have the role
                role_tag = parent.find_next_sibling('div', class_='elementor-widget-text-editor')
                if not role_tag:
                    role_tag = parent.find('div', class_='elementor-text-editor')
                if role_tag:
                    role = role_tag.get_text(strip=True)
                
                # Check parent context for email
                # Often in these Elementor setups, bio info is in the same column
                column = parent.find_parent('div', class_='elementor-column')
                if column:
                    email = self.extract_email_from_soup(column)

            results.append({
                'Name': name,
                'Email ID': email,
                'Role/Designation': role,
                'Description': 'N/A',
                'LinkedIn': '',
                'Instagram': '',
                'Twitter': '',
                'Source URL': self.base_url
            })
        
        # Unique by name
        seen = set()
        unique_results = []
        for r in results:
            if r['Name'] not in seen:
                unique_results.append(r)
                seen.add(r['Name'])
        
        final_results = self.filter_results(unique_results)
        self.save_to_csv(final_results)
        return final_results

def main():
    scrapers = [
        GenericEmailListScraper('India', 'Global Fintech Fest', 'https://globalfintechfest.com/speakers'),
        BharatFintechScraper('India', 'Bharat Fintech Summit', 'https://bharatfintechsummit.com/speakers'),
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

 
