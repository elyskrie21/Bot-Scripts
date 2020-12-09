import requests
from requests.structures import CaseInsensitiveDict
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

options = webdriver.ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

def post_product(data):
  url = "https://warm-ridge-24483.herokuapp.com/product"

  headers = CaseInsensitiveDict()
  headers["Content-Type"] = "application/json"

  data = data
  resp = requests.post(url, headers=headers, json=data)

  print(resp.status_code)

def get_links(link):
  while True: 
    res = requests.get(link)
    soup = BeautifulSoup(res.text,"lxml")
    titles = [urljoin(url,items.get("href")) for items in soup.find_all("a", {"class": "item-title"})]

    if len(titles) != 0:
      break
  
  return titles

def get_stock_and_price(url):
    driver.get(url)
    sauce = BeautifulSoup(driver.page_source,"lxml")
    try:
      if sauce.select_one(".product-title") != None:
          print("I am not a combo")
          itemName = sauce.select_one(".product-title").text
          price = sauce.select_one(".price-current").text
          image = sauce.select_one(".product-view-img-original")['src']
          if sauce.select_one(".btn-primary"):
              itemStock = "IN STOCK"
          else:
              itemStock = "OUT OF STOCK" 
      else:
          print("I am a combo")
          itemName = sauce.select_one("h1").text
          price = sauce.select_one(".current").text.replace('\n', '').strip('Now:  ')
          image = sauce.select_one("#mainSlide_0")['src']
          if sauce.select_one(".atnPrimary").text == "ADD TO CART":
              itemStock = "IN STOCK"
          else:
              itemStock = "OUT OF STOCK"
    except (AttributeError, TypeError) as e:
      print("Failed item url: ", url)
      print("Element could not be found: ", e)
      return ""
    
    itemData = {"name": itemName, "price": price, "stock": itemStock, "link": url, "image": image}
    print(f'{itemName}, Stock: {itemStock}, Price: {price}, Link: {url}, Image: {image}\n')

    return itemData


@sched.scheduled_job('interval', minutes=3)
def timed_job:
    url = "https://www.newegg.com/p/pl?d=3060+ti"
    links = get_links(url)
    productData = []

    for link in links:
      item = get_stock_and_price(link)
      if type(item) is dict:
        post_product(item)
        
sched.start()
  
    
