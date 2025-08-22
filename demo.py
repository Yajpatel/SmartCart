import time
import random
import undetected_chromedriver as uc
uc.Chrome._del_ = lambda self: None
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

PRICE_SELECTORS = [
    "div.Nx9bqj.CxhGGd",
    "div.Nx9bqj.CxhGGd.yKS4la",
    # "div._30jeq3._16Jk6d",           
    # "div._25b18c ._30jeq3._16Jk6d",  
]

TITLE_SELECTORS = [
    ".VU-ZEz",
    # "span.B_NuCI",                   
    # "h1.yhB1nd",                    
    # "._6EBuvT",
]

def scrape_flipkart_price(url, driver):
    print(f"\nScraping Flipkart URL: {url}")

    driver.get(url)
    time.sleep(2 + random.random() * 2)
    time.sleep(3)

    title = ""
    for sel in TITLE_SELECTORS:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            title = el.text
            print(f"Title found with selector: {sel} --> {title}")
            if title:
                break
        except NoSuchElementException:
            print(f"Title selector failed: {sel}")
            continue

    price = None
    for sel in PRICE_SELECTORS:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            price_text = el.text.replace("₹", "").replace(",", "").strip()
            if price_text:
                price = float(price_text)
                print(f"Price found with selector: {sel} --> {price}")
                break
        except NoSuchElementException:
            print(f"Price selector failed: {sel}")
            continue
        except ValueError:
            print(f"Failed to convert price text: {el.text}")

    if not title:
        print("Title not found")
    if not price:
        print("Price not found")

    return price, title

def scrape_multiple_urls(urls):
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.5845.179 Safari/537.36"
    )

    results = []
    driver = uc.Chrome(options=options)

    try:
        for url in urls:
            price, title = scrape_flipkart_price(url, driver)
            results.append({"url": url, "title": title, "price": price})
            time.sleep(random.uniform(2, 5))  # random delay between requests
    finally:
        driver.quit()
        del driver   # ensures GC doesn’t try to clean up again

    return results

if __name__ == "__main__":
    urls = [
        "https://www.flipkart.com/motorola-edge-60-fusion-5g-pantone-mykonos-blue-256-gb/p/itmdbb95e3f12ab6?pid=MOBH9ARFZXNHC7VZ&lid=LSTMOBH9ARFZXNHC7VZD9IAPG&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_1&otracker=clp_bannerads_1_8.bannerAdCard.BANNERADS_Motorola%2BEdge%2B60%2BFusion%2B5G_mobile-phones-store_9LO76G8QXECO&fm=organic&iid=229ede28-889e-4e2d-8319-894ac647c873.MOBH9ARFZXNHC7VZ.SEARCH&ppt=clp&ppn=mobile-phones-store&ssid=pcnagr1gfk0000001755764680593",
        "https://www.flipkart.com/realme-p3-5g-space-silver-128-gb/p/itm69060f73d27e8?pid=MOBHAYN5ZXFQ3GFG&lid=LSTMOBHAYN5ZXFQ3GFGFUCV7J&marketplace=FLIPKART&store=tyy%2F4io&spotlightTagId=default_BestsellerId_tyy%2F4io&srno=b_1_1&otracker=CLP_BannerX3&fm=organic&iid=0a238da7-1ecf-4f90-85e4-fec27b07be4e.MOBHAYN5ZXFQ3GFG.SEARCH&ppt=browse&ppn=browse&ssid=g5knisouwg0000001755765660540",
    ]

    scraped_data = scrape_multiple_urls(urls)
    print("\nFinal Results:")
    for item in scraped_data:
        print(item)