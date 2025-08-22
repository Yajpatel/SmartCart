
# scraper/views.py

from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from base64 import b64decode, urlsafe_b64encode, urlsafe_b64decode

# IMPORTANT: Replace with your actual Zyte API key for Amazon scraping
ZYTE_API_KEY = "31d677029a054280a79b6086ad61db26"

# ===========================
# Helper Fetch Functions
# ===========================

def fetch_url_zyte(url):
    """Fetches URL content using Zyte API for JavaScript-heavy sites (Amazon)."""
    if ZYTE_API_KEY == "YOUR_API_KEY" or not ZYTE_API_KEY:
        print("❌ Error: Please provide a valid Zyte API key to scrape Amazon.")
        return None
    try:
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(ZYTE_API_KEY, ""),
            json={"url": url, "httpResponseBody": True},
            timeout=90
        )
        response.raise_for_status()
        return b64decode(response.json()["httpResponseBody"])
    except requests.exceptions.RequestException as e:
        print(f"❌ Zyte API request error for {url}: {e}")
        return None


def fetch_url_direct(url):
    """Fetches URL content using direct request."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"❌ Direct request error for {url}: {e}")
        return None


# ===========================
# Amazon Scraper (No Changes)
# ===========================

def scrape_amazon_search(query):
    print(f"▶️  Scraping Amazon for: {query}")
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    html_content = fetch_url_zyte(url)
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        title = item.find('h2').get_text(strip=True) if item.find('h2') else None
        price = item.find('span', class_='a-offscreen').get_text(strip=True) if item.find('span', class_='a-offscreen') else None
        product_url = "https://www.amazon.in" + item.find('a', class_='a-link-normal')['href'] if item.find('a', class_='a-link-normal') else None
        image_url = item.find('img', class_='s-image')['src'] if item.find('img', class_='s-image') else None
        if title and product_url and "spons" not in product_url:
            products.append({
                'title': title,
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'encoded_url': urlsafe_b64encode(product_url.encode()).decode(),
                'source': 'Amazon'
            })
    return products


def scrape_amazon_details(product_url):
    html_content = fetch_url_zyte(product_url)
    if not html_content: return None
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('span', id='productTitle').get_text(strip=True) if soup.find('span', id='productTitle') else "N/A"
    price = soup.select_one('span.a-price .a-offscreen').get_text(strip=True) if soup.select_one('span.a-price .a-offscreen') else None
    image = soup.find('img', id='landingImage')['src'] if soup.find('img', id='landingImage') else ''
    about_points = [li.get_text(strip=True) for li in soup.select("#feature-bullets .a-list-item")]
    return {'title': title, 'price': price, 'image_url': image, 'about_points': about_points, 'source_url': product_url, 'source': 'Amazon'}


# ===========================
# Snapdeal Scraper (No Changes)
# ===========================

def scrape_snapdeal_search(query):
    print(f"▶️  Scraping Snapdeal for: {query}")
    url = f"https://www.snapdeal.com/search?keyword={query.replace(' ', '+')}"
    html_content = fetch_url_direct(url)
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for item in soup.find_all('div', class_='product-tuple-listing'):
        title = item.find('p', class_='product-title').get('title', 'N/A').strip()
        price = item.find('span', class_='lfloat product-price').text.strip() if item.find('span', class_='lfloat product-price') else None
        product_url = item.find('a', class_='dp-widget-link')['href'] if item.find('a', class_='dp-widget-link') else None
        image_tag = item.find('img', class_='product-image')
        image_url = image_tag.get('src') or image_tag.get('data-src') if image_tag else None
        if title and product_url:
            products.append({
                'title': title,
                'price': f"Rs. {price}" if price else "N/A",
                'url': product_url,
                'image_url': image_url,
                'encoded_url': urlsafe_b64encode(product_url.encode()).decode(),
                'source': 'Snapdeal'
            })
    return products


def scrape_snapdeal_details(product_url):
    html_content = fetch_url_direct(product_url)
    if not html_content: return None
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('h1', class_='pdp-e-i-head').get_text(strip=True) if soup.find('h1', class_='pdp-e-i-head') else "N/A"
    price = soup.find('span', class_='payBlkBig').get_text(strip=True) if soup.find('span', class_='payBlkBig') else None
    image = soup.find('img', class_='cloudzoom')['src'] if soup.find('img', class_='cloudzoom') else ''
    about_points = [li.get_text(strip=True) for li in soup.select("div.detailssubbox ul li")]
    return {'title': title, 'price': f"Rs. {price}" if price else "N/A", 'image_url': image, 'about_points': about_points, 'source_url': product_url, 'source': 'Snapdeal'}



# ===========================
# Flipkart Scraper (NEW)
# ===========================

def scrape_flipkart_search(query):
    """
    Scrapes search results from Flipkart for a given query.
    """
    print(f"▶️  Scraping Flipkart for: {query}")
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    
    # IMPORTANT: Flipkart often blocks simple requests. 
    # Using fetch_url_direct may not work consistently. 
    # Consider using fetch_url_zyte for better results.
    html_content = fetch_url_direct(url)
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    # Flipkart has multiple layouts, so we check for common container classes
    # Layout 1: ._1AtVbE, Layout 2: ._4ddWXP, Layout 3: .cPHDOP
    for item in soup.find_all('div', {'class': ['_1xHGtK', '_373qXS', '_4ddWXP', 'cPHDOP',"_1sdMkc LFEi7Z",'tUxRFH']}):
        # Try finding title in different possible tags
        title_tag = item.find('a', class_=['wjcEIp','WKTcLC']) or item.find("div",class_='KzDlHZ')
        title = title_tag.get_text(strip=True) if title_tag else None

        # Price is usually consistent
        price_tag = item.find('div', class_=['Nx9bqj','Nx9bqj _4b5DiR'])
        price = price_tag.get_text(strip=True) if price_tag else None
        
        # Find the main link to the product
        link_tag = item.find('a', class_=['VJA3rP','rPDeLR','CGtC98']) or item.find('a', class_='s1Q9rs') or item.find('a', class_='_2UzuFa')
        product_url = "https://www.flipkart.com" + link_tag['href'] if link_tag else None
        
        # Image is often lazy-loaded
        image_tag = item.find('img', class_=['DByuf4','_53J4C-'])
        image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None
        print(title,product_url,"price = ",price)
        if title and product_url and price:
            products.append({
                'title': title,
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'encoded_url': urlsafe_b64encode(product_url.encode()).decode(),
                'source': 'Flipkart'
            })
            print("products = ",products)
            
    return products

def scrape_flipkart_details(product_url):
    """
    Scrapes the details of a single product from its Flipkart URL.
    """
    html_content = fetch_url_direct(product_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Selectors based on your successful standalone script and common layouts
    title = soup.find('span', class_='B_NuCI').get_text(strip=True) if soup.find('span', class_='B_NuCI') else "N/A"
    price = soup.find('div', class_='_30jeq3 _16Jk6d').get_text(strip=True) if soup.find('div', class_='_30jeq3 _16Jk6d') else None
    
    # The main image can be in a few different containers
    image_container = soup.find('div', class_='_2r_T1I _396cs4') or soup.find('img', class_='_2r_T1I _396cs4')
    image = image_container['src'] if image_container else ''
    
    # "Highlights" section serves as the about points
    about_points = [li.get_text(strip=True) for li in soup.select("div._2418kt ul li._21Ahn-")]
    
    return {
        'title': title, 
        'price': price, 
        'image_url': image, 
        'about_points': about_points, 
        'source_url': product_url, 
        'source': 'Flipkart'
    }


# ===========================
# Django Views (No Changes)
# ===========================

def scraping(req):
    """Handles search and homepage requests."""
    product_query = req.GET.get('q', '').strip()
    source = req.GET.get('source', 'amazon').strip().lower()

    context = {
        'query': product_query,
        'source': source,
        'scraped_products': []
    }

    if product_query:
        print(f"▶️  Searching on '{source}' for: {product_query}")
        if source == 'snapdeal':
            context['scraped_products'] = scrape_snapdeal_search(product_query)
        elif source == 'meesho':
            context['scraped_products'] = scrape_meesho_search(product_query)
        elif source == 'myntra':
            context['scraped_products'] = scrape_myntra_search(product_query)
        elif source == 'tatacliq':
            context['scraped_products'] = scrape_tatacliq_search(product_query)
        elif source == 'croma':
            context['scraped_products'] = scrape_croma_search(product_query)
        elif source == 'flipkart':
            context['scraped_products'] = scrape_flipkart_search(product_query)
        else:  # default Amazon
            context['scraped_products'] = scrape_amazon_search(product_query)
    else:
        # Homepage default
        print("▶️  Displaying categorized products from Amazon.")
        categorized_products = {}
        categories = ['laptops', 'mobiles', 'shirts']
        for category in categories:
            products = scrape_amazon_search(category)
            categorized_products[category.title()] = products[:8]
        context['categorized_products'] = categorized_products

    return render(req, 'home.html', context)


def product_detail(req, encoded_url):
    """Handles single product details."""
    try:
        decoded_url = urlsafe_b64decode(encoded_url).decode()
    except Exception:
        return render(req, 'product_detail.html', {'error': 'Invalid product URL.'})

    product = None
    if 'amazon' in decoded_url: # A bit more robust
        product = scrape_amazon_details(decoded_url)
    elif 'snapdeal.com' in decoded_url:
        product = scrape_snapdeal_details(decoded_url)
    elif 'meesho.com' in decoded_url:
        product = scrape_meesho_details(decoded_url)
    elif 'myntra.com' in decoded_url:
        product = scrape_myntra_details(decoded_url)
    elif 'tatacliq.com' in decoded_url:
        product = scrape_tatacliq_details(decoded_url)
    elif 'flipkart.com' in decoded_url:
        product = scrape_flipkart_details(decoded_url)
    elif 'croma.com' in decoded_url:
        product = scrape_croma_details(decoded_url)

    return render(req, 'product_detail.html', {'product': product})


def contact(req):
    """Render contact page and handle basic POST for now."""
    submitted = False
    if req.method == 'POST':
        # For now, just echo success; in real app, send email or store message
        submitted = True
    return render(req, 'contact.html', {'submitted': submitted})
