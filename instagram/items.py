# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    username = scrapy.Field()
    full_name = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    post_data = scrapy.Field()
    master_id = scrapy.Field()
    friendship = scrapy.Field()
    _id = scrapy.Field()



