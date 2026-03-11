from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from driver_utils import get_driver

BASE_URL = "https://exhibitors.gitex.com/gitex-global-2025/Exhibitor"

def scrape_gitex_speakers(keyword, limit=10):
    # Use centralized driver
    driver = get_driver(headless=False)
    wait = WebDriverWait(driver, 30)
    results = []

    try:
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        try:
            search_input = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
                )
            )
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(5)
        except:
            print("Search input not found")

        # Scroll
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5): # Reduced scrolls for speed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        cards = driver.find_elements(
            By.CSS_SELECTOR, "a[href*='/gitex-global-2025/Exhibitor/']"
        )
        
        # Deduplicate cards
        card_urls = []
        unique_cards = []
        for c in cards:
            h = c.get_attribute("href")
            if h and h not in card_urls:
                card_urls.append(h)
                unique_cards.append(c)
        cards = unique_cards

        index = 0
        while index < len(cards):
            if limit and len(results) >= limit:
                break
            try:
                # Re-find cards to avoid stale element
                current_cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/gitex-global-2025/Exhibitor/']")
                if index >= len(current_cards):
                     break
                
                card = current_cards[index]
                url = card.get_attribute("href")
                
                # Check if we already scraped this
                if any(r['profile_url'] == url for r in results):
                    index += 1
                    continue

                index += 1
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                time.sleep(1)
                
                # Click logic
                try:
                    card.click()
                except:
                    driver.execute_script("arguments[0].click();", card)
                
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                name = soup.select_one("h4")
                desc = soup.select_one("p")

                def social(cls):
                    tag = soup.select_one(f"a.{cls}")
                    return tag["href"] if tag and tag.has_attr("href") else ""

                results.append({
                    "company_name": name.get_text(strip=True) if name else "",
                    "designation": desc.get_text(" ", strip=True) if desc else "", # Mapping description to designation to match current config for now
                    "sectors": ", ".join(
                        li.get_text(strip=True)
                        for li in soup.select("ul li")
                    ),
                    "facebook": social("fb_link"),
                    "twitter": social("twitter_link"),
                    "linkedin": social("linkdin_link"),
                    "instagram": social("insta_link"),
                    "youtube": social("youtube_link"),
                    "profile_url": driver.current_url
                })

                driver.back()
                time.sleep(3)
                
            except Exception as e:
                print(f"Error scraping card: {e}")
                try:
                    driver.back()
                    time.sleep(2)
                except:
                    break
    finally:
        driver.quit()

    return results
