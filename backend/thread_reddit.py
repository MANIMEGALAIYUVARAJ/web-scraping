from driver_utils import get_driver
from selenium.webdriver.common.by import By
import time

def scrape_thread_reddit(topic, max_threads=3, max_comments_per_thread=20):
    driver = get_driver(headless=False)

    # Use Old Reddit - it's much more stable for scraping
    url = f"https://old.reddit.com/search?q={topic}&sort=relevance"
    driver.get(url)
    time.sleep(3)
    
    # Use reliable selectors (same as main scraper)
    threads = driver.find_elements(By.CSS_SELECTOR, "a.search-title")
    results = []

    # Capture URLs first to avoid stale elements
    all_links = [t.get_attribute("href") for t in threads[:max_threads*2] if t.get_attribute("href")]
    
    # Filter for actual threads, not subreddits
    thread_urls = [u for u in all_links if "/comments/" in u][:max_threads]

    for thread_url in thread_urls:
        try:
            print(f"Scraping thread: {thread_url}")
            driver.execute_script("window.open(arguments[0]);", thread_url)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            try:
                title = driver.find_element(By.CSS_SELECTOR, "a.title").text
            except:
                title = driver.title

            # Old Reddit Comment Selectors - Broadened
            # div.comment contains the comment block
            # .usertext-body .md contains the actual text
            comments = driver.find_elements(By.CSS_SELECTOR, "div.comment .usertext-body .md")
            print(f"   -> Found {len(comments)} comments")
            count = 0

            for comment in comments:
                if count >= max_comments_per_thread:
                    break

                text = comment.text.strip()
                if text:
                    results.append({
                        "platform": "Reddit Thread",
                        "topic": topic,
                        "thread_url": thread_url,
                        "post_title": title,
                        "subreddit": "unknown",
                        "post_author": "unknown",
                        "comment_author": "unknown",
                        "comment_text": text,
                        "comment_upvotes": "0"
                    })
                    count += 1
            
            # Close tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"⚠️ Thread skipped {thread_url}: {e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            continue
    
    driver.quit()
    return results
