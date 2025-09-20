import time
from playwright.sync_api import sync_playwright, TimeoutError

def extract_text_from_xpaths(url: str, xpaths: list[str]):
    """
    Launches a headed browser, navigates to a URL, and extracts text
    from a list of specified XPaths.

    Args:
        url: The URL of the webpage to scrape.
        xpaths: A list of XPath strings to locate elements.
    """
    with sync_playwright() as p:
        # Launch the browser. headless=False makes the browser UI visible.
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        try:
            print(f"Navigating to {url}...")
            # Go to the specified URL
            page.goto(url, wait_until="networkidle", timeout=60000)
            print("Page loaded successfully.")

            # Loop through each XPath and extract the text
            for i, xpath in enumerate(xpaths):
                print(f"\n--- Extracting text for XPath {i+1} ---")
                print(f"XPath: {xpath}")
                try:
                    # Locate the element using the XPath
                    element = page.locator(f"xpath={xpath}")
                    
                    # Wait for the element to be visible
                    element.wait_for(timeout=5000)

                    # Get the inner text of the element
                    text_content = element.inner_text()
                    
                    print(f"Extracted Text: {text_content.strip()}")

                except TimeoutError:
                    print(f"Error: Element not found or timed out for XPath: {xpath}")
                except Exception as e:
                    print(f"An unexpected error occurred for XPath {xpath}: {e}")
            
            # Give user time to see the last state of the browser
            print("\nExtraction complete. Closing browser in 10 seconds...")
            time.sleep(10)

        except TimeoutError:
            print(f"Error: Timed out while loading the page at {url}. Please check the URL and your connection.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Cleanly close the browser
            browser.close()
            print("Browser closed.")


if __name__ == "__main__":
    # The list of XPaths you want to extract text from
    target_xpaths = [
        "/html/body/div/main/div/div[2]/div[2]/div[2]/div/div[1]/section[1]/div/div/div/div/div[2]/h1",
        "/html/body/div/main/div/div[2]/div[2]/div[2]/div/div[1]/section[1]/div/div/div/div/div[3]/div[1]/div/div/span/div/span",
        "/html/body/div/main/div/div[2]/div[2]/div[2]/div/div[1]/section[2]/div/div/div[2]/div[1]/div[2]/section[1]/div/div/div/div/div[1]/div",
        "/html/body/div/main/div/div[2]/div[2]/div[2]/div/div[1]/section[2]/div/div/div[2]/div[1]/div[2]/section[5]/div/div"
    ]
    
    # Prompt the user to enter a URL
    input_url = input("Please enter the full URL (e.g., https://www.example.com): ")

    if input_url:
        extract_text_from_xpaths(input_url, target_xpaths)
    else:
        print("No URL provided. Exiting.")
