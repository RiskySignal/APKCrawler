# coding=utf-8

def read_log_file(log_file):
    crawled_url = []
    with open(log_file, 'r') as _file_:
        for line in _file_.readlines():
            if "scrapy.core.engine" in line:
                infos = line.split()
                for info in infos:
                    if 'http' in info:
                        info = info[:-1]
                        crawled_url.append(info)

    return crawled_url


def log_analysis(log_file_a, log_file_b):
    """ find url in log file b but not in log file a."""
    crawled_url_a = read_log_file(log_file_a)
    crawled_url_b = read_log_file(log_file_b)  # type: list

    for url in crawled_url_b:
        if url not in crawled_url_a:
            print(url)


if __name__ == '__main__':
    file_a = "../../log/" + "1580663423.txt"
    file_b = "../../log/" + "1580710260.txt"

    log_analysis(file_a, file_b)
