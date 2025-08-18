from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from base64 import b64decode
from urllib.parse import urljoin
import os # Keep os for future use with environment variables

# --- Main Views ---

def home(request):
    # Create a dictionary to hold all product categories
    product_categories = {
        "Laptops": get_home_products("laptop"),
        "Mobiles": get_home_products("mobile"),
        "Clothes": get_home_products("clothes"),
        "Chocolates": get_home_products("chocolates"),
    }
    
    # Pass this dictionary to the template
    return render(request, 'home.html', {"product_categories": product_categories})

def scrapedsites(request):
    return render(request,'scrapedsites.html')

def contact(request): 
    return render(request,'contact.html')

def search_results(request):
    """
    Handles the search query submitted by the user.
    """
    query = request.GET.get('q')
    products = {}
    if query:
        # We reuse the same function from the homepage, but get more results
        products = get_search_products(query) 
    
    context = {
        "products": products,
        "query": query
    }
    
    return render(request, 'searchresults.html', context)


# --- Data Aggregator Functions ---

def get_home_products(query):
    """ Gathers the top 5 products from each site for the homepage. """
    data = {
        "amazon": amazon(query, limit=5),
        "flipkart": flipkart(query, limit=5),
        "meesho": meesho(query, limit=5),
        "myntra": myntra(query, limit=5),
        "tatacliq": tatacliq(query, limit=5),
        "snapdeal": snapdeal(query, limit=5),
    }
    
    # ADD THIS DEBUGGING BLOCK
    print(f"Amazon results: {len(data['amazon'])}")
    print(f"Flipkart results: {len(data['flipkart'])}")
    print(f"Meesho results: {len(data['meesho'])}")
    print(f"Myntra results: {len(data['myntra'])}")
    print(f"Tatacliq results: {len(data['tatacliq'])}")
    print(f"Snapdeal results: {len(data['snapdeal'])}")
    print("--- Finished scrapers ---")
    
    return data

def get_search_products(query):
    """ Gathers more products for the search results page. """
    data = {
        "amazon": amazon(query, limit=20),
        "flipkart": flipkart(query, limit=20),
        "meesho": meesho(query, limit=20),
        "myntra": myntra(query, limit=20),
        "tatacliq": tatacliq(query, limit=20),
        "snapdeal": snapdeal(query, limit=20),
    }
    return data


# --- Web Scraping Logic ---

def fetch_with_zyte(url):
    # IMPORTANT: Move this API key to your settings.py or environment variables!
    # Example: API_KEY = os.environ.get("ZYTE_API_KEY")
    API_KEY = "31d677029a054280a79b6086ad61db26"
    
    try:
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(API_KEY, ""),
            json={
                "url": url,
                "httpResponseBody": True,
            },
            timeout=60 # Add a timeout
        )
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        http_body = b64decode(response.json().get("httpResponseBody", ""))
        return http_body.decode("utf-8", errors="ignore")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL with Zyte: {e}")
        return None

def amazon(query, limit=5):
    try:
        print(f"-> Scraping Amazon for '{query}'...")
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        html = fetch_with_zyte(url)
        if not html:
            print("   - Amazon: Failed to get HTML from Zyte.")
            return []
            
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("div.s-result-item[data-asin]"):
            title_tag = item.select_one("h2 a span")
            price_whole = item.select_one(".a-price-whole")
            link_tag = item.select_one("h2 a")
            image_tag = item.select_one("img.s-image")

            if title_tag and price_whole and link_tag and image_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": f"₹{price_whole.get_text(strip=True)}",
                    "link": urljoin(url, link_tag['href']),
                    "image_url": image_tag['src']
                })
                if len(results) >= limit: break
        print(f"   - Amazon: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in amazon scraper: {e}")
        return []

def flipkart(query, limit=5):
    try:
        print(f"-> Scraping Flipkart for '{query}'...")
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        html = fetch_with_zyte(url)
        if not html:
            print("   - Flipkart: Failed to get HTML from Zyte.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("div._1AtVbE, div._4ddWXP, div._2kHMtA, div.slAVV4"):
            title_tag = item.select_one("div._4rR01T, a.s1Q9rs, .IRpwTa, a.wjcEIp")
            price_tag = item.select_one("div._30jeq3")
            link_tag = item.select_one("a._1fQZEK, a.s1Q9rs, a._2UzuFa, a.wjcEIp")
            image_tag = item.select_one("img._396cs4, img._2r_T1I")
            
            if title_tag and price_tag and link_tag and image_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": price_tag.get_text(strip=True),
                    "link": urljoin(url, link_tag['href']),
                    "image_url": image_tag.get('src')
                })
                if len(results) >= limit: break
        print(f"   - Flipkart: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in flipkart scraper: {e}")
        return []

def direct_scrape(url):
    # Utility for direct scraping, error handling is in the calling function.
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()
    return response.text

