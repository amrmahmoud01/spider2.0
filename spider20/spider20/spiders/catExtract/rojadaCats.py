# spiders/quotes.py

import scrapy


class OrCategoryExtractor(scrapy.Spider):
    name = 'rojadaCats'

    

    def start_requests(self):
        url = "https://rojada-egy.com/shop/"
        yield scrapy.Request(
            url,
        )

    async def parse(self, response):
        res = response.css(".cat-item")
        for item in res:
            yield{
                "Category": item.css("a::text").get().strip(),
                "Link": response.urljoin(item.css("a::attr(href)").get())
            }
    
