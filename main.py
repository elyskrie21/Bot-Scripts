import requests
import time
from urllib.parse import urljoin
from multiprocessing.pool import ThreadPool, Pool
from bs4 import BeautifulSoup
from selenium import webdriver
import threading
import os

class Driver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)

    def __del__(self):
        self.driver.quit() # clean up driver when we are cleaned up
        print('The driver has been "quitted".')

def get_links(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.text,"lxml")
    titles = [urljoin(url,items.get("href")) for items in soup.find_all("a", {"class": "item-title"})]
    return titles

def get_driver():
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        driver = Driver()
        setattr(threadLocal, 'driver', driver)
    return driver.driver

def get_stock_and_price(url):
    driver = get_driver()
    driver.get(url)
    sauce = BeautifulSoup(driver.page_source,"lxml")
    if sauce.select_one(".product-title"):
        itemName = sauce.select_one(".product-title").text
        price = sauce.select_one(".price-current").text
        image = sauce.select_one(".product-view-img-original")['src']
        if sauce.select_one(".btn-primary"):
            itemStock = "IN STOCK"
        else:
            itemStock = "OUT OF STOCK" 
    else:
        itemName = sauce.select_one("h1").text
        price = sauce.select_one(".current").text.replace('\n', '').strip('Now:  ')
        image = sauce.select_one(".checkedimg")['src']
        if sauce.select_one(".atnPrimary").text == "ADD TO CART":
            itemStock = "IN STOCK"
        else:
            itemStock = "OUT OF STOCK"
    itemData = {"name": itemName, "price": price, "stock": itemStock, "link": url, "image": image}
    requests.post("https://warm-ridge-24483.herokuapp.com/product", data=itemData)
    print(f'{itemName}, Stock: {itemStock}, Price: {price}, Link: {url}, Image: {image}\n')

if __name__ == '__main__':
    while True:
        threadLocal = threading.local()
        url = "https://www.newegg.com/p/pl?d=3060+ti"
        ThreadPool(2).map(get_stock_and_price,get_links(url))
        
        del threadLocal
        import gc
        gc.collect() # a little extra insurance
        time.sleep(10)

