import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError

async def scrape_activities(url: str):
    """
    Launches a browser, navigates to a URL, and scrapes activity data.

    This function identifies activity cards based on their HTML structure and extracts
    the name, rating, number of reviews, and a relative URL for each activity.

    Args:
        url: The URL of the page to scrape.
    """
    print("🚀 Starting the scraping process...")
    async with async_playwright() as p:
        # Change headless=False to see the browser UI
        browser = await p.chromium.launch(headless=False) 
        page = await browser.new_page()

        try:
            # Navigate to the target URL
            print(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("Page loaded. Searching for activity cards...")

            # XPath to locate each main activity card <article> element.
            card_xpath = "//article[.//h3 and .//div[@data-automation='bubbleRatingValue']]"
            
            # Wait for the first card to appear to ensure the page is ready
            await page.wait_for_selector(card_xpath, timeout=30000)
            
            activity_cards = await page.locator(card_xpath).all()

            if not activity_cards:
                print("❌ No activity cards found matching the expected structure.")
                return

            print(f"✅ Found {len(activity_cards)} activities. Extracting details...\n")
            
            results = []
            for card in activity_cards:
                try:
                    # FIX: Explicitly use "xpath=" to avoid confusion with CSS selectors.
                    name = await card.locator("xpath=.//h3").inner_text()

                    # FIX: Explicitly use "xpath="
                    rating = await card.locator("xpath=.//div[@data-automation='bubbleRatingValue']/span").inner_text()

                    # FIX: Explicitly use "xpath="
                    reviews_raw = await card.locator("xpath=.//div[@data-automation='bubbleReviewCount']/span").inner_text()
                    reviews = re.sub(r'[(),]', '', reviews_raw).strip()

                    # FIX: Explicitly use "xpath="
                    activity_url = await card.locator("xpath=.//a[.//h3]").get_attribute("href")
                    
                    results.append({
                        "name": name.strip(),
                        "rating": rating.strip(),
                        "reviews": reviews,
                        "url": activity_url.strip()
                    })

                except Exception as e:
                    # This will catch errors if a specific card is missing an element
                    print(f"⚠️ Could not fully process a card, skipping. Error: {e}")
            
            # Print all collected results
            for item in results:
                print("----------------------------------------")
                print(f"Activity Name: {item['name']}")
                print(f"Rating: {item['rating']}")
                print(f"Number of Reviews: {item['reviews']}")
                print(f"Activity URL: https://www.tripadvisor.com{item['url']}")
            print("----------------------------------------")


        except TimeoutError:
            print("❌ Timed out waiting for page content to load or for activity cards to appear.")
            print("   The page might be protected by anti-scraping measures or the structure may have changed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            await browser.close()
            print("\n🎉 Scraping process finished. Browser closed.")


async def main():
    """Main function to run the scraper."""
    target_url = input("Please enter the full URL to scrape: ")
    if target_url.strip():
        await scrape_activities(target_url)
    else:
        print("No URL provided. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())