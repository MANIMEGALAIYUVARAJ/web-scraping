import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from driver_utils import get_driver

def scrape_twitter(hashtag, max_posts=10):

    print("\n🐦 TWITTER HASHTAG SCRAPER STARTED")
    print(f"Hashtag   : {hashtag}")
    print(f"Max Posts : {max_posts}\n")

    driver = None
    scraped = 0
    seen_urls = set()

    # ===============================
    # HELPERS
    # ===============================
    def safe_text(parent, xpath):
        try:
            return parent.find_element(By.XPATH, xpath).text
        except:
            return ""

    def parse_number(text):
        if not text:
            return 0
        text = text.replace(",", "").strip()
        if text.endswith("K"):
            return int(float(text[:-1]) * 1000)
        if text.isdigit():
            return int(text)
        return 0

    try:
        # ===============================
        # ✅ DRIVER SETUP (Centralized)
        # ===============================
        # Use headless=False to allow manual login if needed
        driver = get_driver(headless=False)

        # ===============================
        # ✅ MANUAL LOGIN
        # ===============================
        driver.get("https://x.com/login")
        print("⚠️ Please login manually within 90 seconds...")
        time.sleep(60)

        # ===============================
        # ✅ HASHTAG SEARCH
        # ===============================
        search_url = f"https://x.com/search?q=%23{hashtag.lstrip('#')}&src=typed_query&f=top"
        driver.get(search_url)
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight")

        while scraped < max_posts:
            tweets = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

            for tweet in tweets:
                if scraped >= max_posts:
                    break

                try:
                    link_el = tweet.find_element(By.XPATH, ".//a[contains(@href,'/status/')]")
                    url = link_el.get_attribute("href")

                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    content = safe_text(tweet, ".//div[@data-testid='tweetText']")
                    if not content:
                        continue

                    username = safe_text(tweet, ".//span[contains(text(),'@')]")

                    stats = tweet.find_elements(By.XPATH, ".//div[@role='group']//span")
                    replies = parse_number(stats[0].text) if len(stats) > 0 else 0
                    retweets = parse_number(stats[1].text) if len(stats) > 1 else 0
                    likes = parse_number(stats[2].text) if len(stats) > 2 else 0

                    data = {
                        "username": username,
                        "post_text": content,
                        "likes": likes,
                        "replies": replies,
                        "shares": retweets,
                        "date": "",
                        "url": url
                    }

                    scraped += 1
                    print(f"🐦 Twitter → {scraped}/{max_posts}")

                    yield data

                except Exception as e:
                    print("⚠️ Skipped tweet:", e)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("⚠️ No more tweets loading")
                break
            last_height = new_height

        print(f"\n✅ COMPLETED → {scraped} tweets scraped")

    except Exception as e:
        print("❌ Twitter scraper error:", e)

    finally:
        if driver:
            driver.quit()


# ==============================
# TEST RUN
# ==============================
if __name__ == "__main__":
    for tweet in scrape_twitter("AI", max_posts=5):
        print(tweet)
