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

from os.path import getsize, exists, join
from shutil import copyfile, rmtree
from sys import argv, exit
import time

import re

__version__ = '3.0.0'
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

def resource_path(relative_path):
    base_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else relative_path
    return join(base_dir, relative_path)

def convert(image_file_path, image_file_name, webp_file_path):
    # whether has already converted
    if exists(webp_file_path):
        # has already converted!
        reduce_size = size_diff(image_file_path, webp_file_path)

        if reduce_size < 0:
            remove(webp_file_path)
            print_process(
                image_file_name + ' has already converted, but it larger than origin-image: ' + reduce_size.__str__() + ' so, remove it and re-convert it!')
        else:
            print_process(image_file_name + ' has already converted! reduce: ' + reduce_size.__str__())
            return RESULT_ALREADY_EXIST, reduce_size

    # transparency
    if ignore_transparency_image and image_file_name.endswith('.png'):
        from PIL import Image

        try:
            img = Image.open(image_file_path, 'r')
        except IOError:
            print_process("NOT convert " + image_file_name + ' because convert failed!')
            return RESULT_FAILED, 0

        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            alpha = img.convert('RGBA').split()[-1]
            for pixel in alpha.getdata():
                if pixel < 255:
                    print_process('NOT convert ' + image_file_name + ' because there is alpha[' + pixel.__str__() + ']')
                    return RESULT_WITH_TRANSPARENCY, 0

    print_process('convert for ' + image_file_name)

    os.system(command_prefix + image_file_path + ' -o ' + swap_webp_path)
    # whether convert failed
    if not exists(swap_webp_path):
        # convert failed!
        print_process("NOT convert " + image_file_name + ' because convert failed!')
        return RESULT_FAILED, 0

    reduce_size = size_diff(image_file_path, swap_webp_path)
    if reduce_size < 0:
        # invalid convert
        print_process('NOT convert ' + image_file_name + ' because the webp one is larger: ' + (-reduce_size).__str__())
        remove(swap_webp_path)
        return RESULT_WEBP_LARGER, 0

    print_process('convert ' + image_file_name + ' and reduce size: ' + reduce_size.__str__())
    rename(swap_webp_path, webp_file_path)
    if exists(swap_webp_path): remove(swap_webp_path)
    return RESULT_SUCCESS, reduce_size


# ==================================
start_time = time.time()

image_dir_path = None
quality_ratio = 100
ignore_transparency_image = False
replace = False

# load config
image_dir_path_re = re.compile(r'image-path: *(.*)')
quality_ratio_re = re.compile(r'quality-ratio: *(\d*)')
ignore_transparency_re = re.compile(r'ignore-transparency-image: *(.*)')
replace_re = re.compile(r'replace: *(.*)')

conf_file_path = '.webp.conf'
if not exists(conf_file_path):
    exit(colorize(
        'Please create \'.webp.conf\' file, and add config:\nimage-path: /the/origin/image/path\nquality-ratio:[0~100](default is 100)\nignore-transparency-image: [true/false]\nreplace: [true/false]',
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

    replace_process = replace_re.search(line)
    if replace_process is not None:
        replace = replace_process.groups()[0] == 'true'
        continue

    exit(colorize('unknown config ' + line, fg=YELLOW))
conf_file.close()

if image_dir_path is None:
    exit(colorize(
        'Please create add config:\nimage-path: /the/origin/image/path', fg=RED))

command_prefix = '%s ' % resource_path('cwebp')
if quality_ratio >= 100:
    command_prefix += '-lossless -q 100 '
else:
    command_prefix += '-q ' + quality_ratio.__str__() + ' '

is_clean_env = False
if argv.__len__() > 1:
    value = argv[1]
    if value == '-withClean':
        if replace:
            exit(colorize(
                "can't clean the origin environment: can't withClean for replace mode, please remove 'replace' profile on .webp.conf or not execute with '-withClean' param",
                fg=RED))
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

RESULT_SUCCESS = 0
RESULT_FAILED = -1
RESULT_WEBP_LARGER = -2
RESULT_WITH_TRANSPARENCY = -3
RESULT_ALREADY_EXIST = -4

for subdir, dirs, files in os.walk(image_dir_path):
    for file_name in files:
        if file_name == '.DS_Store':
            continue
        if not file_name.endswith('.jpg') and not file_name.endswith('.png'):
            continue

        scan_file_count += 1
        input_file_path = join(subdir, file_name)
        output_file_name = file_name.rsplit('.', 1)[0] + '.webp'
        if replace:
            output_file_path = join(subdir, output_file_name)
        else:
            output_file_path = join(root, output_file_name)

        result, reduce_size = convert(input_file_path, file_name, output_file_path)
        if reduce_size > 0:
            all_reduce_size += reduce_size
            if result != RESULT_ALREADY_EXIST:
                valid_convert_file_count += 1
        elif RESULT_FAILED:
            failed_convert_count += 1
        elif RESULT_WEBP_LARGER:
            skip_file_count += 1
        elif result == RESULT_WITH_TRANSPARENCY:
            skip_transparency_file_count += 1

        if replace:
            if reduce_size > 0:
                remove(input_file_path)
        else:
            if result == RESULT_WITH_TRANSPARENCY:
                if not exists(transparency_image_path):
                    makedirs(transparency_image_path)
                copyfile(input_file_path, transparency_image_path + file_name)
            elif result == RESULT_FAILED:
                if not exists(convert_fail_path):
                    makedirs(convert_fail_path)
                copyfile(input_file_path, convert_fail_path + file_name)
            elif result == RESULT_WEBP_LARGER:
                if not exists(keep_origin_path):
                    makedirs(keep_origin_path)
                copyfile(input_file_path, keep_origin_path + file_name)

print '-----------------------------------------------'
print ' '
if replace:
    print colorize('Replace ' + valid_convert_file_count.__str__() + ' image files on ' + image_dir_path, fg=CYAN)
else:
    print colorize('All files handled on: ', fg=CYAN) + root

print colorize('Consume: ', fg=CYAN) + '%ss' % (time.time() - start_time)
print ' '
print colorize('Scan files count: ', fg=GREEN) + scan_file_count.__str__()
print colorize('Converted files count: ', fg=GREEN) + valid_convert_file_count.__str__()
print colorize('Reduce size: ', fg=GREEN) + human_bytes(all_reduce_size)
print colorize('Skip files(because convert failed) count: ',
               fg=GREEN) + failed_convert_count.__str__()
print colorize('Skip files(because the webp one is greater than origin one) count: ',
               fg=GREEN) + skip_file_count.__str__()
if skip_transparency_file_count > 0:
    print colorize('Skip files(because there is transparency) count: ',
                   fg=GREEN) + skip_transparency_file_count.__str__()
print ' '
print '-----------------------------------------------'
