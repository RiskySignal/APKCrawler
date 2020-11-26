# coding=utf-8
from database import Database
from settings import DEFAULT_SIZE, FILES_STORE
from pipelines import get_file_size
import os
import logging
from utils import cal_file_hash
import pymysql


def update_hash():
    db_handler = Database()
    cursor = db_handler.get_cursor()

    sql_str = "select update_id, market_name, apk_name, version, size from `update` " \
              "inner join app a on `update`.app_id = a.app_id " \
              "inner join market b on a.market_id = b.market_id " \
              "where is_download=TRUE and apk_hash is NULL;"
    update_hash_sql_str = "update `update` set apk_hash=unhex(%s) " \
                          "where update_id=%s;"
    update_size_sql_str = "update `update` set size=%s " \
                          "where update_id=%s;"

    try:
        # 获取全部update信息
        cursor.execute(sql_str)
        results = cursor.fetchall()

        for result in results:
            apk_path = os.path.join(FILES_STORE, result['market_name'].decode('utf-8'), result['apk_name'].decode("utf-8"), result['version'].decode('utf-8'), result['apk_name'].decode('utf-8'))
            if not os.path.exists(apk_path):
                logging.warning("Apk {} not found, but it had been downloaded.".format(apk_path))
                continue

            # 将sha256存储到数据库
            sha256_value = cal_file_hash(apk_path)

            cursor.execute(
                update_hash_sql_str,
                (sha256_value, result['update_id'])
            )

            # 更新apk size
            if result['size'].decode('utf-8') == DEFAULT_SIZE:
                apk_size = get_file_size(apk_path)

                cursor.execute(
                    update_size_sql_str,
                    (apk_size, result['update_id'])
                )
    except pymysql.Error as _err:
        db_handler.db.rollback()
        raise _err
    else:
        db_handler.db.commit()

        print("Done!")
    finally:
        db_handler.close()


if __name__ == '__main__':
    update_hash()
