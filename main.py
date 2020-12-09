import requests
from requests.structures import CaseInsensitiveDict
import time
from urllib.parse import urljoin
from multiprocessing import Pool
from bs4 import BeautifulSoup
from selenium import webdriver
import threading
import os

options = webdriver.ChromeOptions()
#options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

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
    print('this is the soup', soup)
    titles = [urljoin(url,items.get("href")) for items in soup.find_all("a", {"class": "item-title"})]

    if len(titles) != 0:
      break
  
  return titles

def get_stock_and_price(url):
    driver.get(url)
    sauce = BeautifulSoup(driver.page_source,"lxml")
    try:
<<<<<<< HEAD
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
    except AttributeError:
        print('product not found') 
    itemData = {"name": itemName, "price": int(price), "stock": itemStock, "link": url, "image": image}
    requests.post("https://warm-ridge-24483.herokuapp.com/product", data=itemData)
=======
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
          itemName = sauce.select_one("h1").text
          price = sauce.select_one(".current").text.replace('\n', '').strip('Now:  ')
          #image = sauce.select_one(".checkedimg")['src']
          if sauce.select_one(".atnPrimary").text == "ADD TO CART":
              itemStock = "IN STOCK"
          else:
              itemStock = "OUT OF STOCK"
    except (AttributeError, TypeError) as e:
      print("Item url: ", url)
      print("Element could not be found: ", e)
      return ""
    
    itemData = {"name": itemName, "price": price, "stock": itemStock, "link": url, "image": image}
>>>>>>> 5cec666bbe938583ab822888da15fc2d82cacc2a
    print(f'{itemName}, Stock: {itemStock}, Price: {price}, Link: {url}, Image: {image}\n')

    return itemData

if __name__ == '__main__':
    url = "https://www.newegg.com/p/pl?d=3060+ti"
    links = get_links(url)
    productData = []

    for link in links:
      item = get_stock_and_price(link)
      if type(item) is dict:
        productData = []
        print("One item appended")
    
    with Pool(5) as p:
      p.map(post_product, productData)
    



