import scrapy
import re
import json
import os
from spider20.items import SpiderItem

# from spider20.spider20.items import SpiderItem 


class OrSpider(scrapy.Spider):
    name = "rojada"

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

        config_path = os.path.join(spider_dir, '..', 'configs', 'rojadaConfig.json')
    
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
                                           "gender": "women"}
                                )

        
        
        


    def parse(self, response, category_name, gender):
        products = response.css(".product-small.box")
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
        next_page = response.css(".pagination__item--prev ::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url = response.urljoin(next_page), 
                callback=self.parse,
                cb_kwargs={
                    "category_name": category_name,
                    "gender": gender
                })
            

    
    def parse_product(self,response, category_name, gender):

        onSale = len(response.css(".product-main bdi::text").getall())==2

        if onSale:
            
            rawSalePrice = response.css(".product-main bdi::text").getall()[1]
            rawSalePriceNoDot = rawSalePrice.replace(".","")
            rawSalePriceNoComma = rawSalePriceNoDot.replace(",",".")
            salePrice = re.sub(r"[^\d.]", "", rawSalePriceNoComma)

            rawPrice = response.css(".product-main bdi::text").getall()[0]
            rawPriceNoDot = rawPrice.replace(".","")
            rawPriceNoComma = rawPriceNoDot.replace(",",".")
            price = re.sub(r"[^\d.]", "", rawPriceNoComma)

        else:

            rawPrice = response.css(".product-main bdi::text").getall()[0]
            rawPriceNoDot = rawPrice.replace(".","")
            rawPriceNoComma = rawPriceNoDot.replace(",",".")
            price = re.sub(r"[^\d.]", "", rawPriceNoComma)

            salePrice = 0 
        

        

        item = SpiderItem()

        item["imageLink"]= "https:" + response.css(".woocommerce-product-gallery__image img::attr(data-src)").get() 
        item["name"] = response.css(".product-title ::text").get().strip()
        item["price"] = price
        item["salePrice"] = salePrice
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = category_name
        item["storeId"] = 1005

        yield item
