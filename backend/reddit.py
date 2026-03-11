import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from driver_utils import get_driver

def scrape_reddit(topic, subreddit=None, min_upvotes=0, max_posts=50, headless=True):

    # Use centralized driver with stealth settings
    driver = get_driver(headless=headless)
    wait = WebDriverWait(driver, 10) # 10s is sufficient if page loads


    seen_urls = set()
    scraped = 0

    def parse_votes(text):
        if not text:
            return 0
        text = text.lower().replace("points", "").strip()
        if "k" in text:
            try:
                return int(float(text.replace("k", "")) * 1000)
            except:
                return 0
        nums = re.findall(r"\d+", text.replace(",", ""))
        return int(nums[0]) if nums else 0

    try:
        if subreddit:
            url = f"https://old.reddit.com/r/{subreddit}/search?q={topic}&restrict_sr=on&sort=relevance"
        else:
            url = f"https://old.reddit.com/search?q={topic}&sort=relevance"

        driver.get(url)
        time.sleep(3)

        while scraped < max_posts:

            try:
                posts = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.search-result")
                    )
                )
            except Exception:
                print(f"No results found or timed out for topic: {topic}")
                if "search results" not in driver.title.lower():
                     print(f"Page title mismatch: {driver.title}")
                break

            for post in posts:
                if scraped >= max_posts:
                    break

                try:
                    title_el = post.find_element(By.CSS_SELECTOR, "a.search-title")
                    title = title_el.text.strip()
                    post_url = title_el.get_attribute("href")

                    if not post_url or post_url in seen_urls:
                        continue
                    seen_urls.add(post_url)

                    try:
                        subreddit_name = post.find_element(
                            By.CSS_SELECTOR, "a.search-subreddit-link"
                        ).text.strip()
                    except:
                        subreddit_name = subreddit or "unknown"

                    try:
                        author = post.find_element(By.CSS_SELECTOR, "a.author").text.strip()
                    except:
                        author = "unknown"

                    try:
                        votes_text = post.find_element(
                            By.CSS_SELECTOR, "span.search-score"
                        ).text
                        upvotes = parse_votes(votes_text)
                    except:
                        upvotes = 0

                    if upvotes < min_upvotes:
                        continue

                    try:
                        comments_text = post.find_element(
                            By.XPATH, ".//a[contains(text(),'comment')]"
                        ).text
                        comments = int(re.findall(r"\d+", comments_text)[0])
                    except:
                        comments = 0

                    yield {
                        "platform": "Reddit",
                        "topic": topic,
                        "title": title,
                        "subreddit": subreddit_name,
                        "user": author,
                        "upvotes": upvotes,
                        "replies": comments,
                        "url": post_url,
                    }

                    scraped += 1

                except:
                    continue

            try:
                driver.find_element(By.LINK_TEXT, "next ›").click()
                time.sleep(2)
            except:
                break

    finally:
        driver.quit()


if __name__ == "__main__":
    for item in scrape_reddit(
        topic="docker",
        subreddit="programming",
        min_upvotes=5,
        max_posts=10,
        headless=True,
    ):
        print(item)
