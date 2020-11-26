# coding=utf-8
import argparse
import os
import time
import subprocess
from database import Database
from utils import cal_file_hash


def get_apk_info(apk_path, print_info=True):
    """
    :return: [{"app_title":.., "type_name":.., "market_name":.., "href":.., "language":..},...]
    """
    if not os.path.exists(apk_path) or not os.path.isfile(apk_path):
        raise FileNotFoundError("The apk {} is not existing.".format(apk_path))

    sha256_value = cal_file_hash(apk_path)
    sql_str = "select app_title, type_name, market_name, href from app " \
              "inner join `update` u on app.app_id = u.app_id " \
              "inner join market m on m.market_id=app.market_id " \
              "inner join app_type a on app.type_id = a.type_id " \
              "inner join link l on app.app_link_id = l.link_id " \
              "where apk_hash=unhex(%s);"
    db_handler = Database()
    cursor = db_handler.get_cursor()
    cursor.execute(
        sql_str,
        sha256_value
    )
    results = cursor.fetchall()

    for result in results:
        result['app_title'] = result['app_title'].decode('utf-8')
        result['type_name'] = result['type_name'].decode('utf-8')
        result['market_name'] = result['market_name'].decode('utf-8')
        result['href'] = result['href'].decode('utf-8')
        result['language'] = "中文" if result['market_name'] == "xiaomi" else "English"

    if print_info:
        print("APK file: {}\nSHA256 Value: {}".format(apk_path, sha256_value))
        if results:
            print("Find {} information about it.".format(len(results)))

            for result in results:
                print("-" * 64)
                print("App Title: {app_title}\nType Name: {type_name}\nMarket Name: {market_name}\nHref: {href}\nLanguage: {language}".format(**result))
            print("-" * 64)
        else:
            print("Not found any crawler information about it.")

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get apks info.")
    parser.add_argument("apk_path", type=str, help="The apks folder path.")
    arg_infos = parser.parse_args()

    apks_path = arg_infos.apk_path
    apks = []
    apk_paths = []
    apk_sizes = []
    for root, dirs, files in os.walk(apks_path):
        for f in files:
            if f.endswith('.apk'):
                apks.append(os.path.join(root,f))

    timenow = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    logfile = open('../../log/apk_info_%s.log'%(timenow),'a+')
    log = []
    for apk in apks:
        ###### Get Crawler info ######
        results = get_apk_info(apk)
        if results:
            print("Find {} information about it.".format(len(results)))
            for result in results:
                print("-" * 64)
                print("App Title: {app_title}\nType Name: {type_name}\nMarket Name: {market_name}\nHref: {href}\nLanguage: {language}".format(**result))
                log.append("-" * 64 + '\n')
                log.append("App Title: {app_title}\nType Name: {type_name}\nMarket Name: {market_name}\nHref: {href}\nLanguage: {language}\n".format(**result))
        else:
            log.append("No Crawler info of APK "+apk+'\n')
            print("Not found any crawler information about it.")
        ###### Get SDK and permission info ######
        command = 'aapt list -a '+ apk +' > apkversion.txt'
        ret = subprocess.call(command, shell=True)
        if ret == 0:
            # find targetSdkVersion in apkversion.txt
            # example : android:targetSdkVersion(0x0101020c)=(type 0x10)0xf - 0xf - 15
            sdk_info = 'android:targetSdkVersion'
            permission_info = 'android.permission'
            fp = open('apkversion.txt','r')
            lines = fp.readlines()
            fp.close()
            flines = len(lines)
            print('=== Processing APK '+apk+' ===')
            log.append('=== SDK and Permission info of APK '+apk+' ===\n')
            for i in range(flines):
                if sdk_info in lines[i]:
                    sdkversion = lines[i].rsplit(')')[-1].strip()
                    print('targetSdkVersion:'+sdkversion)
                    log.append('targetSdkVersion:'+sdkversion+'\n')
                if permission_info in lines[i]:
                    permission = lines[i].rsplit('\"')[-2]
                    print('uses-permission:'+permission)
                    log.append('uses-permission:'+permission+'\n')
        else:
            print('[AAPT PROCESS WARNING]'+apk)
        log.append("-" * 64 + '\n')
    logfile.writelines(log)

    if os.path.exists('apkversion.txt'):
        os.remove('apkversion.txt')

