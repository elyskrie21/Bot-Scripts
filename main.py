import requests
from urllib.parse import urljoin
from multiprocessing.pool import ThreadPool, Pool
from bs4 import BeautifulSoup
from selenium import webdriver
import threading

class Driver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(r"./chromedriver.exe",options=options)

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

threadLocal = threading.local()

def get_stock_and_price(url):
    driver = get_driver()
    driver.get(url)
    sauce = BeautifulSoup(driver.page_source,"lxml")
    if sauce.select_one(".product-title"):
        itemName = sauce.select_one(".product-title").text
        price = sauce.select_one(".price-current").text
        if sauce.select_one(".btn-primary"):
            itemStock = "IN STOCK"
        else:
            itemStock = "OUT OF STOCK" 
    else:
        itemName = sauce.select_one("h1").text
        price = sauce.select_one(".current").text.replace('\n', '').strip('Now:  ')
        if sauce.select_one(".atnPrimary").text == "ADD TO CART":
            itemStock = "IN STOCK"
        else:
            itemStock = "OUT OF STOCK"
    itemData = {"Name": itemName, "Price": price, "Stock": itemStock}
    requests.post("http://192.168.254.65:5000/", data=itemData)
    print(f'{itemName}, Stock: {itemStock}, Price: {price}, Link: {url}\n')

if __name__ == '__main__':
    url = "https://www.newegg.com/p/pl?d=3060+ti"
    ThreadPool(4).map(get_stock_and_price,get_links(url))
    
    del threadLocal
    import gc
    gc.collect() # a little extra insurance

