import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from driver_utils import get_driver


def scrape_linkedin_articles(query, limit=10, filters=None, debug=False):
    if filters is None:
        filters = {}

    results = []
    seen_urls = set()
    min_likes = int(filters.get("min_likes", 0))

    # Use existing Chrome profile (for login)
    # Use absolute path relative to this script (backend/chrome-profile)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "chrome-profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    # Lock file cleanup is now handled by driver_utils.get_driver()

    # Use robust driver initialization from driver_utils
    # This handles version matching, anti-detection, and timeouts automatically
    driver = get_driver(headless=(not debug), profile_path=profile_path)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://www.linkedin.com/")
        print("Ensure LinkedIn login is done in this profile...")
        time.sleep(5)  # wait for page to load

        # Verify login state
        if "session_redirect" in driver.current_url or "login" in driver.current_url:
            raise RuntimeError("LinkedIn Login Required. Please run 'python backend/login_linkedin.py' in your terminal and log in.")

        try:
             # Check for "Sign In" button or similar indicators of being logged out
             driver.find_element(By.XPATH, "//a[contains(text(), 'Sign in')]|//button[contains(text(), 'Sign in')]")
             raise RuntimeError("LinkedIn Login Required (Sign In button detected). Please run 'python backend/login_linkedin.py'.")
        except RuntimeError:
             raise
        except:
             pass # Element not found, assume logged in

        search_url = f"https://www.linkedin.com/search/results/content/?keywords={query}"
        driver.get(search_url)
        time.sleep(6)

        # Scroll to load posts
        for _ in range(5): # Reduced for speed, increase for production
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Broad container for both organic and promoted updates
        # Primary selector: Content search results often look like feed updates
        selectors = [
            "//div[contains(@class,'feed-shared-update-v2')]",
            "//li[contains(@class, 'reusable-search__result-container')]",
            "//div[contains(@data-urn, 'urn:li:activity')]",
            "//div[contains(@class, 'update-components-actor')]/ancestor::div[contains(@class, 'feed-shared-update-v2')]"
        ]
        
        posts = []
        for sel in selectors:
            posts = driver.find_elements(By.XPATH, sel)
            if posts:
                print(f"✅ Found {len(posts)} posts using selector: {sel}")
                break
        
        if not posts:
            # Ensure the output directory exists for debug files
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # DEBUG: Save page source to analyze why no articles were found
            try:
                source_path = os.path.join(output_dir, "debug_linkedin_source.html")
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved debug HTML to {os.path.abspath(source_path)}")
            except Exception as e:
                print(f"Failed to save debug HTML: {e}")

            print(f"❌ Found 0 potential posts. Sceenshotting page...")
            screenshot_path = os.path.join(output_dir, "debug_linkedin_failure.png")
            driver.save_screenshot(screenshot_path)
            print(f"Saved failure screenshot to: {os.path.abspath(screenshot_path)}")
            # Use View Page Source if needed, but screenshot is best for user
            
        print(f"Found {len(posts)} potential posts")

        for post in posts:
            if len(results) >= limit:
                break

            # 1. Post Text
            try:
                # Try multiple common selectors for text
                text_elem = None
                text_selectors = [
                    ".//div[contains(@class,'update-components-text')]",
                    ".//span[contains(@class,'break-words')]/span", 
                    ".feed-shared-update-v2__description"
                ]
                
                for t_sel in text_selectors:
                    try:
                        if t_sel.startswith("//") or t_sel.startswith(".//"):
                            text_elem = post.find_element(By.XPATH, t_sel)
                        else:
                            text_elem = post.find_element(By.CSS_SELECTOR, t_sel)
                        if text_elem: break
                    except: continue

                text = text_elem.text if text_elem else "No text found"
            except:
                text = "No text found"

            # 2. Author
            try:
                # From Screenshot 1: .update-components-actor__title contains the name
                # Structure: span.update-components-actor__title > span[dir=ltr] > span[aria-hidden=true]
                author_elem = post.find_element(By.CSS_SELECTOR, ".update-components-actor__title")
                author = author_elem.find_element(By.XPATH, ".//span[@dir='ltr']/span[@aria-hidden='true']").text
            except:
                try:
                    # Fallback: Just the title text
                    author = post.find_element(By.CSS_SELECTOR, ".update-components-actor__title").text.split("\n")[0]
                except:
                    try:
                        # Old fallback
                        author = post.find_element(By.CSS_SELECTOR, ".update-components-actor__name").text.split("\n")[0]
                    except:
                        author = "Unknown"

            # 3. Post URL & Date
            post_url = ""
            date = ""
            try:
                # Improved URL Extraction
                
                # 0. Try data-urn attribute on the post element itself (Most reliable)
                try:
                    urn = post.get_attribute("data-urn")
                    if urn:
                        post_url = f"https://www.linkedin.com/feed/update/{urn}"
                except: pass

                # 1. Look for the distinct 'feed/update/' link which is often the timestamp
                if not post_url:
                    try:
                        # Search for any link containing 'feed/update'
                        link_elem = post.find_element(By.XPATH, ".//a[contains(@href, 'feed/update')]")
                        post_url = link_elem.get_attribute("href").split('?')[0]
                        # Usually this same link contains the date text
                        date_text = link_elem.text.strip()
                        date = date_text.split("•")[0].strip()
                    except:
                        pass

                # 2. Try the permalink anchor by class
                if not post_url:
                    try:
                        link_elem = post.find_element(By.CSS_SELECTOR, "a.update-components-actor__sub-description")
                        post_url = link_elem.get_attribute("href").split('?')[0]
                        date_text = link_elem.text.strip()
                        date = date_text.split("•")[0].strip()
                    except:
                        pass

                # 2b. Try meta-link (often the timestamp link)
                if not post_url:
                    try:
                        link_elem = post.find_element(By.CSS_SELECTOR, "a.update-components-actor__meta-link")
                        post_url = link_elem.get_attribute("href").split('?')[0]
                        if not date:
                             date = link_elem.text.split("•")[0].strip()
                    except: pass

                # 3. Fallback: Search for 'activity' or 'urn:li:activity' in any anchor
                if not post_url:
                    try:
                        links = post.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and ("feed/update" in href or "activity" in href):
                                post_url = href.split('?')[0]
                                break
                    except:
                        pass

            except Exception as e:
                print(f"Error extracting URL: {e}")

            # Validation: Skip if really nothing useful found
            if text == "No text found" and not post_url:
                continue

            # 4. Social Counts (Likes, Comments, Shares)
            likes = 0
            comments = 0
            shares = 0
            
            try:
                # Reactions/Likes
                # Look for the small count next to the icon - often strictly numbers + "comments"
                # Using a more generic approach if specific class fails: look for the social-counts container
                likes_elem = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__reactions-count")
                likes = int(re.sub(r'\D', '', likes_elem.text))
            except:
                pass
                
            try:
                # Comments count
                comments_elem = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__comments")
                comments = int(re.sub(r'\D', '', comments_elem.text))
            except:
                pass
                
            try:
                # Shares count
                shares_elem = post.find_element(By.CSS_SELECTOR, ".social-details-social-counts__item--right-aligned")
                shares = int(re.sub(r'\D', '', shares_elem.text))
            except:
                pass

            if likes < min_likes:
                continue

            # Deduplication Check
            unique_key = post_url if post_url else text[:50] # Use URL or first 50 chars of text
            if unique_key in seen_urls:
                continue
            seen_urls.add(unique_key)

            results.append({
                "platform": "LinkedIn",
                "topic": query, 
                "author": author,
                "post_text": text,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "date": date,
                "post_url": post_url
            })

        return results

    finally:
        driver.quit()


def save_to_csv(filename, data):
    if not data:
        print(f"No data to save for {filename}")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        import csv
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} records to {filename}")


if __name__ == "__main__":
    data = scrape_linkedin_articles("data analytics", limit=5)
    for d in data:
        print(d)
    save_to_csv("linkedin_articles.csv", data)
