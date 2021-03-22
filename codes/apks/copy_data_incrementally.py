# coding=utf-8
import argparse
import glob
import json
import logging
import os
import shutil
import time
from subprocess import Popen

from database import Database
from settings import DB_DATABASE

cur_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(cur_folder, "../../data")
copy_status_file = os.path.join(cur_folder, "../../data/copy_status.json")


def restore_copy_status(pre_copy_status_file: str = ""):
    if not pre_copy_status_file:  # reset the copy status
        with open(copy_status_file, 'w') as _file_:
            json.dump({}, _file_)
    else:
        if not os.path.exists(pre_copy_status_file):
            raise FileNotFoundError("File {} not found.".format(pre_copy_status_file))
        try:
            with open(copy_status_file, "r") as _file_:
                json.load(_file_)
        except Exception:
            raise ValueError("File is not a valid file.".format(pre_copy_status_file))
        else:
            shutil.copyfile(pre_copy_status_file, copy_status_file)

    logging.info("Restoring the copy status Success.")


def export_data(target_root_folder: str):
    assert target_root_folder is not None
    os.makedirs(target_root_folder, exist_ok=True)

    if os.path.exists(copy_status_file):
        with open(copy_status_file, 'r') as _file_:
            copy_status = json.load(_file_)
    else:
        copy_status = {}

    version_copy_folder_num = 0
    for platform_folder in glob.glob(os.path.join(data_folder, "*")):  # platform
        if not os.path.isdir(platform_folder):
            continue
        platform_name = os.path.basename(platform_folder)
        platform_copy_status = copy_status.get(platform_name)
        if platform_copy_status is None:
            platform_copy_status = {}

        for apk_folder in glob.glob(os.path.join(platform_folder, "*")):  # apk
            if not os.path.isdir(apk_folder):
                continue
            apk_name = os.path.basename(apk_folder)
            apk_copy_status = platform_copy_status.get(apk_name)
            if apk_copy_status is None:
                apk_copy_status = {}

            for version_folder in glob.glob(os.path.join(apk_folder, "*")):  # version
                if not os.path.isdir(version_folder):
                    continue
                version_name = os.path.basename(version_folder)
                version_copy_status = platform_copy_status.get(version_name)
                if version_copy_status is None:
                    version_copy_status = {}

                last_modify_time = os.path.getmtime(version_folder)
                for t_file in glob.glob(os.path.join(version_folder, "*")):  # file in version folder
                    last_modify_time = max(last_modify_time, os.path.getmtime(t_file))

                p_last_modify_time = version_copy_status.get("last_modify_time")
                if p_last_modify_time is None:
                    p_last_modify_time = -1

                if last_modify_time > p_last_modify_time:  # need to copy
                    last_copy_time = int(time.time())
                    target_version_folder = os.path.join(target_root_folder, platform_name, apk_name, version_name)
                    shutil.copytree(version_folder, target_version_folder)
                    version_copy_folder_num += 1

                    # update status
                    version_copy_status.update({
                        "last_copy_time": last_copy_time,
                        "last_modify_time": last_modify_time
                    })
                    apk_copy_status.update({
                        version_name: version_copy_status
                    })
                    platform_copy_status.update({
                        apk_name: apk_copy_status
                    })
                    copy_status.update({
                        platform_name: platform_copy_status
                    })

    # write the copy status
    with open(copy_status_file, 'w') as _file_:
        json.dump(copy_status, _file_)

    logging.info("Copy the apk data to folder {} Success. Total copy {} folders.".format(target_root_folder, version_copy_folder_num))


def export_database(target_root_folder: str):
    assert target_root_folder is not None
    os.makedirs(target_root_folder, exist_ok=True)

    # 直接导出数据库中的全部信息
    target_sql_file = os.path.join(
        os.path.abspath(target_root_folder), "apk_merge.sql"
    )
    with open(target_sql_file, 'w') as _file_:
        Popen(["mysqldump", "-uroot", "-p123456", DB_DATABASE], stdout=_file_)


def import_data(target_root_folder: str):
    for market_folder in glob.glob(os.path.join(target_root_folder, "*")):
        if os.path.isdir(market_folder):
            market_name = os.path.basename(market_folder)
            dst_folder = os.path.join(data_folder, market_name)
            shutil.copytree(market_folder, dst_folder)
    logging.info("Import data from Folder {} Success.".format(target_root_folder))


def import_database(target_root_folder: str):
    if not os.path.exists(os.path.join(target_root_folder, "apk_merge.sql")):
        raise FileNotFoundError("File apk_merge.sql is not exist in Folder {}.".format(target_root_folder))
    """
    首先把本地数据库中的额外数据导出
    """
    # 权限表, 权限关系表
    target_sql_file = os.path.join(
        os.path.abspath(target_root_folder), "local.sql"
    )
    with open(target_sql_file, 'w') as _file_:
        Popen(["mysqldump", "-uroot", "-p123456", DB_DATABASE, "authority", "authority_relation"], stdout=_file_)

    # update表
    db = Database()
    update_info_json = db.get_local_update_info()
    target_json_file = os.path.join(
        os.path.abspath(target_root_folder), "local.json"
    )
    with open(update_info_json, 'w') as _file_:
        json.dump(target_json_file, _file_)
    logging.info("Export update info to File {} Success.".format(target_json_file))

    """
    然后将外部的sql脚本运行，覆盖本地数据
    """
    apk_merge_sql_file = os.path.join(
        os.path.abspath(target_root_folder), "apk_merge.sql"
    )
    with open(apk_merge_sql_file, 'r') as _file_:
        line = _file_.readline()
        while line:
            db.execute(line)
            line = _file_.readline()

    """
    将本地语句库中的额外数据再导入
    """
    # 权限表，权限关系表
    with open(target_sql_file, 'r') as _file_:
        line = _file_.readline()
        while line:
            db.execute(line)
            line = _file_.readline()

    # update表
    with open(target_json_file, 'r') as _file_:
        update_info = json.load(_file_)
    db.insert_local_update_info(update_info)

    logging.info("Import Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Script for copying data incrementally.")
    parser.add_argument("target_path", type=str, help="Export data to which folder or Import data from which folder or restore copy status from which file.")
    parser.add_argument("--import_mode", default=False, type=bool, help="Whether on import mode. Default is False.")
    parser.add_argument("--restore_copy_mode", default=False, type=bool, help="If True, Script will restore the copy status from target_path(a pre-status json file) instead of import or export the data.")
    args = parser.parse_args()

    if args.restore_copy_mode:
        restore_copy_status(args.target_path)
        exit(0)

    if args.import_mode:
        import_data(args.target_path)
        import_database(args.target_path)
    else:
        export_data(args.target_path)
        export_database(args.target_path)
