# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZenkokuJinjaItem(scrapy.Item):
    referer = scrapy.Field()            # リファラ
    url = scrapy.Field()                # URL
    name = scrapy.Field()               # 名称
    area = scrapy.Field()               # 都道府県
    zip_code = scrapy.Field()           # 郵便番号
    address = scrapy.Field()            # 住所
    phone_number = scrapy.Field()       # 電話番号
    business_hours = scrapy.Field()     # 営業時間
    introduction = scrapy.Field()       # 紹介文
    height = scrapy.Field()             # 標高


