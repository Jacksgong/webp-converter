import os
from os import listdir, makedirs, remove, rename

from os.path import getsize, exists
from shutil import copyfile
from sys import argv

import re

__version__ = '1.0.0'
__author__ = 'JacksGong'

RESET = '\033[0m'
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def termcolor(fg=None, bg=None):
    codes = []
    if fg is not None: codes.append('3%d' % fg)
    if bg is not None: codes.append('10%d' % bg)
    return '\033[%sm' % ';'.join(codes) if codes else ''


def colorize(message, fg=None, bg=None):
    return termcolor(fg, bg) + message + RESET


def print_process(message):
    print colorize(message, fg=YELLOW)


def size_diff(left, right):
    return getsize(left) - getsize(right)


image_dir_path = None
quality_ratio = 100

# load config
image_dir_path_re = re.compile(r'image-path: *(.*)')
quality_ratio_re = re.compile(r'quality-ratio: *(\d*)')

conf_file_path = '.webp.conf'
if not exists(conf_file_path):
    exit(colorize(
        'Please create \'.webp.conf\' file, and add config:\nimage-path: /the/origin/image/path\nquality-ratio:[0~100](default is 100)',
        fg=RED))

conf_file = open(conf_file_path, 'r')
for line in conf_file:
    line = line.strip()
    if line.startswith('#') or line.startswith('/') or line.startswith('*'):
        continue
    image_dir_path_process = image_dir_path_re.search(line)
    if image_dir_path_process is not None:
        image_dir_path = image_dir_path_process.groups()[0]
        continue

    quality_ratio_process = quality_ratio_re.search(line)
    if quality_ratio_process is not None:
        quality_ratio = int(quality_ratio_process.groups()[0])
        continue

    print colorize('unknown config ' + line, fg=YELLOW)
conf_file.close()

if image_dir_path is None:
    exit(colorize(
        'Please create add config:\nimage-path: /the/origin/image/path', fg=RED))

command_prefix = 'cwebp '
if quality_ratio >= 100:
    command_prefix += '-lossless -q 100 '
else:
    command_prefix += '-q ' + quality_ratio.__str__() + ' '

is_clean_env = False
if argv.__len__() > 1:
    value = argv[1]
    if value == '-withClean':
        is_clean_env = True
    else:
        exit(colorize(
            "unknown arg: " + value + " only support '-withClean' to clean environment", fg=RED))

root = 'webp-converted/'
keep_origin_path = root + 'origin/'
convert_fail_path = root + 'failed/'
swap_webp_path = root + 'swap.webp'

if not exists(root):
    makedirs(root)
elif is_clean_env:
    remove(root)

all_reduce_size = 0
process_file_count = 0
failed_convert_count = 0

if exists(swap_webp_path):
    remove(swap_webp_path)

for image_file_name in listdir(image_dir_path):
    image_file_path = image_dir_path + '/' + image_file_name
    print_process('convert for ' + image_file_name)

    output_file_path = root + image_file_name + '.webp'
    if exists(output_file_path):
        # has already converted!
        reduce_size = size_diff(image_file_path, swap_webp_path)

        if reduce_size < 0:
            exit('failed! ' + image_file_name + ' reduce ' + reduce_size)

        all_reduce_size += reduce_size
        print_process(image_file_name + ' has already converted! reduce: ' + reduce_size)
        continue

    os.system(command_prefix + image_file_path + ' -o ' + swap_webp_path)
    if not exists(swap_webp_path):
        # convert failed!
        print_process("can't convert " + image_file_name)
        failed_convert_count += 1

        if not exists(convert_fail_path):
            makedirs(convert_fail_path)
        copyfile(image_file_path, convert_fail_path + image_file_name)
        continue

    reduce_size = size_diff(image_file_path, swap_webp_path)
    if reduce_size < 0:
        # invalid convert
        print_process('ignore ' + image_file_name + ', reduce ' + reduce_size.__str__())
        remove(swap_webp_path)

        if not exists(keep_origin_path):
            makedirs(keep_origin_path)
        copyfile(image_file_path, keep_origin_path + image_file_name)
        continue

    process_file_count += 1
    all_reduce_size += reduce_size
    print_process('reduce ' + reduce_size.__str__() + ' because of ' + image_file_name)
    rename(swap_webp_path, output_file_path)

print_process(
    'reduce size: ' + all_reduce_size.__str__() + ' from file count: ' + process_file_count.__str__() + ' failed convert file count: ' + failed_convert_count.__str__())
