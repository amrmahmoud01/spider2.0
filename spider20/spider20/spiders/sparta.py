import scrapy
import json
from spider20.items import SpiderItem
import os


class SpartaApiSpider(scrapy.Spider):
    name = "sparta"
    
    # These headers are the "secret sauce" you discovered in Postman

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
    
    
    custom_headers = {
        'Origin': 'https://spartaeg.myeasyorders.com',
        'Referer': 'https://spartaeg.myeasyorders.com/',
        'Currency-Id': 'vvvj772111f1v2v8v9j39d75zdvjvj8z2xz5xf78667707j345629j757jz83715',
        'Accept': 'application/json, text/plain, */*',
    }

    def start_requests(self):
        # Use the API URLs from your config
        spider_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(spider_dir, '..', 'configs', 'spartaConfig.json')
    
        # Normalized path to make it clean
        config_path = os.path.normpath(config_path)


        with open(config_path) as f:
            self.config=json.load(f)


        for category, info in self.config.items():
            urls = info["urls"]
            for url in urls:
                yield scrapy.Request(url = url["url"],
                                     headers=self.custom_headers,
                                callback=self.parse,
                                cb_kwargs={"category_name": category,
                                           "gender": url["gender"]}
                                )


    def parse(self, response, gender, category_name):
        # Use json.loads because the response is a raw JSON string
        data = json.loads(response.text)
        
        # EasyOrders usually stores the list in a 'data' key
        products = data.get('data', [])
        
        for product in products:
            item = SpiderItem()
            item["imageLink"]= product.get('thumb')
            item["name"] = product.get('name')
            item["price"] = product.get('price')
            item["salePrice"] = product.get('sale_price')
            item["productLink"] = f"https://spartaeg.myeasyorders.com/products/{product.get('slug')}",
            item["gender"] = gender
            item["type"] = category_name
            item["storeId"] = 1006

            yield item