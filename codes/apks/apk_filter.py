# coding=utf-8
import click
import os
import shutil
import random
import glob
from collections import defaultdict

import database


@click.command()
@click.argument("target_folder")
@click.option("--market", type=click.Choice(['all', 'xiaomi', 'fossdroid', 'apkpure'], case_sensitive=False), default="all", help="Which market of apps to be filtered. Default is all.")
@click.option("--apk_size", type=int, default=100, help="The max threshold of apk size in MB. Default is 100MB, if it's 0 then not limit the apk size.")
@click.option("--app_num_per_type", type=int, default=100, help="The max number of apps in filtered folder for each app type. Default is 100, if it's 0 then not limit the number.")
def apk_filt(target_folder: str, market: str = "all", apk_size: int = 100, app_num_per_type: int = 100):
    if apk_size <= 0:
        limit_apk_size = False
    else:
        limit_apk_size = True

    if app_num_per_type <= 0:
        limit_type_num = False
    else:
        limit_type_num = True

    if market == "all":
        market_folders = ["../../data/xiaomi", "../../data/fossdroid", "../../data/apkpure"]
    else:
        market_folders = ["../../data/{}".format(market)]
    __current_folder__ = os.path.dirname(__file__)
    for _index_ in range(len(market_folders)):
        market_folders[_index_] = os.path.join(__current_folder__, market_folders[_index_])

    type_app_dict = defaultdict(list)
    db_handler = database.Database()
    _mb_ = float(1024 * 1024)
    for market_folder in market_folders:
        market_name = os.path.basename(market_folder)

        for app_folder in glob.glob(os.path.join(market_folder, "*")):
            apk_name = os.path.basename(app_folder)

            for update_folder in glob.glob(os.path.join(app_folder, "*")):
                version_name = os.path.basename(update_folder)

                if limit_apk_size:
                    apk_path = os.path.join(update_folder, apk_name)
                    if os.path.exists(apk_path) and os.path.getsize(apk_path) / _mb_ <= apk_size:
                        type_name = db_handler.get_app_type(market_name, apk_name)
                        output_type_folder = os.path.join(target_folder, type_name)
                        if not os.path.exists(output_type_folder):
                            os.makedirs(output_type_folder)
                        output_apk_path = os.path.join(output_type_folder, "{}-{}".format(version_name, apk_name))
                        type_app_dict[type_name].append((output_apk_path, apk_path))

    filter_number_dict = defaultdict(lambda: 0)
    for type_key in type_app_dict.keys():
        type_app_list = type_app_dict[type_key]

        if limit_type_num and len(type_app_list) > app_num_per_type:
            tmp_type_app_list = []
            random_index = random.sample(range(len(type_app_list)), app_num_per_type)
            for _index_ in random_index:
                tmp_type_app_list.append(type_app_list[_index_])
            type_app_list = tmp_type_app_list

        for output_apk_path, apk_path in type_app_list:
            filter_number_dict[type_key] += 1
            shutil.copy(apk_path, output_apk_path)

    print("Filter number for different app type: " + str(dict(filter_number_dict)))
    print("Done!")


if __name__ == '__main__':
    apk_filt()
