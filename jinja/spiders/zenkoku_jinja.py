import re
import scrapy
from ..items import ZenkokuJinjaItem


class ZenkokuJinjaSpider(scrapy.Spider):
    name = 'zenkoku_jinja'
    allowed_domains = ['shrine.mobi']
    start_urls = ['https://shrine.mobi/']
    # スパイダーごとの設定
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 60,
        'ITEM_PIPELINES': {'jinja.pipelines.ZenkokuJinjaPipeline': 800}
    }

    # 都道府県ごとのURLを取得
    def parse(self, response):
        area_urls = response.xpath('//div[@id="map_box"]//ul/li/a/@href')
        if area_urls:
            for area_url in area_urls:
                yield response.follow(area_url.get(), callback=self.parse_list)
        else:
            self.logger.warn(f'起点ページから一覧URLを取得できませんでした...(URL:{response.url})')

    # 全ての詳細ページのURLを取得（ページング処理あり）
    def parse_list(self, response):
        # リファラの取得
        referer = response.url
        # 都道府県を取得
        area = response.css('div.line_head').re_first(r'<h2\s*[^>]*?>(.*?)の神社一覧\s*</h2>', default='')

        # 詳細ページのURLを取得
        detail_urls = response.xpath('//div[has-class("list_data")]//ul[has-class("list_main")]/li/a/@href')
        if detail_urls:
            for detail_url in detail_urls:
                # 受け渡す値の準備
                keyword_args = {
                    'referer': referer,
                    'area': area,
                }
                yield response.follow(detail_url.get(), callback=self.parse_detail, cb_kwargs=keyword_args)

        # ページング処理
        next_xpath = '//div[has-class("list_data")]//ul[has-class("linklist")]/li/span/following-sibling::a[1]/@href'
        next_page = response.xpath(next_xpath)
        if next_page:
            yield response.follow(next_page.get(), callback=self.parse_list)

    # 詳細ページから値を抽出
    def parse_detail(self, response, referer, area):
        item = ZenkokuJinjaItem()
        # 各項目を抽出
        item['referer'] = referer
        item['url'] = response.url
        item['area'] = area
        # 名称
        item['name'] = response.css('h1 span[itemprop="name"]::text').get(default='')
        # 郵便番号と住所
        zip_code = ''
        address = ''
        address_list = response.xpath('//dl/dt[contains(text(), "住所")]/following-sibling::dd//text()').getall()
        if address_list:
            # 住所の文字列を全て連結
            address_str = ''.join(address_list)
            # 郵便番号を取得
            zip_code_obj = re.search(r'〒?([0-9]{3}-?[0-9]{4})', address_str)
            if zip_code_obj is not None:
                zip_code = zip_code_obj.group(1)
            # 郵便番号以外を住所とする
            address = re.sub(r'〒?[0-9]{3}-?[0-9]{4}', '', address_str)
        item['zip_code'] = zip_code
        item['address'] = address
        # 電話番号
        phone_xpath = '//dl/dt[contains(text(), "電話番号")]/following-sibling::dd//text()'
        item['phone_number'] = response.xpath(phone_xpath).re_first(r'[0-9\-]+', default='')
        # 営業時間
        business_hours_xpath = '//dl/dt[contains(text(), "営業時間")]/following-sibling::dd//text()'
        item['business_hours'] = response.xpath(business_hours_xpath).get(default='')
        # 紹介文
        introduction_xpath = '//dl/dt[contains(text(), "ご由緒")]/following-sibling::dd//text()'
        item['introduction'] = response.xpath(introduction_xpath).get(default='')
        # 標高
        height_xpath = '//dl/dt[contains(text(), "標高")]/following-sibling::dd//text()'
        item['height'] = response.xpath(height_xpath).re_first(r'[0-9]+', default='')

        yield item
