# spiders/quotes.py

import scrapy
from scrapy_playwright.page import PageMethod


class DefactoCatExtractor(scrapy.Spider):
    name = 'defactocat'

    

    def start_requests(self):
        url = "https://www.defacto.com.eg/en-eg/man"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # PageMethod("hover",".menu-header-item__title"),
                    PageMethod("click", ".header__menu-button"),
                    PageMethod("wait_for_timeout", 2000),
                    PageMethod("click", "//a[contains(@class, 'menu-top__list--item-link') and normalize-space(text())='Man']"),
                    PageMethod("wait_for_timeout", 2000),
                ],
            },
            errback=self.errback,   # ✅ must be inside scrapy.Request()
        )

    async def parse(self, response):
        items = response.css("a.menu__main--item-link")
        for item in items:
            text = item.css("a.menu__main--item-link::attr(name)").get()
            link = item.css("a.menu__main--item-link::attr(href)").get()
            link = "https://www.defacto.com.eg" + link
            yield{link: text.strip()}


    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()


