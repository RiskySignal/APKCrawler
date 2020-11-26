# coding=utf-8
import hashlib


def cal_file_hash(file_path: str):
    sha256_value = hashlib.sha256()
    with open(file_path, 'rb') as _apk_file_:
        while True:
            data_flow = _apk_file_.read(8096)
            if not data_flow:
                break
            sha256_value.update(data_flow)
    sha256_value = sha256_value.hexdigest()
    return sha256_value
