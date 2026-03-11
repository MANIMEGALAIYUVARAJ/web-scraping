import time
import re
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =====================================================
# CONFIG
# =====================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_csvs")
HEADLESS = True  # True → headless browser (works in Docker)
MAX_SCROLL = 6   # Number of scrolls to load videos

# =====================================================
# MAIN SCRAPER FUNCTION
# =====================================================
def scrape_youtube(topic, max_videos=6):
    print(f"\n🎥 YOUTUBE SCRAPER STARTED")
    print(f"🔎 Topic      : {topic}")
    print(f"🎯 Max Videos : {max_videos}")

    # ---------------------------
    # CHROME OPTIONS
    # ---------------------------
    # ---------------------------
    # WEBDRIVER (Centralized)
    # ---------------------------
    from driver_utils import get_driver
    driver = get_driver(headless=False)
    wait = WebDriverWait(driver, 15)

    try:
        # SEARCH PAGE
        query = topic.replace(" ", "+")
        search_url = f"https://www.youtube.com/results?search_query={query}"
        driver.get(search_url)
        time.sleep(4)

        # Scroll to load videos
        for _ in range(MAX_SCROLL):
            driver.execute_script("window.scrollBy(0, 1200)")
            time.sleep(2)

        # Collect video links
        video_links = []
        try:
            # More robust selector for video tiles
            video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"][contains(@href, "/watch?v=")]')
            for v in video_elements:
                link = v.get_attribute("href")
                if link and link not in video_links:
                    video_links.append(link)
        except:
            print("Error finding video links")

        video_links = video_links[:max_videos]
        print(f"✅ Found {len(video_links)} videos")

        all_data = []

        # SCRAPE EACH VIDEO
        for idx, url in enumerate(video_links, start=1):
            print(f"📥 Scraping {idx}/{len(video_links)} → {url}")
            driver.get(url)
            time.sleep(3)

            video_id = re.search(r"v=([^&]+)", url)
            video_id = video_id.group(1) if video_id else ""

            # Title
            try:
                title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1//yt-formatted-string'))).text
            except:
                title = ""

            # Channel Name & ID
            try:
                channel_elem = driver.find_element(By.XPATH, '//div[@id="upload-info"]//ytd-channel-name//a')
                channel_name = channel_elem.text
                channel_link = channel_elem.get_attribute("href")
                channel_id = channel_link.split("/")[-1] if channel_link else ""
            except:
                channel_name = ""
                channel_id = ""

            # Views
            try:
                # Look for "X views"
                views_elem = driver.find_element(By.XPATH, '//*[@id="info"]//span[contains(text(), "views")]')
                views = views_elem.text.split(" ")[0]
            except:
                views = "0"

            # Published Date (often in description snippet or under title)
            try:
                # Try finding the "X days ago" or date string
                pub_elem = driver.find_element(By.XPATH, '//*[@id="info"]//span[contains(text(), "ago") or contains(text(), "20")]')
                published = pub_elem.text
            except:
                published = ""

            # Likes
            try:
                # This is tricky. Look for the like button and its likely format.
                # Assuming the button text or aria-label contains the count.
                like_btn = driver.find_element(By.XPATH, '//like-button-view-model//button')
                likes = like_btn.get_attribute("aria-label") # "Like this video along with 1,234 other people"
                if likes:
                    likes = re.search(r"([\d,]+)", likes)
                    likes = likes.group(1) if likes else "0"
            except:
                likes = "0"

            # Comments (Count is hard to get reliably without scrolling down)
            comments = "0"
            
            # Description
            try:
                # Expand description first if needed
                driver.execute_script("document.querySelectorAll('#expand').forEach(b => b.click())")
                time.sleep(1)
                description = driver.find_element(By.XPATH, '//div[@id="description-inner"]').text[:200]
            except:
                description = ""

            all_data.append({
                "topic": topic,
                "video_id": video_id,
                "title": title,
                "channel_name": channel_name,
                "channel_id": channel_id,
                "views": views,
                "likes": likes,
                "comments": comments,
                "published_date": published,
                "description": description,
                "url": url
            })

        # SAVE CSV
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{topic.replace(' ', '_')}_youtube_full.csv")
        pd.DataFrame(all_data).to_csv(output_file, index=False, encoding="utf-8-sig")

        print("\n🎉 SCRAPING COMPLETED")
        print(f"📁 Saved to: {output_file}")
        return all_data, output_file

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_youtube("AI", max_videos=5)
