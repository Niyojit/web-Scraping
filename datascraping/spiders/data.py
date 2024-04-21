import scrapy
from pathlib import Path
from pymongo import MongoClient
import datetime
from urllib.parse import quote_plus

class DataSpider(scrapy.Spider):
    name = "data"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # Escape the username and password
    username = "niyo"
    password = "0502@Niyo"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    # Use the escaped username and password in the connection string
    client = MongoClient(f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.2dmddfh.mongodb.net/")
    db = client.Scrapy

    def insertToDb(self, page, title, rating, image, price, inStock):
        collection = self.db[page]  # Define collection here
        doc = {
            "title": title,
            "rating": rating,
            "image": image,
            "price": price,
            "inStock": inStock,
            "date": datetime.datetime.now(tz=datetime.timezone.utc),
        }
        inserted = collection.insert_one(doc)
        return inserted.inserted_id
  
    def start_requests(self):
        urls = [
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
            "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
            "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
            "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"data-{page}.html"
        # Path(filename).write_bytes(response.body)
        self.log(f"saved file {filename}")
        cards = response.css(".product_pod")
        for card in cards:

            title = card.css("h3 > a::text").get()
            print(title)

            rating = card.css(".star-rating").attrib["class"].split(" ")[1]
            print(rating)

            image = card.css(".image_container img").attrib["src"]
            print(image)
        
            price = card.css(".price_color::text").get()
            print(price)

            availability = card.css(".availability")
            if len(availability.css(".icon-ok")) > 0:
                instock = True
            else:
                instock = False

            # Call insertToDb function
            self.insertToDb(page, title, rating, image, price, instock)
