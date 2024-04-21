import scrapy
from pymongo import MongoClient
import datetime
from urllib.parse import quote_plus

class DataSpider(scrapy.Spider):
    name = "data"
    allowed_domains = ["toscrape.com", "nseindia.com"]
    start_urls = [
        "https://books.toscrape.com/",
        "https://www.nseindia.com/"
    ]

    # Escape the username and password
    username = "niyo"
    password = "0502@Niyo"
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    # Use the escaped username and password in the connection string
    client = MongoClient(f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.2dmddfh.mongodb.net/")
    db = client.data  # Use "data" database

    def insertToDb(self, collection_name, data):
        collection = self.db[collection_name]
        inserted = collection.insert_one(data)
        return inserted.inserted_id

    def start_requests(self):
        urls = [
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
            "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
            "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
            "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
            "https://www.nseindia.com/resources/exchange-communication-media-center",
            "https://www.nseindia.com/market-data/securities-available-for-trading",
            "https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives",
            "https://www.nseindia.com/complaints/complaints-public-notice",
            "https://www.nseindia.com/research/events-conferences"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]

        if "toscrape" in response.url:
            cards = response.css(".product_pod")
            for card in cards:
                title = card.css("h3 > a::text").get()
                rating = card.css(".star-rating").attrib["class"].split(" ")[1]
                image = card.css(".image_container img").attrib["src"]
                price = card.css(".price_color::text").get()
                availability = response.css(".availability")
                instock = len(availability.css(".icon-ok")) > 0

                # Prepare data to insert
                data = {
                    "title": title,
                    "rating": rating,
                    "image": image,
                    "price": price,
                    "inStock": instock,
                    "date_scraped": datetime.datetime.now(tz=datetime.timezone.utc),
                }
                # Insert data into MongoDB
                self.insertToDb(page, data)

        elif "nseindia" in response.url:
            # Extracting heading
            heading = response.css("p.tab_box.up::text").get()
            heading2 = response.css(".card-header h4::text").get()
            # Extracting amount 1
            amount1 = response.css("p.tb_name::text").get()

            # Extracting amount 2
            amount2 = response.css("p.tb_per.greenTxt::text").get()
            date = response.css(".card-header h4::text").re_first(r'(\d+-\w+-\d+)')
            # Extracting PDF link
            pdf_link = response.css("a[aria-label='Download File']::attr(href)").get()
            # Extracting image link
            image_link = response.css(".media-img img::attr(src)").get()
            # Prepare data to insert
            data = {
                "heading": heading,
                "heading2": heading2,
                "date": date,
                "pdf_link": pdf_link,
                "image_link": image_link,
                "amount1": amount1,
                "amount2": amount2,
                "date_scraped": datetime.datetime.now(tz=datetime.timezone.utc),
            }
            # Insert data into MongoDB
            self.insertToDb(page, data)
