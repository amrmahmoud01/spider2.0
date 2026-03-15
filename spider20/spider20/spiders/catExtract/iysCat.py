# spiders/quotes.py

import scrapy
from scrapy_playwright.page import PageMethod


class IYSCategoryExtractor(scrapy.Spider):
    name = 'iyscat'

    

    def start_requests(self):
        url = "https://inyourshoe.com/"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # PageMethod("hover",".menu-header-item__title"),
                    PageMethod("click", ".navigation__control"),
                    PageMethod("wait_for_selector", ".submenu__list", state="visible", timeout=10000),
                    PageMethod("wait_for_timeout", 1000),
                ],
            },
            errback=self.errback,   # ✅ must be inside scrapy.Request()
        )

    async def parse(self, response):
        items = response.css(".submenu__item ")
        for item in items:
            link = item.css(".submenu__link::attr(href)").get()
            link = "https://inyourshoe.com" + link
            text = item.css(".submenu__link-text::text").get().strip()
            yield{text: link}
        page = response.meta.get("playwright_page")
        await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()


