import scrapy
import re
import json
import os
from ..mapping import classify_product
from spider20.items import SpiderItem

# from spider20.spider20.items import SpiderItem 


class CloudSpider(scrapy.Spider):
    name = "cloud"

    custom_settings = {
        "ITEM_PIPELINES": {
            "spider20.pipelines.SpiderPipeline": 300,
        },
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "DOWNLOAD_DELAY": 0.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
                }
    item = SpiderItem()
    def start_requests(self):


        spider_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(spider_dir, '..', 'configs', 'cloudConfig.json')
    
        # Normalized path to make it clean
        config_path = os.path.normpath(config_path)

        with open(config_path) as f:
            self.config = json.load(f)

        # Iterate through the gender keys: "women", "men", "kids"
        for gender, info in self.config.items():
            urls = info.get("urls", [])
            for url in urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    # We no longer pass "category_name" here because 
                    # we will infer it from the product title in parse_product
                    cb_kwargs={
                        "gender": gender
                    }
                )

        
        
        


    def parse(self, response, gender):
        products = response.css(".product-card")
        for product in products:
            
            link = response.urljoin(product.css("a::attr(href)").get())
            yield scrapy.Request(
                url = link,
                callback = self.parse_product,
                cb_kwargs={
                    "gender": gender
                }
                )
        next_page = response.css(".pagination__item--prev ::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url = response.urljoin(next_page), 
                callback=self.parse,
                cb_kwargs={
                    # "category_name": category_name,
                    "gender": gender
                })
            

    
    def parse_product(self,response, gender):
        salePrice = 0

        
        # salePrice = re.sub(r"[^\d.]", "", response.css("sale-price ::text").getall().strip()) 
        # print("SaLE:", salePrice)
        # if float(salePrice) == 0: 
        #     salePrice = 0
        #     print("NO SALE")
        # else:
        #     print("SALE")
        #     print(salePrice)
        #     salePrice = re.sub(r"[^\d.]", "", response.css("sale-price ::text").getall()[-1].strip()) 

        #TODO When there's a sale add the logic

        item = SpiderItem()


        item["imageLink"]= "https:" + response.css(".product-gallery__media img::attr(src)").get()
        item["name"] = response.css(".product-info__title::text").get().strip()
        item["price"] = re.sub(r"[^\d.]", "", response.css("sale-price ::text").getall()[2].strip()) 
        item["salePrice"] = salePrice
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = classify_product(item["name"])
        item["storeId"] = 1004
        item['colors'] = response.css('.color-swatch span::text').getall()

        yield item
