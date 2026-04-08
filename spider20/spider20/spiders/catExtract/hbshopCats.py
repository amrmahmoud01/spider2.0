# spiders/quotes.py

import scrapy


class HBShopCategoryExtractor(scrapy.Spider):
    name = 'hbCats'

    

    def start_requests(self):
        url = "https://hbshop.co/"
        yield scrapy.Request(
            url,
        )

    async def parse(self, response):
        menuItems = response.css(".mega-menu__list li")
        for item in menuItems:
            yield{
                "Category": item.css(".mega-menu__link ::text").get().strip(),
                "Link": response.urljoin(item.css(".mega-menu__link ::attr(href)").get())
            }
    
