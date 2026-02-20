# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    type = scrapy.Field()
    productLink = scrapy.Field()
    storeId = scrapy.Field()    
    imageLink = scrapy.Field()
    gender = scrapy.Field()
    salePrice = scrapy.Field()
    colors = scrapy.Field()
    pass
