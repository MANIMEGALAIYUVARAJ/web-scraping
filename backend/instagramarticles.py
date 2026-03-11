import time
import re
import csv
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import get_driver

# ---------- Helper functions ----------
def extract_number(text):
    """Convert Instagram likes/comments like '20.9K' or '1.2M' to int"""
    if not text:
        return 0
    text = text.replace(",", "").upper()
    match = re.search(r"([\d\.]+)\s*([KM]?)", text)
    if not match:
        return 0
    number, magnitude = match.groups()
    number = float(number)
    if magnitude == "K":
        number *= 1000
    elif magnitude == "M":
        number *= 1_000_000
    return int(number)

def click_next(driver, wait):
    """Click next post button"""
    xpaths = [
        "//button//*[name()='svg' and @aria-label='Next']/ancestor::button",
        "//button//*[name()='svg' and @aria-label='Next']",
    ]
    for xp in xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return True
        except:
            continue
    return False

def save_to_csv(filename, data):
    """Save list of dictionaries to CSV"""
    if not data:
        print(f"No data to save for {filename}")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} records to {filename}")

# ---------- Instagram Hashtag Scraper ----------
def scrape_instagram_hashtag(tag, max_posts=10):
    """Scrape Instagram posts from a hashtag"""
    driver = get_driver(headless=False)
    wait = WebDriverWait(driver, 15)
    scraped = 0
    seen_urls = set()
    tag = tag.lstrip("#")
    results = []

    try:
        driver.get("https://www.instagram.com/")
        print("Please login manually (you have 90 seconds)...")
        time.sleep(90)  # Manual login

        driver.get(f"https://www.instagram.com/explore/tags/{tag}/")
        time.sleep(6)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/p/')]"))
        ).click()
        time.sleep(3)

        while scraped < max_posts:
            try:
                post_url = driver.current_url
                if post_url in seen_urls:
                    if not click_next(driver, wait):
                        break
                    time.sleep(1)
                    continue

                seen_urls.add(post_url)

                # Username
                try:
                    # Try finding the username link in the header
                    username = driver.find_element(By.XPATH, "//header//a[not(contains(@href,'explore'))]").text.strip()
                except:
                    username = "-"

                # Post Text (Caption)
                try:
                    # Instagram captions are often in an h1 or the first span of the comment section
                    caption_elem = driver.find_element(By.XPATH, "//h1")
                    caption = caption_elem.text.strip()
                except:
                    try:
                        # Fallback: First comment-like structure
                        caption = driver.find_element(By.XPATH, "//div[@role='button']/following-sibling::div//span").text
                    except:
                        caption = "-"

                # Likes
                likes = 0
                try:
                    # Look for text "likes" and get the number before it
                    # Logic: Find element containing "likes", then parse text
                    like_elems = driver.find_elements(By.XPATH, "//*[contains(text(), 'likes')]")
                    for elem in like_elems:
                        if "likes" in elem.text:
                            likes = extract_number(elem.text)
                            if likes > 0:
                                break
                    
                    # Fallback: specific button/span
                    if likes == 0:
                        like_span = driver.find_element(By.XPATH, "//section//span[contains(@class, 'html-span')]") 
                        likes = extract_number(like_span.text)
                except:
                    likes = 0

                # Date
                try:
                    date_elem = driver.find_element(By.XPATH, "//time")
                    date = date_elem.get_attribute("title")  # "Dec 17, 2025"
                    if not date:
                         date = date_elem.get_attribute("datetime")
                except:
                    date = "-"
                
                # Comments (Count)
                comments = 0
                try:
                    # Try to find "View all X comments" button
                    comment_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'comments')]")
                    for btn in comment_btns:
                        comments = extract_number(btn.text)
                        if comments > 0:
                            break
                except:
                    comments = 0

                result = {
                    "platform": "Instagram",
                    "topic": tag,
                    "username": username,
                    "post_text": caption,
                    "likes": likes,
                    "comments": comments,
                    "shares": 0,
                    "date": date,
                    "url": post_url
                }

                print(f"Scraped: {username} | {post_url}")
                results.append(result)
                scraped += 1

                if scraped >= max_posts:
                    break

                if not click_next(driver, wait):
                    break

                time.sleep(random.uniform(1.5, 2.5))

            except (TimeoutException, StaleElementReferenceException):
                continue
            except Exception as e:
                print("Error:", e)
                continue

        return results

    finally:
        driver.quit()

# ---------- Main ----------
if __name__ == "__main__":
    hashtag = "AI"
    max_posts = 10

    posts = scrape_instagram_hashtag(hashtag, max_posts)
    save_to_csv(f"instagram_hashtag_{hashtag.lower()}.csv", posts)
