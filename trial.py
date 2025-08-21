import requests
import json
from base64 import b64decode
from bs4 import BeautifulSoup

# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual Zyte API key.
ZYTE_API_KEY = "31d677029a054280a79b6086ad61db26"

# Example Flipkart URL to scrape.
FLIPKART_URL = "https://www.flipkart.com/search?q=shirt"

# --- Main Scraping Logic ---
def scrape_flipkart_search(api_key, url):
    """
    Scrapes a Flipkart search results page for its HTML, then extracts a list
    of products with their title, price, and URL.

    Args:
        api_key (str): Your Zyte API key.
        url (str): The Flipkart search results URL to scrape.

    Returns:
        list: A list of dictionaries, where each dictionary represents a product.
              Returns None on error.
    """
    if api_key == "YOUR_API_KEY" or not api_key:
        print("❌ Error: Please replace 'YOUR_API_KEY' with your actual Zyte API key.")
        return None

    print(f"▶️  Sending request to Zyte API for URL: {url}")

    try:
        # Make the POST request to the Zyte API endpoint
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json={
                "url": url,
                "httpResponseBody": True,  # Request the raw HTML body
            },
            timeout=90 # Increased timeout for potentially larger pages
        )

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        api_response_json = response.json()
        print("✅ Successfully received data from Zyte API.")

        # Decode the base64 HTML content
        html_body_bytes = b64decode(api_response_json["httpResponseBody"])
        
        # --- Parsing Logic ---
        print("🔎 Parsing HTML and extracting product data...")
        soup = BeautifulSoup(html_body_bytes, 'html.parser')
        
        products = []
        # Find all elements that are individual search results
        result_items = soup.find_all('div', {'class': '_1AtVbE'})
        
        if not result_items:
            print("⚠️ No product items found. Flipkart's layout may have changed.")
            return []

        for item in result_items:
            # Find the title, which is in the 'title' attribute of the 'a' tag
            title_element = item.find('a', class_='s1Q9rs')
            title = title_element.get('title') if title_element else None

            # Find the price
            price_element = item.find('div', class_='_30jeq3')
            price = price_element.get_text(strip=True) if price_element else None

            # Find the product URL
            url_element = item.find('a', class_='s1Q9rs')
            product_url = "https://www.flipkart.com" + url_element['href'] if url_element else None

            # Only add products that have a title and URL
            if title and product_url:
                products.append({
                    'title': title,
                    'price': price,
                    'url': product_url
                })
        
        return products

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the API request: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during parsing: {e}")
        return None


# Scrape Flipkart
scraped_products_flipkart = scrape_flipkart_search(ZYTE_API_KEY, FLIPKART_URL)

if scraped_products_flipkart:
    print(f"\n--- Found {len(scraped_products_flipkart)} products on Flipkart ---")
    # Print details for all found products
    for product in scraped_products_flipkart:
        print(json.dumps(product, indent=2))
    print("\n-------------------------------------------")


# # import time
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # # 1. The URL of the product page
# # url = "https://www.flipkart.com/asus-expertbook-p1-intel-core-i3-13th-gen-1315u-16-gb-512-gb-ssd-windows-11-home-p1403cva-s60938ws-thin-light-laptop/p/itm0af4b81838b5b?pid=COMH8Z2QAWCCUCSP&lid=LSTCOMH8Z2QAWCCUCSPPZPFKG&marketplace=FLIPKART&q=laptop&store=6bo%2Fb5g&srno=s_1_10&otracker=search&fm=organic&iid=518b7e5a-321c-4312-881f-ad1e65da51ef.COMH8Z2QAWCCUCSP.SEARCH&ppt=None&ppn=None&ssid=whs9nfneao0000001755666159333&qH=312f91285e048e09"

# # # 2. Set up Chrome options (optional, but good practice)
# # options = webdriver.ChromeOptions()
# # # options.add_argument("--headless") # Uncomment to run without opening a browser window
# # options.add_argument("--start-maximized")

# # # 3. Initialize the WebDriver
# # driver = webdriver.Chrome(options=options)
# # print("▶️  WebDriver initialized.")

# # try:
# #     # 4. Navigate to the URL
# #     driver.get(url)
# #     print(f"🔗 Navigating to URL...")

# #     # 5. Wait for the elements to be loaded on the page
# #     # This is a crucial step! We wait up to 10 seconds for the title to become visible.
# #     wait = WebDriverWait(driver, 10)
    
# #     # Wait for the title element and then find it
# #     title_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'VU-ZEz')))
# #     title = title_element.text.strip()

# #     # Wait for the price element and then find it
# #     # Note: We use By.CSS_SELECTOR because the class name has a space.
# #     price_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.Nx9bqj.CxhGGd')))
# #     price = price_element.text.strip()
    
# #     # 6. Print the results
# #     print("\n--- ✅ Product Details Scraped ---")
# #     print(f"Title: {title}")
# #     print(f"Price: {price}")
# #     print("----------------------------------")

# # except TimeoutException:
# #     print("❌ Error: Timed out waiting for page elements to load. The page structure might have changed.")
# # except NoSuchElementException:
# #     print("❌ Error: An element was not found. The class name might be incorrect.")
# # except Exception as e:
# #     print(f"An unexpected error occurred: {e}")

# # finally:
# #     # 7. Close the browser
# #     print("🛑 Closing the browser.")
# #     driver.quit()


# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# # 1. The URL of the search results page
# url = "https://www.flipkart.com/search?q=laptop"

# # 2. Set up Chrome options
# options = webdriver.ChromeOptions()
# # options.add_argument("--headless") # Uncomment to run without opening a browser window
# options.add_argument("--start-maximized")

# # 3. Initialize the WebDriver
# driver = webdriver.Chrome(options=options)
# print("▶️  WebDriver initialized.")

# try:
#     # 4. Navigate to the URL
#     driver.get(url)
#     print(f"🔗 Navigating to URL...")

#     # 5. Wait for the product images to be loaded
#     # We will wait for at least one image with the class '_396cs4' to be visible.
#     wait = WebDriverWait(driver, 10)
#     wait.until(EC.visibility_of_element_located((By.CLASS_NAME, '_396cs4')))
#     print("✅ Product images are visible.")

#     # 6. Find all the image elements
#     # The main product images on the search page have the class '_396cs4'
#     image_elements = driver.find_elements(By.CLASS_NAME, '_396cs4')
    
#     image_urls = []
#     print(f"🔎 Found {len(image_elements)} product images. Extracting URLs...")

#     # 7. Loop through the elements and get the 'src' attribute
#     for img_element in image_elements:
#         # Use .get_attribute('src') to get the URL from the image tag
#         src_url = img_element.get_attribute('src')
#         if src_url:
#             image_urls.append(src_url)

#     # 8. Print the results
#     print("\n--- 🖼️ Scraped Image URLs ---")
#     for i, img_url in enumerate(image_urls):
#         print(f"{i + 1}: {img_url}")
#     print("----------------------------")


# except TimeoutException:
#     print("❌ Error: Timed out waiting for product images to load. The page structure or class names may have changed.")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

# finally:
#     # 9. Close the browser
#     print("🛑 Closing the browser.")
#     driver.quit()