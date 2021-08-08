import MySQLdb
from scrapy.exceptions import DropItem


class ZenkokuJinjaPipeline:
    def __init__(self, mysql_database, mysql_host, mysql_user, mysql_password, mysql_charset):
        self.mysql_database = mysql_database
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_charset = mysql_charset
        self.connection = None
        self.c = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_database=crawler.settings.get('MYSQL_DATABASE'),
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET'),
        )

    def open_spider(self, spider):
        """
            Spider開始時にMySQLに接続する
            zenkoku_jinjaテーブルがない場合は作成する
        """
        params = {
            'host': self.mysql_host,
            'db': self.mysql_database,
            'user': self.mysql_user,
            'passwd': self.mysql_password,
            'charset': self.mysql_charset
        }
        # MySQLに接続してカーソルを取得
        self.connection = MySQLdb.connect(**params)
        self.c = self.connection.cursor()
        # テーブルが無ければ作成
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS zenkoku_jinja (
                id int not null auto_increment comment '識別ID',
                referer varchar(120) comment 'リファラー',
                url varchar(120) not null comment 'URL',
                name varchar(50) comment '名称',
                area varchar(20) comment '都道府県',
                zip_code varchar(20) comment '郵便番号',
                address varchar(200) comment '住所',
                phone_number varchar(20) comment '電話番号',
                business_hours varchar(500) comment '営業時間',
                introduction varchar(3000) comment '紹介文',
                height int comment '標高',
                
                primary key (id),
                index area_index (area)

            ) CHARACTER SET utf8 COLLATE utf8_general_ci
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        """
            ItemをMySQLに保存する
        """
        # 既に登録されたデータは保存しない
        self.c.execute("""
            SELECT * FROM zenkoku_jinja WHERE detail_url = %s
        """, (item['url'],))
        saved_url = self.c.fetchone()
        if saved_url:
            raise DropItem(f'{saved_url}は既にデータベースに登録されています')
        # 登録されていない場合は保存する
        else:
            self.c.execute("""
                INSERT INTO zenkoku_jinja(
                    referer,
                    url,
                    name,
                    area,
                    zip_code,
                    address,
                    phone_number,
                    business_hours,
                    introduction,
                    height
                )
                VALUES (
                    %(referer)s,
                    %(url)s,
                    %(name)s,
                    %(area)s,
                    %(zip_code)s,
                    %(address)s,
                    %(phone_number)s,
                    %(business_hours)s,
                    %(introduction)s,
                    %(height)s
                )
            """, dict(item))
            self.connection.commit()
        return item

    def close_spider(self, spider):
        """
            Spider終了時にMySQLを切断する
        """
        self.connection.close()
