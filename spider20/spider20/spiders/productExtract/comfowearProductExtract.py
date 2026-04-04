import scrapy
from spider20.clean_text import clean_text

class ComfowearproductextractSpider(scrapy.Spider):
    name = "comfowearProductExtract"
    allowed_domains = ["comfowear.com"]
    start_urls = ["https://comfowear.com/collections/shop-all-men", "https://comfowear.com/collections/shop-all-women"]

    def parse(self, response):
        products = response.css('.card__heading a ::text').getall()
        for product in products:
            yield {"productName": clean_text(product.strip())}

        next_page = response.css("a[aria-label='Next page'] ::attr(href)").get()

        if next_page:
            yield scrapy.Request(url = response.urljoin(next_page))
