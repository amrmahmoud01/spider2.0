import scrapy
import re
import json
import os
from ..mapping import classify_product
from spider20.items import SpiderItem

# from spider20.spider20.items import SpiderItem 


class ComfowearSpider(scrapy.Spider):
    name = "comfowear"

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

        config_path = os.path.join(spider_dir, '..', 'configs', 'comfowearConfig.json')
    
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
        products = response.css(".card-wrapper")
        for product in products:
            
            link = response.urljoin(product.css("a::attr(href)").get())
            yield scrapy.Request(
                url = link,
                callback = self.parse_product,
                cb_kwargs={
                    "gender": gender
                }
                )
        next_page = response.css("a[aria-label='Next page'] ::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url = response.urljoin(next_page), 
                callback=self.parse,
                cb_kwargs={
                    # "category_name": category_name,
                    "gender": gender
                })
            

    
    def parse_product(self,response, gender):

        regularPriceDiv = response.css('.price__regular .price-item.price-item--regular ::text').get().strip()
        salePriceInSaleDiv = response.css('.price__sale .price-item.price-item--sale ::text').get().strip()
        if not regularPriceDiv==salePriceInSaleDiv: ##If not on sale
            salePrice=0
            price = re.sub(r"[^\d.]","",response.css('.price__regular .price-item.price-item--regular ::text').get().strip())

        else:
            salePrice = salePrice = re.sub(r"[^\d.]","",response.css(".price__sale .price-item.price-item--sale.price-item--last ::text").get().strip())
            price = re.sub(r"[^\d.]","",response.css(".price__sale .price-item.price-item--regular ::text").get().strip())

        
        #TODO When there's no sale add the logic

        item = SpiderItem()


        item["imageLink"]= "https:" + response.css(".image-magnify-lightbox ::attr(src)").get()
        item["name"] = response.css(".product__title h1::text").get().strip()
        item["price"] = re.sub(r"[^\d.]", "", response.css(".price-item.price-item--regular ::text").getall()[-1].strip()) 
        item["salePrice"] = salePrice
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = classify_product(item["name"])
        item["storeId"] = 1007

        yield item
