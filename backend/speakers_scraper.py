import time
import csv
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

# ==========================
# DRIVER SETUP
# ==========================
def start_driver(headless=True):
    return get_driver()

def wait():
    time.sleep(random.uniform(2, 5))

# ==========================
# SCRAPER
# ==========================
def scrape_speakers(role_filter="", max_results=10, output_file="speakers.csv"):
    BASE_URL = "https://www.tngss.startuptn.in/speakers"
    driver = start_driver(headless=True)
    wait_driver = WebDriverWait(driver, 20)

    print("\n🚀 Starting StartupTN speakers scraper")
    driver.get(BASE_URL)
    wait_driver.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)

    # Scroll to load all profiles
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(15):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Collect profile links
    links = []
    cards = driver.find_elements(By.XPATH, "//a[contains(@href,'/speakers/')]")
    for card in cards:
        href = card.get_attribute("href")
        if href and href not in links:
            links.append(href)
    print(f"🔗 Found {len(links)} speaker profiles")

    results = []

    # CSV writer
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name","Designation","Organization","Location","About",
            "LinkedIn","Experience","ImageURL","ProfileURL"
        ])

        for i, link in enumerate(links, 1):
            if len(results) >= max_results:
                print("🛑 Limit reached")
                break

            driver.get(link)
            try:
                wait_driver.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
            except:
                continue
            time.sleep(1)

            name = driver.find_element(By.TAG_NAME, "h2").text.strip()
            h3s = driver.find_elements(By.TAG_NAME, "h3")
            designation = h3s[0].text.strip() if len(h3s) > 0 else ""
            organization = h3s[1].text.strip() if len(h3s) > 1 else ""

            # Filter by role
            if role_filter and role_filter.lower() not in designation.lower():
                continue

            try:
                location = driver.find_element(By.XPATH, "//span[contains(text(),',')]").text.strip()
            except:
                location = ""

            about = " ".join([p.text.strip() for p in driver.find_elements(By.TAG_NAME, "p") if p.text.strip()])
            linkedin_elem = driver.find_elements(By.XPATH, "//a[contains(@href,'linkedin.com')]")
            linkedin = linkedin_elem[0].get_attribute("href") if linkedin_elem else ""
            image_elem = driver.find_elements(By.TAG_NAME, "img")
            image = image_elem[0].get_attribute("src") if image_elem else ""

            # Experience
            experience = []
            exp_sections = driver.find_elements(By.XPATH, "//h4[normalize-space()='Experience']/following-sibling::div//article")
            for exp in exp_sections:
                try:
                    title = exp.find_element(By.TAG_NAME, "h4").text.strip()
                except:
                    title = ""
                roles = [p.text.strip() for p in exp.find_elements(By.TAG_NAME, "p")]
                experience.append(f"{title} | {' | '.join(roles)}")

            results.append({
                "name": name,
                "designation": designation,
                "organization": organization,
                "location": location,
                "about": about,
                "linkedin": linkedin,
                "experience": " || ".join(experience),
                "imageurl": image,
                "profileurl": link
            })

            writer.writerow([
                name, designation, organization, location, about,
                linkedin, " || ".join(experience), image, link
            ])

            print(f"✅ {len(results)}/{max_results} → {name}")

    driver.quit()
    print(f"\n🎉 Speakers scraping completed! Saved at {output_file}")
    return results

# ==========================
# DIRECT RUN
# ==========================
if __name__ == "__main__":
    scrape_speakers(role_filter="CEO", max_results=5)
