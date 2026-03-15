# spiders/quotes.py

import scrapy


class OrCategoryExtractor(scrapy.Spider):
    name = 'cloudCats'

    

    def start_requests(self):
        url = "https://cloud-clothing.co/"
        yield scrapy.Request(
            url,
        )

    async def parse(self, response):
        menuItems = response.css(".dropdown-menu__item")
        for item in menuItems:
            yield{
                "Category": item.css(".dropdown-menu__item span::text").get().strip(),
                "Link": response.urljoin(item.css(".dropdown-menu__item::attr(href)").get())
            }
    
