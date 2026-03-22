import scrapy
import re
import json
import os
import scrapy_zyte_api
from spider20.items import SpiderItem
from scrapy_playwright.page import PageMethod
from urllib.parse import urlparse, urlunparse

class LCSpider(scrapy.Spider):
    name = "lc"

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "spider20.pipelines.SpiderPipeline": 300,
    #     },
    #     "CONCURRENT_REQUESTS": 4,
    #     "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    #     "DOWNLOAD_DELAY": 0.5, 
    #     "RANDOMIZE_DOWNLOAD_DELAY": True,
    #     "DEFAULT_REQUEST_HEADERS": {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    #             "Accept-Language": "en-US,en;q=0.9",
    #         },
    #     "ADDONS": {
    #         scrapy_zyte_api.Addon: 500,
    #     }
    #             }
        

    def start_requests(self):

        spider_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(spider_dir, '..', 'configs', 'lcConfig.json')
    
        # Normalized path to make it clean
        config_path = os.path.normpath(config_path)


        

        print("PIPELINES:", self.settings.get("ITEM_PIPELINES"))
        with open(config_path) as f:
            self.config=json.load(f)

        for category, info in self.config.items():
            for url in info["urls"]:
                yield scrapy.Request(
                    url=url["url"],
                    callback=self.parse,
                    cb_kwargs={"category_name": category,
                               "gender": url["gender"] }
                )

    def parse(self, response, category_name, gender, nextPage=2):
        print("Visiting: ", response.url)
        products = response.css(".product-card")
        for product in products:
            link = response.urljoin(product.css("a::attr(href)").get())

            if(product.css(".product-price__badge").get() is not None):
                yield scrapy.Request(
                url=link,
                callback=self.parse_product,
                cb_kwargs={"category_name": category_name,"gender":gender, "salePrice": product.css(".price-in-cart::text").get()},
            )
            else:
                yield scrapy.Request(
                url=link,
                callback=self.parse_product,
                cb_kwargs={"category_name": category_name,"gender":gender, "salePrice":"0"},
            )

        # pagination logic…

        parsed = urlparse(response.url)
        base_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

        next_url = f"{base_url}?page={nextPage}"
        if response.css(".load-more__button"):
            nextPage += 1
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                cb_kwargs={"category_name": category_name, "gender": gender, "nextPage": nextPage}
            )

    def parse_product(self, response, category_name, gender, salePrice):

        print("Parsing product")
        salePrice = re.sub(r"[^\d.]", "", salePrice)

        script = response.xpath('//script[contains(text(), "GA4ViewItemEvent")]/text()').get()
        json_str = re.search(r'JSON\.parse\("(.*?)"\)', script).group(1)
        data = json.loads(json_str.replace('\\"', '"'))
        item_details = data['ecommerce']['items'][0]
        name = item_details.get('item_name')

        item = SpiderItem()
        item["imageLink"] = response.css(".main-image::attr(src)").get()
        item["name"] = name
        item["price"] = re.sub(r"[^\d.]", "", response.css(".current-price::text").get())
        item["salePrice"] = salePrice
        item["productLink"] = response.url
        item["gender"] = gender 
        item["type"] = category_name
        item["storeId"] = 1001
        item["colors"] = response.css(".product-detail-colors__option-image::attr(alt)").getall() 

        yield item
