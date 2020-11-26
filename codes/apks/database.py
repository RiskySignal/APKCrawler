# coding=utf-8
import logging
from typing import List

import pymysql
from pymysql.constants import FIELD_TYPE

import settings as settings
from items import AppDetail


class Database(object):
    """
    Database Operation Superclass
    """

    def __init__(self):
        self.db_type = settings.DB_TYPE
        self.db_host = settings.DB_HOST
        self.db_database = settings.DB_DATABASE
        self.db_user = settings.DB_USER
        self.db_password = settings.DB_PASSWORD
        self.db_charset = settings.DB_CHARSET

        # init db connect
        self.db = None
        self.__connect__()

        self.logger = logging.getLogger("Database")

    def __connect__(self):
        """
        connect to database
        """
        orig_conv = pymysql.converters.conversions
        orig_conv[FIELD_TYPE.BIT] = lambda data: data == b'\x01'

        db_params = dict(
            host=self.db_host,
            db=self.db_database,
            user=self.db_user,
            passwd=self.db_password,
            charset=self.db_charset,
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
            conv=orig_conv
        )

        self.db = pymysql.connect(**db_params)

    def get_cursor(self):
        if not self.db or not self.db.open:
            self.__connect__()
        return self.db.cursor()

    def close(self):
        """
        close connection
        """
        if self.db:
            self.db.close()
            self.db = None

    def get_image_status(self, image_id):
        sql_str = "select is_download from `image` where image_id=%s;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (image_id,)
        )
        result = cursor.fetchone()
        if result:
            return result['is_download']
        else:
            return False

    def get_update_status(self, update_id):
        sql_str = "select is_download from `update` where update_id=%s;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (update_id,)
        )
        result = cursor.fetchone()
        if result:
            return result['is_download']
        else:
            return False

    def insert_app(self, item: AppDetail):
        """
        insert information into database, and return whether the apk file is download
        """
        try:
            cursor = self.get_cursor()
            cursor.callproc(
                "insert_app_update",
                (item['app_title'], item['apk_name'], item['app_link'], item['developer'], item['category'], item['market'], item['version'], item['size'], item['download_link'], item['update_date'])
            )
            result = cursor.fetchone()
            if result:
                item['update_id'] = result['update_id']
            else:
                raise pymysql.DatabaseError("Get update_id Error.")
        except Exception as _err:
            self.db.rollback()
            raise _err
        else:
            self.db.commit()

        for picture_link in item['picture_links']:
            try:
                cursor.callproc(
                    "insert_image",
                    (picture_link, item['update_id'])
                )
                result = cursor.fetchone()
                if result:
                    item['picture_link_ids'].append(result['image_id'])
                else:
                    raise pymysql.DatabaseError("Get image_id Error.")
            except Exception as _err:
                self.db.rollback()
                raise _err
            else:
                self.db.commit()

    def set_update_available(self, update_id, file_size, file_hash):
        try:
            cursor = self.get_cursor()
            cursor.callproc(
                "set_update_available",
                (update_id, file_size, file_hash)
            )
        except Exception as _err:
            self.db.rollback()
            raise _err
        else:
            self.db.commit()

    def set_image_available(self, image_id):
        try:
            cursor = self.get_cursor()
            cursor.callproc(
                "set_image_available",
                (image_id,)
            )
        except Exception as _err:
            self.db.rollback()
            raise _err
        else:
            self.db.commit()

    def get_app_number(self, market_name: str):
        sql_str = "select count(*) " \
                  "from `app` a " \
                  "inner join `market` b on a.market_id=b.market_id " \
                  "where market_name=%s;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (market_name,)
        )
        result = cursor.fetchone()
        if result:
            return result['count(*)']
        else:
            raise ValueError("Get {} app number Error.".format(market_name))

    def get_update_number(self, market_name: str):
        sql_str = "select count(*) " \
                  "from `app` a " \
                  "inner join `market` b on a.market_id=b.market_id " \
                  "inner join `update` c on a.app_id=c.app_id " \
                  "where market_name=%s;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (market_name,)
        )
        result = cursor.fetchone()
        if result:
            return result['count(*)']
        else:
            raise ValueError("Get {} update number Error.".format(market_name))

    def get_available_update_number(self, market_name: str):
        sql_str = "select count(*) " \
                  "from `app` a " \
                  "inner join `market` b on a.market_id=b.market_id " \
                  "inner join `update` c on a.app_id=c.app_id " \
                  "where market_name=%s and is_download=TRUE;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (market_name,)
        )
        result = cursor.fetchone()
        if result:
            return result['count(*)']
        else:
            raise ValueError("Get {} available update number Error.".format(market_name))

    def get_diff_type_update_number(self):
        sql_str = "select count(*), type_name " \
                  "from `app` a " \
                  "inner join `update` b on a.app_id=b.app_id " \
                  "inner join `app_type` c on a.type_id=c.type_id " \
                  "group by type_name;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
        )
        results = cursor.fetchall()
        if results:
            type_names = []
            type_counts = []
            for result in results:
                count = result['count(*)']
                type_name = result['type_name'].decode('utf-8')  # type: str
                type_names.append(type_name)
                type_counts.append(count)
            return type_names, type_counts
        else:
            raise ValueError("Get different type update number Error.")

    def get_app_type(self, market_name: str, apk_name: str):
        sql_str = "select type_name " \
                  "from `app` a " \
                  "inner join `app_type` b on a.type_id=b.type_id " \
                  "inner join `market` c on a.market_id=c.market_id " \
                  "where market_name=%s and apk_name=%s;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str,
            (market_name, apk_name)
        )
        result = cursor.fetchone()
        if result:
            return result['type_name'].decode('utf-8')  # type: str
        else:
            raise ValueError("Get app type name Error.")

    def get_all_app_type(self):
        sql_str = "select type_id, type_name from app_type;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str
        )
        results = cursor.fetchall()
        type_datas = []
        if results:
            for result in results:
                type_datas.append((result['type_id'], result['type_name'].decode('utf-8')))
        else:
            raise ValueError('Get type Error.')

        return type_datas

    def get_all_market(self):
        sql_str = "select market_id, market_name from market;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str
        )
        results = cursor.fetchall()
        market_datas = []
        if results:
            for result in results:
                market_datas.append((result['market_id'], result['market_name'].decode('utf-8')))
        else:
            raise ValueError("Get market Error.")

        return market_datas

    def update_information(self, apk_hash: str, malware: bool = None, obfuscation: bool = None, sdk_level: str = None, authority_list: List[str] = None):
        """
        根据分析更新数据库中apk的信息
        :param apk_hash: apk hash, is a sha256 value of apk file. See the algorithm in utils.cal_file_hash.
        :param malware:  whether the apk is a malware
        :param obfuscation: whether the apk uses the obfuscation
        :param sdk_level: sdk level
        :param authority_list: authority list with data like [<authority_name>, <authority_name>, ....]
        """
        if apk_hash is None or malware is None or obfuscation is None or sdk_level is None or authority_list is None or len(authority_list) == 0:
            logging.info("No information for apk (hash: {}) need to update.".format(apk_hash))
            return
        if malware is not None or obfuscation is not None or sdk_level is not None:
            try:
                cursor = self.get_cursor()

                sql_str = "UPDATE `update` SET "
                params = []
                # 生成sql字符串
                if malware is not None:
                    sql_str += "`malware` = %s, "
                    params.append(malware)
                if obfuscation is not None:
                    sql_str += "`obfuscation` = %s, "
                    params.append(obfuscation)
                if sdk_level is not None:
                    sql_str += "`sdk_level` = %s, "
                    params.append(sdk_level)
                sql_str = sql_str[:-2] + " where apk_hash = unhex(%s);"
                params.append(apk_hash)
                cursor.execute(
                    sql_str, params
                )
            except pymysql.Error as _err_:
                self.db.rollback()
                raise _err_
            else:
                self.db.commit()

        if authority_list is not None:
            try:
                cursor = self.get_cursor()
                for authority in authority_list:
                    cursor.callproc(
                        "insert_authority_relation",
                        (apk_hash, authority)
                    )
            except pymysql.Error as _err_:
                self.db.rollback()
                raise _err_
            else:
                self.db.commit()
