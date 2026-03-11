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

def extract_number(text):
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

def scrape_instagram(hashtag, max_posts=10):
    driver = get_driver(headless=False)
    wait = WebDriverWait(driver, 15)
    scraped = 0
    seen_urls = set()
    tag = hashtag.lstrip("#")

    try:
        driver.get("https://www.instagram.com/")
        print("Please login manually (90 seconds)...")
        time.sleep(90)

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
                    username = driver.find_element(
                        By.XPATH, "//header//a[contains(@href,'/')]"
                    ).text.strip()
                except:
                    username = "-"

                # Post Text
                try:
                    spans = driver.find_elements(By.XPATH, "//article//span")
                    caption = "\n".join([s.text for s in spans if s.text.strip() != ""])
                    if not caption:
                        caption = "-"
                except:
                    caption = "-"

                # Likes
                likes = "-"
                try:
                    like_btn = driver.find_element(
                        By.XPATH, "//button[contains(@aria-label,'like')]"
                    )
                    likes = extract_number(like_btn.get_attribute("aria-label"))
                except:
                    try:
                        like_span = driver.find_element(By.XPATH, "//section//div/span")
                        likes = extract_number(like_span.text)
                    except:
                        likes = "-"

                # Comments
                comments = ""
                try:
                    comment_btn = driver.find_element(
                        By.XPATH, "//button[contains(@aria-label,'comment')]"
                    )
                    comments = extract_number(comment_btn.get_attribute("aria-label"))
                except:
                    comments = 0

                # Shares / Reposts
                shares = ""
                try:
                    share_span = driver.find_element(
                        By.XPATH, "//button//*[name()='svg' and @aria-label='Repost']/following-sibling::span"
                    )
                    shares = extract_number(share_span.text)
                except:
                    shares = "-"

                # Date
                try:
                    date = driver.find_element(By.XPATH, "//time").get_attribute("datetime")
                except:
                    date = "-"

                result = {
                    "username": username,
                    "post_text": caption,
                    "likes": likes,
                    "replies": comments,
                    "shares": shares,
                    "date": date,
                    "url": post_url,
                }

                print(result)
                scraped += 1
                yield result

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

    finally:
        driver.quit()

def save_to_csv(filename, data):
    if not data:
        print(f"No data to save for {filename}")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} records to {filename}")

if __name__ == "__main__":
    hashtag = "AI"
    max_posts = 10
    posts = list(scrape_instagram(hashtag, max_posts))
    save_to_csv(f"instagram_{hashtag.lower()}.csv", posts)
