import scrapy
import re
import json
import os
from spider20.items import SpiderItem
from scrapy.exceptions import CloseSpider

# from spider20.spider20.items import SpiderItem 


class HBSpider(scrapy.Spider):
    name = "hbshop"

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

        config_path = os.path.join(spider_dir, '..', 'configs', 'hbConfig.json')
    
        # Normalized path to make it clean
        config_path = os.path.normpath(config_path)


        with open(config_path) as f:
            self.config=json.load(f)

        for category, info in self.config.items():
            urls = info["urls"]
            for url in urls:
                yield scrapy.Request(url = url["url"],
                                callback=self.parse,
                                cb_kwargs={"category_name": category,
                                           "gender": url["gender"]}
                                )

        
        
        


    def parse(self, response, category_name, gender):
        products = response.css(".card-wrapper")
        for product in products:
            
            link = response.urljoin(product.css("a::attr(href)").get())
            yield scrapy.Request(
                url = link,
                callback = self.parse_product,
                cb_kwargs={
                    "category_name": category_name,
                    "gender": gender
                }
                )
        next_page = response.css("a[aria-label='Next page']::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url = response.urljoin(next_page), 
                callback=self.parse,
                cb_kwargs={
                    "category_name": category_name,
                    "gender": gender
                })
            

    
    def parse_product(self,response, category_name, gender):

        checkRegularPriceInSaleDiv = response.css('.price__sale .price-item.price-item--regular ::text').get().strip()
        if checkRegularPriceInSaleDiv == '' or checkRegularPriceInSaleDiv=='0.00 EGP':
            salePrice=0
            price = re.sub(r"[^\d.]","",response.css('.price__regular .price-item.price-item--regular ::text').get().strip())


        else:
            salePrice = salePrice = re.sub(r"[^\d.]","",response.css(".price__sale .price-item.price-item--sale.price-item--last ::text").get().strip())
            price = re.sub(r"[^\d.]","",response.css(".price__sale .price-item.price-item--regular ::text").get().strip())



        item = SpiderItem()

        item["imageLink"]= "https:" + response.css(".image-magnify-hover::attr(src)").get()
        item["name"] = response.css(".product__title h1::text").get().strip()
        item["price"] = price
        item["salePrice"] = salePrice
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = category_name
        item["storeId"] = 1008
    
        yield item
