import requests
import json
from base64 import b64decode
from bs4 import BeautifulSoup

# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual Zyte API key.
ZYTE_API_KEY = "31d677029a054280a79b6086ad61db26"

# Example Amazon URL to scrape. This can be a product or search page.
AMAZON_URL = "https://www.amazon.com/s?k=shirt"

# --- Main Scraping Logic ---
def scrape_amazon_search(api_key, url):
    """
    Scrapes an Amazon search results page for its HTML, then extracts a list
    of products with their title, price, and URL.

    Args:
        api_key (str): Your Zyte API key.
        url (str): The Amazon search results URL to scrape.

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
        # Amazon often uses 's-result-item' for this container class
        result_items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        if not result_items:
            print("⚠️ No product items found. Amazon's layout may have changed.")
            return []

        for item in result_items:
            title_element = item.find('h2')
            title = title_element.get_text(strip=True) if title_element else None

            # Find the price
            price_whole = item.find('span', class_='a-price-whole')
            price_fraction = item.find('span', class_='a-price-fraction')
            price = f"{price_whole.text}{price_fraction.text}" if price_whole and price_fraction else None

            # Find the product URL
            url_element = item.find('a', class_='a-link-normal')
            product_url = "https://www.amazon.com" + url_element['href'] if url_element else None

            # Only add products that have a title and URL
            if title and product_url and not "spons" in product_url:
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


scraped_products = scrape_amazon_search(ZYTE_API_KEY, AMAZON_URL)

if scraped_products:
    print(f"\n--- Found {len(scraped_products)} products ---")
    # Print details for the first 5 products for brevity
    for product in scraped_products[:]:
        print(json.dumps(product, indent=2))
    print("\n-------------------------------------------")

