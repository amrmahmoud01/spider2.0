# spiders/quotes.py

import scrapy
from scrapy_playwright.page import PageMethod


class QuotesSpider(scrapy.Spider):
    name = 'lccat'

    def start_requests(self):
        url = "https://www.lcwaikiki.eg/en"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # PageMethod("hover",".menu-header-item__title"),
                    PageMethod("hover", "//a[contains(@class, 'menu-header-item__title') and normalize-space(text())='WOMEN']"),
                    PageMethod("wait_for_selector", ".menu-items-container", state="visible", timeout=10000),
                    PageMethod("wait_for_timeout", 1000),
                ],
            },
            errback=self.errback,   # ✅ must be inside scrapy.Request()
        )

    async def parse(self, response):
        
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        page = response.meta.get("playwright_page")
        screenshot = await page.screenshot(path="example.png", full_page=True)
        # items = response.css(".mega-menu .menu-zone-item")
        items = response.xpath(
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' menu-header-item__wrapper ')][.//a[normalize-space(text())='WOMEN' or normalize-space(text())='MEN']]"
            "/following-sibling::*[contains(concat(' ', normalize-space(@class), ' '), ' mega-menu ')]"
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' menu-zone-item ')]"
        )



        for item in items:
            link = item.css("span.menu-zone-item a.link__element::attr(href)").get()
            text = item.css("span.menu-zone-item a.link__element span::text").get()

            if(link):
                link ="https://www.lcwaikiki.eg"+ link
                if(text):
                    yield {text : link}
                else:
                    self.logger.warning("Missing category name for link: %s", link)
                    yield{"None": link}
            else:
                if(text):
                    yield{text: "NONE"}
        await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()


