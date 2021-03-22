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
        except pymysql.Error as _err:
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
        sql_str = "select type_id, type_name from app_type order by type_name;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str
        )
        results = cursor.fetchall()
        type_data = []
        if results:
            for result in results:
                type_data.append((result['type_id'], result['type_name'].decode('utf-8')))
        else:
            raise ValueError('Get type Error.')

        return type_data

    def get_all_market(self):
        sql_str = "select market_id, market_name from market;"
        cursor = self.get_cursor()
        cursor.execute(
            sql_str
        )
        results = cursor.fetchall()
        results = [] if not results else results
        for result in results:
            result.update({
                "market_name": result['market_name'].decode('utf-8')
            })

        return results

    def update_information(self, apk_hash: str, malware: bool = None, obfuscation: bool = None, sdk_level: str = None, authority_list: List[str] = None):
        """
        根据分析更新数据库中apk的信息
        :param apk_hash: apk hash, is a sha256 value of apk file. See the algorithm in utils.cal_file_hash.
        :param malware:  whether the apk is a malware
        :param obfuscation: whether the apk uses the obfuscation
        :param sdk_level: sdk level
        :param authority_list: authority list with data like [<authority_name>, <authority_name>, ....]
        """
        if apk_hash is None or (malware is None and obfuscation is None and sdk_level is None and authority_list is None and len(authority_list) == 0):
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

    def get_all_app(self, market_id):
        cursor = self.get_cursor()
        sql_str = "select app_id, app_title from app where market_id=%s;"
        cursor.execute(sql_str, (market_id,))
        results = cursor.fetchall()
        results = [] if not results else results
        for result in results:
            result.update({
                "app_title": result['app_title'].decode('utf-8')
            })
        return results

    def get_all_updates(self, app_id):
        cursor = self.get_cursor()
        sql_str = "select update_id, version from `update` where app_id=%s and is_delete=0;"
        cursor.execute(sql_str, (app_id,))
        results = cursor.fetchall()
        results = [] if not results else results
        for result in results:  # type: dict
            result.update({
                "version": result['version'].decode('utf-8')
            })
        return results

    def get_information_by_update_id(self, update_id):
        cursor = self.get_cursor()
        sql_str = "select update_id, version, `size`, b.href as download_href, is_download, hex(apk_hash) as `hash`, malware, obfuscation, sdk_level, update_date, is_delete, app_title, apk_name, d.href as app_href, developer_name, type_name, market_name" \
                  " from `update` a" \
                  " left join link b on b.link_id=a.download_link_id" \
                  " left join app c on c.app_id=a.app_id" \
                  " left join link d on c.app_link_id=d.link_id" \
                  " left join developer e on e.developer_id=c.developer_id" \
                  " left join app_type f on f.type_id=c.type_id" \
                  " left join market g on g.market_id=c.market_id" \
                  " where update_id=%s;"
        cursor.execute(sql_str, (update_id,))
        results = cursor.fetchall()
        results = [] if not results else results
        for result in results:  # type: dict
            result.update({
                "version": result['version'].decode('utf-8'),
                "size": result['size'].decode('utf-8') if result['size'] is not None else None,
                "download_href": result['download_href'].decode('utf-8') if result['download_href'] is not None else None,
                "hash": result['hash'].decode('utf-8') if result['hash'] is not None else None,
                "sdk_level": result['sdk_level'].decode('utf-8') if result['sdk_level'] is not None else None,
                "update_date": result['update_date'].strftime("%Y-%m-%d") if result['update_date'] is not None else None,
                "app_title": result['app_title'].decode('utf-8'),
                "apk_name": result['apk_name'].decode('utf-8'),
                "app_href": result['app_href'].decode('utf-8') if result['app_href'] is not None else None,
                "developer_name": result['developer_name'].decode('utf-8') if result['developer_name'] is not None else None,
                "type_name": result['type_name'].decode('utf-8'),
                "market_name": result['market_name'].decode('utf-8')
            })
        return results

    def get_information_by_file_hash(self, file_hash):
        cursor = self.get_cursor()
        sql_str = "select update_id, version, `size`, b.href as download_href, is_download, hex(apk_hash) as `hash`, malware, obfuscation, sdk_level, update_date, is_delete, app_title, apk_name, d.href as app_href, developer_name, type_name, market_name" \
                  " from `update` a" \
                  " left join link b on b.link_id=a.download_link_id" \
                  " left join app c on c.app_id=a.app_id" \
                  " left join link d on c.app_link_id=d.link_id" \
                  " left join developer e on e.developer_id=c.developer_id" \
                  " left join app_type f on f.type_id=c.type_id" \
                  " left join market g on g.market_id=c.market_id" \
                  " where apk_hash=unhex(%s);"
        cursor.execute(sql_str, (file_hash,))
        results = cursor.fetchall()
        results = [] if not results else results
        for result in results:  # type: dict
            result.update({
                "version": result['version'].decode('utf-8'),
                "size": result['size'].decode('utf-8') if result['size'] is not None else None,
                "download_href": result['download_href'].decode('utf-8') if result['download_href'] is not None else None,
                "hash": result['hash'].decode('utf-8') if result['hash'] is not None else None,
                "sdk_level": result['sdk_level'].decode('utf-8') if result['sdk_level'] is not None else None,
                "update_date": result['update_date'].strftime("%Y-%m-%d") if result['update_date'] is not None else None,
                "app_title": result['app_title'].decode('utf-8'),
                "apk_name": result['apk_name'].decode('utf-8'),
                "app_href": result['app_href'].decode('utf-8') if result['app_href'] is not None else None,
                "developer_name": result['developer_name'].decode('utf-8') if result['developer_name'] is not None else None,
                "type_name": result['type_name'].decode('utf-8'),
                "market_name": result['market_name'].decode('utf-8')
            })
        return results

    def delete_apk_by_update_id(self, update_id):
        cursor = self.get_cursor()
        sql_str = "update `update` set is_delete=TRUE where update_id=%s;"
        try:
            cursor.execute(sql_str, (update_id,))
        except pymysql.Error as _err_:
            self.db.rollback()
            raise _err_
        else:
            self.db.commit()

    def delete_apk_by_hash(self, apk_hash):
        cursor = self.get_cursor()
        sql_str = "update `update` set is_delete=TRUE where apk_hash=unhex(%s);"
        try:
            cursor.execute(sql_str, (apk_hash,))
        except pymysql.Error as _err_:
            self.db.rollback()
            raise _err_
        else:
            self.db.commit()

    def get_all_sdk_level(self):
        cursor = self.get_cursor()
        sql_str = "select `sdk_level` from `update` group by sdk_level order by sdk_level;"
        cursor.execute(sql_str)
        results = cursor.fetchall()
        sdk_level_list = []
        for result in results:
            if result and result['sdk_level']:
                sdk_level_list.append(result['sdk_level'].decode('utf-8'))
        return sdk_level_list

    def get_all_authority(self):
        cursor = self.get_cursor()
        sql_str = "select authority_id, `authority_name` from `authority` order by authority_name;"
        cursor.execute(sql_str)
        results = cursor.fetchall()
        authority_list = []
        for result in results:
            if result and result['authority_name']:
                authority_list.append((result['authority_id'], result['authority_name'].decode('utf-8')))
        return authority_list

    def search_platform_not_delete(self):
        cursor = self.get_cursor()
        sql_str = "select market_id, `market_name` from `update` join app using(app_id) join market using(market_id) where is_delete=FALSE group by market_id order by market_name;"
        cursor.execute(sql_str)
        results = cursor.fetchall()
        market_list = []
        for result in results:
            if result and result['market_name']:
                market_list.append({
                    "market_id": result['market_id'],
                    "market_name": result['market_name'].decode('utf-8')
                })
        return market_list

    def search_app_not_delete(self, market_id):
        cursor = self.get_cursor()
        sql_str = "select app_id, app_title from `update` join app using(app_id) join market using(market_id) where is_delete=FALSE and market_id=%s group by app_id order by app_title;"
        cursor.execute(sql_str, (market_id,))
        results = cursor.fetchall()
        app_list = []
        for result in results:
            if result and result['app_title']:
                app_list.append({
                    "app_id": result['app_id'],
                    "app_title": result['app_title'].decode('utf-8')
                })
        return app_list

    def search_update_not_delete(self, app_id):
        cursor = self.get_cursor()
        sql_str = "select version, update_id from `update` join app using(app_id) where is_delete=FALSE  and app_id=%s group by version;"
        cursor.execute(sql_str, (app_id,))
        results = cursor.fetchall()
        update_list = []
        for result in results:
            if result and result['version']:
                update_list.append({
                    "update_id": result['update_id'],
                    "version": result['version'].decode('utf-8')
                })
        return update_list

    def insert_app_from_file(self, market_name, apk_hash, app_title, apk_name, developer, app_type, version, size, update_date):
        cursor = self.get_cursor()
        # check the app whether in the market
        check_sql_str = "select update_id from `update` join app using(app_id) join market using(market_id) where market_name=%s and apk_hash=unhex(%s);"
        cursor.execute(check_sql_str, (market_name, apk_hash))
        results = cursor.fetchall()
        if results and len(results) > 0:
            return False

        # insert app
        try:
            cursor.callproc(
                "insert_app_from_file",
                (app_title, apk_name, developer, app_type, market_name, version, size, update_date, apk_hash)
            )
        except pymysql.err as _err_:
            self.db.rollback()
            raise _err_
        else:
            self.db.commit()

        return True

    def get_local_update_info(self):
        cursor = self.get_cursor()
        sql_str = "select update_id, malware, obfuscation, sdk_level, is_delete from `update`;"
        cursor.execute(sql_str)
        results = cursor.fetchall()
        filtered_result = {}
        for result in results:
            if result and (result['malware'] or result['obfuscation'] or result['sdk_level'] or result['is_delete']):
                filtered_result[result['update_id']] = result
        return filtered_result

    def insert_local_update_info(self, update_info: dict):
        cursor = self.get_cursor()
        try:
            for update_id, item_info in enumerate(update_info):
                cursor.execute(
                    "update `update` set malware=%s, obfuscation=%s, sdk_level=%s, is_delete=%s where update_id=%s;",
                    (item_info['malware'], item_info['obfuscation'], item_info['sdk_level'], item_info['is_delete'], update_id)
                )
        except Exception as _err:
            self.db.rollback()
            raise _err
        else:
            self.db.commit()

    def execute(self, sql_str: str):
        try:
            cursor = self.get_cursor()
            cursor.execute(sql_str)
        except Exception as _err:
            self.db.rollback()
            raise _err
        else:
            self.db.commit()
