#!/usr/bin/python -u

"""
Copyright 2017, JacksGong(https://jacksgong.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
from os import makedirs, environ
from os.path import getsize, join, exists
from shutil import copyfile

import re

RESET = '\033[0m'
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

NO_HOME_PATH = re.compile(r'~/(.*)')
HOME_PATH = environ['HOME']


# get the home case path
def handle_home_case(path):
    path = path.strip()
    if path.startswith('~/'):
        path = HOME_PATH + '/' + NO_HOME_PATH.match(path).groups()[0]
    return path


def print_blue(msg):
    print(colorize(msg, fg=BLUE))


def print_warn(msg):
    print(colorize(msg, fg=YELLOW))


def termcolor(fg=None, bg=None):
    codes = []
    if fg is not None: codes.append('3%d' % fg)
    if bg is not None: codes.append('10%d' % bg)
    return '\033[%sm' % ';'.join(codes) if codes else ''


def colorize(message, fg=None, bg=None):
    return termcolor(fg, bg) + message + RESET


def print_process(message):
    print(colorize(message, fg=YELLOW))


def size_diff(left, right):
    return getsize(left) - getsize(right)


def human_bytes(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string"""
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
    # noinspection PyProtectedMember
    return join(sys._MEIPASS, relative_path) if hasattr(sys, '_MEIPASS') else relative_path


def copyfile_safe(input_file_path, target_file_dir, file_name):
    if not exists(target_file_dir):
        makedirs(target_file_dir)

    target_file_path = target_file_dir + file_name
    if exists(target_file_path):
        print_warn(
            'we will not copy file[%s] because of there is a another file with the same name has been handled.' % input_file_path)
    else:
        copyfile(input_file_path, target_file_dir + file_name)
