# coding=utf-8
import time

from database import Database


def statistic():
    print("统计时间：" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    db_handler = Database()

    market_names = ['xiaomi', 'fossdroid', 'apkpure']

    # app number
    app_numbers = []
    for market_name in market_names:
        app_number = db_handler.get_app_number(market_name)
        app_numbers.append(app_number)

    # update number
    update_numbers = []
    for market_name in market_names:
        update_number = db_handler.get_update_number(market_name)
        update_numbers.append(update_number)

    # available update number
    available_update_numbers = []
    for market_name in market_names:
        available_update_number = db_handler.get_available_update_number(market_name)
        available_update_numbers.append(available_update_number)

    # diff type update number
    diff_type_names, diff_type_update_numbers = db_handler.get_diff_type_update_number()

    # print
    print_string = ""
    print_string += "已扫描的APP数量：\n\t"
    for _i in range(len(market_names)):
        print_string += "{}-{}\t\t".format(market_names[_i], app_numbers[_i])
    print_string += "\n"

    print_string += "已扫描的UPDATE数量：\n\t"
    for _i in range(len(market_names)):
        print_string += "{}-{}\t\t".format(market_names[_i], update_numbers[_i])
    print_string += "\n"

    print_string += "已下载的UPDATE数量：\n\t"
    for _i in range(len(market_names)):
        print_string += "{}-{}\t\t".format(market_names[_i], available_update_numbers[_i])
    print_string += "\n"

    print_string += "各分类的UPDATE数量：\n\t"
    for _i in range(len(diff_type_names)):
        print_string += "'{}'-{} ".format(diff_type_names[_i], diff_type_update_numbers[_i])
    print_string += "\n"

    print(print_string)


if __name__ == '__main__':
    statistic()
