from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from base64 import b64decode, urlsafe_b64encode, urlsafe_b64decode
from urllib.parse import urljoin
import os
import json

# IMPORTANT: Replace "YOUR_API_KEY" with your actual Zyte API key.
ZYTE_API_KEY = "31d677029a054280a79b6086ad61db26"

def scrape_amazon_search(api_key, url):
    """
    Scrapes an Amazon search results page.
    """
    if api_key == "YOUR_API_KEY" or not api_key:
        print("❌ Error: Please replace 'YOUR_API_KEY' with your actual Zyte API key.")
        return None

    print(f"▶️  Sending request to Zyte API for URL: {url}")

    try:
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json={"url": url, "httpResponseBody": True},
            timeout=90
        )
        response.raise_for_status()
        api_response_json = response.json()
        html_body_bytes = b64decode(api_response_json["httpResponseBody"])
        soup = BeautifulSoup(html_body_bytes, 'html.parser')
        
        products = []
        result_items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        if not result_items:
            print("⚠️ No product items found on search page.")
            return []

        for item in result_items:
            title_element = item.find('h2')
            title = title_element.get_text(strip=True) if title_element else None

            price = None
            price_whole = item.find('span', class_='a-price-whole')
            price_fraction = item.find('span', class_='a-price-fraction')
            if price_whole and price_fraction:
                price = f"${price_whole.text}{price_fraction.text}"
            else:
                price_offscreen = item.find('span', class_='a-offscreen')
                if price_offscreen:
                    price = price_offscreen.get_text(strip=True)

            url_element = item.find('a', class_='a-link-normal')
            product_url = "https://www.amazon.com" + url_element['href'] if url_element else None
            
            image_element = item.find('img', class_='s-image')
            image_url = image_element['src'] if image_element else None

            if title and product_url and "spons" not in product_url:
                encoded_url = urlsafe_b64encode(product_url.encode()).decode()
                products.append({
                    'title': title,
                    'price': price,
                    'url': product_url,
                    'image_url': image_url,
                    'encoded_url': encoded_url
                })
        
        return products

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the API request: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during search parsing: {e}")
        return None

def scrape_product_details(api_key, product_url):
    """
    Scrapes a single product detail page for detailed information.
    """
    if api_key == "YOUR_API_KEY" or not api_key:
        return None
    
    print(f"▶️  Scraping detail page: {product_url}")
    try:
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json={"url": product_url, "httpResponseBody": True},
            timeout=90
        )
        response.raise_for_status()
        api_response_json = response.json()
        html_body_bytes = b64decode(api_response_json["httpResponseBody"])
        soup = BeautifulSoup(html_body_bytes, 'html.parser')

        title = soup.find('span', id='productTitle').get_text(strip=True) if soup.find('span', id='productTitle') else "Not available"
        
        rating_element = soup.find('span', class_='a-icon-alt')
        rating = rating_element.get_text(strip=True) if rating_element else "No rating"
        
        reviews_element = soup.find('span', id='acrCustomerReviewText')
        reviews_count = reviews_element.get_text(strip=True) if reviews_element else "0 reviews"

        price = None
        price_element = soup.select_one('span.a-price .a-offscreen')
        if price_element:
            price = price_element.get_text(strip=True)

    
        
        about_points = []
        selector = "span.a-list-item.a-size-base.a-color-base"
        
        # Directly select all matching elements from the entire soup object
        about_elements = soup.select(selector)
        
        for element in about_elements:
            # Clean up the text, as it can sometimes have hidden characters or extra spaces
            text = ' '.join(element.get_text(strip=True).split())
            if text: # Ensure we don't add empty strings
                about_points.append(text)
        # --- END OF DIRECT LOGIC ---

        specifications = {}
        tech_spec_table = soup.find('table', id='productDetails_techSpec_section_1')
        if tech_spec_table:
            for row in tech_spec_table.find_all('tr'):
                th = row.find('th').get_text(strip=True) if row.find('th') else ''
                td = row.find('td').get_text(strip=True) if row.find('td') else ''
                if th and td:
                    specifications[th] = td
        
        image_element = soup.find('img', id='landingImage')
        image_url = image_element['src'] if image_element else ''

        return {
            'title': title,
            'rating': rating,
            'reviews_count': reviews_count,
            'price': price,
            'about_points': about_points,
            'specifications': specifications,
            'image_url': image_url,
            'amazon_url': product_url
        }

    except Exception as e:
        print(f"❌ An unexpected error occurred during detail parsing: {e}")
        return None

def scraping(req):
    """
    Handles the home page and search requests.
    """
    product_query = req.GET.get('q', None)
    context = {}

    if product_query:
        print(f"▶️  Searching for: {product_query}")
        amazon_url = f"https://www.amazon.com/s?k={product_query}"
        scraped_products = scrape_amazon_search(ZYTE_API_KEY, amazon_url)
        context = {
            'scraped_product': scraped_products if scraped_products is not None else [],
            'query': product_query
        }
    else:
        print("▶️  Displaying home page with categorized products.")
        categories = ['laptops', 'mobiles', 'shirts', 'electronics']
        categorized_products = {}
        for category in categories:
            amazon_url = f"https://www.amazon.com/s?k={category}"
            products = scrape_amazon_search(ZYTE_API_KEY, amazon_url)
            if products:
                categorized_products[category.title()] = products[:6]
            else:
                categorized_products[category.title()] = []
        context = {
            'categorized_products': categorized_products,
            'query': None
        }
    
    return render(req, 'home.html', context)

def product_detail(req, encoded_url):
    """
    Handles displaying the details for a single product.
    """
    try:
        decoded_url = urlsafe_b64decode(encoded_url).decode()
    except:
        return render(req, 'product_detail.html', {'error': 'Invalid product URL.'})
    
    product_details = scrape_product_details(ZYTE_API_KEY, decoded_url)

    context = {
        'product': product_details
    }
    return render(req, 'product_detail.html', context)