def meesho(query, limit=5):
    try:
        print(f"-> Scraping Meesho for '{query}'...")
        base_url = "https://www.meesho.com"
        url = f"{base_url}/search?q={query}"
        html = direct_scrape(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("a[href*='/p/']"):
            title_tag = item.select_one("p.NewProductCard__ProductTitle_nowrap-one")
            price_tag = item.select_one("h5.Text__h5")
            image_tag = item.select_one("img")

            if title_tag and price_tag and image_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": price_tag.get_text(strip=True),
                    "link": urljoin(base_url, item['href']),
                    "image_url": image_tag.get('src')
                })
                if len(results) >= limit: break
        print(f"   - Meesho: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in meesho scraper: {e}")
        return []

def myntra(query, limit=5):
    try:
        print(f"-> Scraping Myntra for '{query}'...")
        base_url = "https://www.myntra.com"
        url = f"{base_url}/{query.replace(' ', '-')}"
        html = direct_scrape(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select("li.product-base"):
            title_tag = item.select_one(".product-product")
            price_container = item.select_one(".product-price")
            image_tag = item.select_one("picture.img-responsive img")
            link_tag = item.select_one("a")

            if title_tag and price_container and image_tag and link_tag:
                price_tag = price_container.select_one("span.product-discountedPrice") or price_container.select_one("span")
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": price_tag.get_text(strip=True),
                    "link": urljoin(base_url, link_tag['href']),
                    "image_url": image_tag.get('src')
                })
                if len(results) >= limit: break
        print(f"   - Myntra: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in myntra scraper: {e}")
        return []

def tatacliq(query, limit=5):
    try:
        print(f"-> Scraping TataCliq for '{query}'...")
        base_url = "https://www.tatacliq.com"
        url = f"{base_url}/search/?searchCategory=all&text={query}"
        html = direct_scrape(url)
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select(".ProductModule__base"):
            title_tag = item.select_one(".ProductDescription__name")
            price_tag = item.select_one(".ProductDescription__price-value")
            link_tag = item.select_one("a")
            image_tag = item.select_one("img.Image__actual-image")

            if title_tag and price_tag and link_tag and image_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": f"₹{price_tag.get_text(strip=True)}",
                    "link": urljoin(base_url, link_tag['href']),
                    "image_url": image_tag.get('src')
                })
                if len(results) >= limit: break
        print(f"   - TataCliq: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in tatacliq scraper: {e}")
        return []

