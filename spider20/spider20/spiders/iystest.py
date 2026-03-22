import scrapy
import re
import json
import os
from spider20.items import SpiderItem

class InYourShoeSpider(scrapy.Spider):
    name = "iystest"

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "spider20.pipelines.SpiderPipeline": 300,
    #     },
    #     "CONCURRENT_REQUESTS": 4,
    #     "DOWNLOAD_DELAY": 1,
    #     # Ensure Playwright is actually used if the page is dynamic
    #     "DOWNLOAD_HANDLERS": {
    #         "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    #         "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    #     },
    #     "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    # }

    # Scrapy 2.13+ preferred way (Resolves Deprecation Warning)
    async def start(self):
        spider_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.normpath(os.path.join(spider_dir, '..', 'configs', 'iystestconfig.json'))

        with open(config_path) as f:
            self.config = json.load(f)

        for category, info in self.config.items():
            for url_data in info["urls"]:
                yield scrapy.Request(
                    url=url_data["url"],
                    callback=self.parse,
                    cb_kwargs={
                        "category_name": category,
                        "gender": url_data["gender"]
                    },
                    meta={"playwright": True} # Added to ensure JS renders
                )

    def parse(self, response, category_name, gender):
        # Target the list items in the product grid
        products = response.css("li.grid__item")
        
        self.logger.info(f"Found {len(products)} product cards on page.")

        for product in products:
            # Look for the link inside the h3 or the main anchor
            link = product.css("a.full-unstyled-link::attr(href)").get()
            if link:
                yield scrapy.Request(
                    url=response.urljoin(link),
                    callback=self.parse_product,
                    cb_kwargs={
                        "category_name": category_name,
                        "gender": gender
                    },
                    meta={"playwright": True}
                )

        # Pagination
        next_page = response.css("a.pagination__item--next::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse,
                cb_kwargs={"category_name": category_name, "gender": gender},
                meta={"playwright": True}
            )

    def parse_product(self, response, category_name, gender):
        item = SpiderItem()
        
        # Selectors adjusted for IYS Shopify theme
        name = response.css(".product__title h1::text").get()
        reg_price = response.css(".price-item--regular::text").get()
        sale_price = response.css(".price-item--sale::text").get()
        
        # Image: Usually the first featured image
        img = response.css(".product__media img::attr(src)").get()

        item["name"] = name.strip() if name else "Unknown"
        item["price"] = re.sub(r"[^\d.]", "", reg_price) if reg_price else "0"
        item["salePrice"] = re.sub(r"[^\d.]", "", sale_price) if sale_price else "0"
        item["imageLink"] = response.urljoin(img) if img else ""
        item["productLink"] = response.url
        item["gender"] = gender
        item["type"] = category_name
        item["storeId"] = 1004

        yield item