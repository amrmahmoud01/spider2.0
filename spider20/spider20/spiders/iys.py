import scrapy
import re
import json
import os
from spider20.items import SpiderItem

# from spider20.spider20.items import SpiderItem 


class IysSpider(scrapy.Spider):
    name = "iys"

    custom_settings = {
        "REDIRECT_ENABLED" : False,
        "ITEM_PIPELINES": {
            "spider20.pipelines.SpiderPipeline": 300,
        },
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "DOWNLOAD_DELAY": 1.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            },
                }
    item = SpiderItem()
    def start_requests(self):


        spider_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(spider_dir, '..', 'configs', 'iysconfig.json')
    
        # Normalized path to make it clean
        config_path = os.path.normpath(config_path)


        with open(config_path) as f:
            self.config=json.load(f)


        for category, info in self.config.items():
            urls = info["urls"]
            for url in urls:
                yield scrapy.Request(url = url,
                                callback=self.parse,
                                cb_kwargs={"category_name": category},
                                cookies={'country': 'EG', 'locale': 'ar_EG', 'currency': 'EGP'}
                                )

        
        
        


    def parse(self, response, category_name):
        products = response.css("product-item")
        for product in products:
            
            link = response.urljoin(product.css("a::attr(href)").get())
            yield scrapy.Request(
                url = link,
                callback = self.parse_product,
                cb_kwargs={
                    "category_name": category_name
                },
                cookies={'country': 'EG', 'locale': 'ar_EG', 'currency': 'EGP'}
                )
        next_page = response.css(".pagination-item__navigation-button--type-next::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url = response.urljoin(next_page), 
                callback=self.parse,
                cb_kwargs={
                    "category_name": category_name
                },
                cookies={'country': 'EG', 'locale': 'ar_EG', 'currency': 'EGP'}

                )
            

    
    def parse_product(self,response, category_name):

        genderText = response.css(".product-block-featured-icon__text p::text").get()
        gender = ""
        if genderText is not None:
            if("Male" in genderText.split()):
                if("Female" in genderText.split()):
                    gender="Unisex"
                else:
                    gender="Male"
            else:
                gender = "Female"
        else:
            gender = "Unisex"
        
        salePrice = response.css(".price__strikethrough .money::text").get()
        if salePrice is not None: 
            salePrice = re.sub(r"[^\d.]", "", salePrice)
        else: 
            salePrice = 0

        item = SpiderItem()

        item["imageLink"]= "https:" + response.css(".lightbox-media.lightbox-image img::attr(srcset)").get().split(",")[-1].split(" ")[1]
        item["name"] = response.css(".product-details__title::text").get().strip()
        item["price"] = re.sub(r"[^\d.]", "", response.css(".main .price__main .money::text").get()) if not salePrice else salePrice
        item["salePrice"] = re.sub(r"[^\d.]", "", response.css(".main .price__main .money::text").get()) if salePrice else salePrice
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = category_name
        item["storeId"] = 1000

        yield item
