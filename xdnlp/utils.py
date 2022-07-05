import hashlib
import os
import sys
import logging
import time
import csv

try:
    from pathlib import Path
except ImportError:
    Path = None

log_stderr = logging.StreamHandler(sys.stderr)
default_logger = logging.getLogger(__name__)
default_logger.setLevel(logging.DEBUG)
default_logger.addHandler(log_stderr)

package_path = os.path.abspath(os.path.dirname(sys.modules[__package__].__file__))


def sha1(query: str) -> str:
    m = hashlib.sha1()
    m.update(query.encode())
    return m.hexdigest()


def md5(query: str) -> str:
    m = hashlib.md5()
    m.update(query.encode())
    return m.hexdigest()


def read_lines(filename, func=None):
    if Path is not None and isinstance(filename, Path):
        filename = str(filename)
    if hasattr(filename, "read"):
        f_obj = filename
    else:
        f_obj = open(filename, 'r', encoding='utf-8')
    for l in f_obj:
        l = l.strip()
        if func is not None:
            l = func(l)
        yield l
    f_obj.close()


def read_csv_row(filename, func=None):
    if Path is not None and isinstance(filename, Path):
        filename = str(filename)
    if hasattr(filename, "read"):
        f_obj = filename
    else:
        f_obj = open(filename, 'r', encoding='utf-8')
    f_csv = csv.reader(f_obj)
    for row in f_csv:
        if func is not None:
            row = func(row)
        yield row
    f_obj.close()


def logging_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        default_logger.info('Function [%s] start' % func.__name__)
        t = func(*args, **kw)
        default_logger.info('Function [%s] cost time %.2f second' % (func.__name__, time.time() - local_time))
        return t

    return wrapper


if __name__ == '__main__':

    with open("/home/geb/PycharmProjects/whisper-data-dependence/online/preprocess/convertZ.txt", 'r',
              encoding='utf-8') as f, open(
        "/home/geb/PycharmProjects/whisper-data-dependence/preprocess/convertSpecial.txt", 'r',
        encoding='utf-8') as f2, open("data/letter_mapping.txt", 'w', encoding='utf-8') as f3:
        for line in f:
            a = line.strip().split()
            f3.write(f"{md5(a[0])}\t{a[1]}\t1\n")

        for line in f2:
            a = line.strip().split()
            f3.write(f"{md5(a[0])}\t{a[1]}\t0\n")
