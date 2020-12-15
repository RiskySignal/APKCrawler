# coding=utf-8
import os

__current_folder__ = os.path.dirname(__file__)


def get_app_folder(item):
    market = item['market']
    apk_name = item['apk_name']
    version = item['version']
    return os.path.join(os.path.dirname(__file__), "../../../data", market, apk_name, version)


def get_file_size(file_path: str):
    size = os.path.getsize(file_path)

    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level + 1 > len(units):
        level = -1
    return ('{}.{:>03d} {}'.format(integer, remainder, units[level]))