def snapdeal(query, limit=5):
    try:
        print(f"-> Scraping Snapdeal for '{query}'...")
        base_url = "https://www.snapdeal.com"
        url = f"{base_url}/search?keyword={query}"
        html = direct_scrape(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select(".product-tuple-listing"):
            title_tag = item.select_one(".product-title")
            price_tag = item.select_one(".product-price")
            link_tag = item.select_one("a.dp-widget-link")
            image_tag = item.select_one(".product-tuple-image img")

            if title_tag and price_tag and link_tag and image_tag:
                image_src = image_tag.get('data-src') or image_tag.get('src')
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "price": price_tag.get_text(strip=True).replace("Rs. ", "₹"),
                    "link": link_tag['href'],
                    "image_url": image_src
                })
                if len(results) >= limit: break
        print(f"   - Snapdeal: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"   - ERROR in snapdeal scraper: {e}")
        return []


# from django.shortcuts import render
# from bs4 import BeautifulSoup
# import requests
# from base64 import b64decode
# import json
# import concurrent.futures # Import for concurrent scraping

# # --- Helper Functions with Error Handling ---

# def fetch_with_zyte(url):
#     """
#     Fetches content from a URL using the Zyte API with robust error handling.
#     Returns the HTML content as a string, or None if an error occurs.
#     """
#     # NOTE: It's highly recommended to move this key to your Django settings.py
#     # and load it using `from django.conf import settings`.
#     API_KEY = "31d677029a054280a79b6086ad61db26" 
    
#     try:
#         response = requests.post(
#             "https://api.zyte.com/v1/extract",
#             auth=(API_KEY, ""),
#             json={
#                 "url": url,
#                 "httpResponseBody": True,
#                 "browserHtml": True,
#             },
#             timeout=30 # Add a timeout to prevent hanging indefinitely
#         )
#         # Raise an exception for bad status codes (like 404, 500)
#         response.raise_for_status() 
        
#         # Safely parse the JSON response and decode the body
#         json_response = response.json()
#         http_body_b64 = json_response.get("httpResponseBody")
        
#         if not http_body_b64:
#             print(f"Zyte Error: 'httpResponseBody' not found in response for {url}")
#             return None
            
#         http_body = b64decode(http_body_b64)
#         return http_body.decode("utf-8", errors="ignore")

#     except requests.exceptions.RequestException as e:
#         print(f"Network Error fetching {url} with Zyte: {e}")
#         return None
#     except (json.JSONDecodeError, KeyError, TypeError) as e:
#         print(f"Error processing Zyte response for {url}: {e}")
#         return None


# def fetch_direct(url):
#     """
#     Fetches content directly with standard headers and error handling.
#     Returns the HTML content as a string, or None if an error occurs.
#     """
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Network Error fetching {url} directly: {e}")
#         return None

# # --- Scraping Functions (Now with Error Handling) ---

# def amazon(query):
#     html = fetch_with_zyte(f"https://www.amazon.in/s?k={query.replace(' ', '+')}")
#     if not html:
#         return [] # Return empty list if fetch failed
    
#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     for item in soup.select("div.s-result-item"):
#         try: # Add try/except for parsing each item
#             title_tag = item.select_one("h2 a span")
#             price_whole = item.select_one(".a-price-whole")
#             link_tag = item.select_one("h2 a")

#             if title_tag and price_whole and link_tag and link_tag.has_attr('href'):
#                 price = price_whole.get_text(strip=True)
#                 results.append({
#                     "title": title_tag.get_text(strip=True),
#                     "price": f"₹{price}",
#                     "link": "https://www.amazon.in" + link_tag['href']
#                 })
#         except Exception as e:
#             print(f"Error parsing an Amazon item: {e}")
#     return results


# def flipkart(query):
#     html = fetch_with_zyte(f"https://www.flipkart.com/search?q={query.replace(' ', '+')}")
#     if not html:
#         return []

#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     # Try multiple selectors as Flipkart's structure can vary
#     for item in soup.select("div._1AtVbE, div._4ddWXP"): 
#         try:
#             title_tag = item.select_one("div._4rR01T, a.s1Q9rs")
#             price_tag = item.select_one("div._30jeq3._1_WHN1, div._30jeq3")
#             link_tag = item.select_one("a._1fQZEK, a.s1Q9rs")

#             if title_tag and price_tag and link_tag and link_tag.has_attr('href'):
#                 results.append({
#                     "title": title_tag.get_text(strip=True),
#                     "price": price_tag.get_text(strip=True),
#                     "link": "https://www.flipkart.com" + link_tag['href']
#                 })
#         except Exception as e:
#             print(f"Error parsing a Flipkart item: {e}")
#     return results


# def meesho(query):
#     html = fetch_direct(f"https://www.meesho.com/search?q={query}")
#     if not html:
#         return []
        
#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     # This selector is fragile and likely to break.
#     for item in soup.select("div[class*='ProductList__GridCol']"):
#         try:
#             title = item.select_one("p")
#             price = item.select_one("h5")
#             if title and price:
#                 results.append({
#                     "title": title.get_text(strip=True),
#                     "price": price.get_text(strip=True),
#                     "link": "#" # Link not easily available
#                 })
#         except Exception as e:
#             print(f"Error parsing a Meesho item: {e}")
#     return results


# def myntra(query):
#     html = fetch_direct(f"https://www.myntra.com/{query}")
#     if not html:
#         return []

#     soup = BeautifulSoup(html, "html.parser")
#     results = []
#     for item in soup.select(".product-base"):
#         try:
#             brand = item.select_one(".product-brand")
#             product_name = item.select_one(".product-product")
#             price = item.select_one(".product-discountedPrice, .product-price")
#             link_tag = item.find("a", href=True)

#             if brand and product_name and price and link_tag:
#                 results.append({
#                     "title": f"{brand.get_text(strip=True)} - {product_name.get_text(strip=True)}",
#                     "price": price.get_text(strip=True),
#                     "link": "https://www.myntra.com/" + link_tag['href']
#                 })
#         except Exception as e:
#             print(f"Error parsing a Myntra item: {e}")
#     return results

# # ... (tatacliq and snapdeal functions would be updated similarly) ...
# # For brevity, I'm showing the pattern. Apply the same try/except and
# # fetch_direct logic to tatacliq and snapdeal.

# # --- Performance Improvement: Concurrent Scraping ---

# def get_home_products():
#     """
#     Scrapes all sites concurrently for a default query and returns the top 5 from each.
#     """
#     query = "laptop"
#     data = {}
    
#     # List of functions to run, along with their site names
#     scraper_tasks = {
#         "amazon": amazon,
#         "flipkart": flipkart,
#         "meesho": meesho,
#         "myntra": myntra,
#         # "tatacliq": tatacliq,
#         # "snapdeal": snapdeal,
#     }
    
#     # Using ThreadPoolExecutor to run network requests in parallel
#     with concurrent.futures.ThreadPoolExecutor(max_workers=len(scraper_tasks)) as executor:
#         # Create a future for each scraper function
#         future_to_site = {executor.submit(func, query): site for site, func in scraper_tasks.items()}
        
#         for future in concurrent.futures.as_completed(future_to_site):
#             site = future_to_site[future]
#             try:
#                 # Get the result and take the first 5 items
#                 result = future.result()
#                 data[site] = result[:5]
#                 print(f"Successfully scraped {len(result)} items from {site}.")
#             except Exception as exc:
#                 print(f"{site} scraper generated an exception: {exc}")
#                 data[site] = [] # Return empty list on failure

#     return data


# # --- Django Views ---

# def home(request):
#     products = get_home_products()
#     return render(request, 'home.html', {"products": products})

# def scrapedsites(request):
#     return render(request, 'scrapedsites.html')

# def contact(request):
#     return render(request, 'contact.html')

# # This view was empty. It must return an HttpResponse.
# # I'll have it render a simple template for now.
# def main(request):
#     return render(request, 'main.html')
