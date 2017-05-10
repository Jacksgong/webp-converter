#!/usr/bin/python -u

'''
Copyright 2017, JacksGong(https://blog.dreamtobe.cn)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
from os import listdir, makedirs, remove, rename

from os.path import getsize, exists
from shutil import copyfile, rmtree
from sys import argv

import re

import operator

import itertools

__version__ = '2.0.0'
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


def human_bytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)


image_dir_path = None
quality_ratio = 100
ignore_transparency_image = False

# load config
image_dir_path_re = re.compile(r'image-path: *(.*)')
quality_ratio_re = re.compile(r'quality-ratio: *(\d*)')
ignore_transparency_re = re.compile(r'ignore-transparency-image: *(.*)')

conf_file_path = '.webp.conf'
if not exists(conf_file_path):
    exit(colorize(
        'Please create \'.webp.conf\' file, and add config:\nimage-path: /the/origin/image/path\nquality-ratio:[0~100](default is 100)\nignore-transparency-image: [true/false]',
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

    ignore_transparency_process = ignore_transparency_re.search(line)
    if ignore_transparency_process is not None:
        ignore_transparency_image = ignore_transparency_process.groups()[0] == 'true'
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
transparency_image_path = root + 'transparency/'
swap_webp_path = root + 'swap.webp'

if not exists(root):
    makedirs(root)
elif is_clean_env:
    rmtree(root)

all_reduce_size = 0
valid_convert_file_count = 0
failed_convert_count = 0
scan_file_count = 0
skip_file_count = 0
skip_transparency_file_count = 0

if exists(swap_webp_path):
    remove(swap_webp_path)


def handle_failed(_file_path, _file_name):
    print_process("NOT convert " + image_file_name + ' because convert failed!')
    if not exists(convert_fail_path):
        makedirs(convert_fail_path)
    copyfile(_file_path, convert_fail_path + _file_name)


for image_file_name in listdir(image_dir_path):
    if image_file_name == '.DS_Store':
        continue

    image_file_path = image_dir_path + '/' + image_file_name
    scan_file_count += 1

    output_file_path = root + image_file_name + '.webp'
    if exists(output_file_path):
        # has already converted!
        reduce_size = size_diff(image_file_path, output_file_path)

        if reduce_size < 0:
            exit('failed! ' + image_file_name + ' reduce ' + reduce_size.__str__())

        all_reduce_size += reduce_size
        print_process(image_file_name + ' has already converted! reduce: ' + reduce_size.__str__())
        continue

    if ignore_transparency_image and image_file_name.endswith('.png'):
        from PIL import Image

        try:
            img = Image.open(image_file_path, 'r')
        except IOError:
            failed_convert_count += 1
            handle_failed(image_file_path, image_file_name)
            continue

        has_transparency = False
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            alpha = img.convert('RGBA').split()[-1]

            for value in alpha.getdata():
                if value < 255:
                    print_process('NOT convert ' + image_file_name + ' because there is alpha[' + value.__str__() + ']')
                    has_transparency = True
                    break

        if has_transparency:
            if not exists(transparency_image_path):
                makedirs(transparency_image_path)

            skip_transparency_file_count += 1
            copyfile(image_file_path, transparency_image_path + image_file_name)
            continue

    print_process('convert for ' + image_file_name)
    os.system(command_prefix + image_file_path + ' -o ' + swap_webp_path)
    if not exists(swap_webp_path):
        # convert failed!
        failed_convert_count += 1
        handle_failed(image_file_path, image_file_name)
        continue

    reduce_size = size_diff(image_file_path, swap_webp_path)
    if reduce_size < 0:
        # invalid convert
        print_process('NOT convert ' + image_file_name + ' because the webp one is larger: ' + (-reduce_size).__str__())
        remove(swap_webp_path)

        skip_file_count += 1
        if not exists(keep_origin_path):
            makedirs(keep_origin_path)
        copyfile(image_file_path, keep_origin_path + image_file_name)
        continue

    valid_convert_file_count += 1
    all_reduce_size += reduce_size
    print_process('convert ' + image_file_name + ' and reduce size: ' + reduce_size.__str__())
    rename(swap_webp_path, output_file_path)

print '-----------------------------------------------'
print ' '
print colorize('All files handled on: ', fg=BLUE) + root
print ' '
print colorize('Scan files count: ', fg=GREEN) + scan_file_count.__str__()
print colorize('Converted files count: ', fg=GREEN) + valid_convert_file_count.__str__()
print colorize('Reduce size: ', fg=GREEN) + human_bytes(all_reduce_size)
print colorize('Skip files(because convert failed) count: ',
               fg=GREEN) + failed_convert_count.__str__() + ' (' + convert_fail_path + ')'
print colorize('Skip files(because the webp one is greater than origin one) count: ',
               fg=GREEN) + skip_file_count.__str__() + ' (' + keep_origin_path + ')'
if skip_transparency_file_count > 0:
    print colorize('Skip files(because there is transparency) count: ',
                   fg=GREEN) + skip_transparency_file_count.__str__() + ' (' + transparency_image_path + ')'
print ' '
print '-----------------------------------------------'
