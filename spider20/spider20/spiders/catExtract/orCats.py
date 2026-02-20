# spiders/quotes.py

import scrapy


class OrCategoryExtractor(scrapy.Spider):
    name = 'orCats'

    

    def start_requests(self):
        url = "https://or-egypt.com/"
        yield scrapy.Request(
            url,
        )

    async def parse(self, response):
        menuItems = response.css(".header__menu-item")
        for item in menuItems:
            yield{
                "Category": item.css(".header__menu-item::text").get().strip(),
                "Link": response.urljoin(item.css(".header__menu-item::attr(href)").get())
            }
    
