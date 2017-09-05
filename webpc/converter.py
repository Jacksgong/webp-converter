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
import subprocess
import os
from os import remove, rename
from os.path import exists

from helper import size_diff, print_process, resource_path

RESULT_SUCCESS = 0
RESULT_FAILED = -1
RESULT_WEBP_LARGER = -2
RESULT_WITH_TRANSPARENCY = -3
RESULT_ALREADY_EXIST = -4

FNULL = open(os.devnull, 'w')


class Converter:
    swap_webp_path = None
    command_prefix = list()

    def __init__(self, swap_webp_path, quality_ratio):
        self.swap_webp_path = swap_webp_path

        command = list()
        command.append(resource_path("cwebp"))
        # command_prefix = '%s ' % resource_path('cwebp')
        if quality_ratio >= 100:
            command.append("-lossless")
            command.extend(['-q', '100'])
            # command_prefix += '-lossless -q 100 '
        else:
            command.extend(['-q', quality_ratio.__str__()])
            # command_prefix += '-q ' + quality_ratio.__str__() + ' '

        self.command_prefix = command

    def convert(self, ignore_transparency_img, image_file_path, image_file_name, webp_file_path, is_debug):
        # whether has already converted
        if exists(webp_file_path):
            # has already converted!
            _reduce_size = size_diff(image_file_path, webp_file_path)

            if _reduce_size < 0:
                remove(webp_file_path)
                print_process(
                    image_file_name + ' has already converted, but it larger than origin-image: ' + _reduce_size.__str__() + ' so, remove it and re-convert it!')
            else:
                print_process(image_file_name + ' has already converted! reduce: ' + _reduce_size.__str__())
                return RESULT_ALREADY_EXIST, _reduce_size

        # transparency
        if ignore_transparency_img and image_file_name.endswith('.png'):
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
                        print_process(
                            'NOT convert ' + image_file_name + ' because there is alpha[' + pixel.__str__() + ']')
                        return RESULT_WITH_TRANSPARENCY, 0

        print_process('convert for ' + image_file_path)

        swap_webp_path = self.swap_webp_path

        command = list(self.command_prefix)
        command.append(image_file_path)
        command.extend(['-o', swap_webp_path])

        if is_debug:
            subprocess.Popen(command).communicate()
            print command.__str__()
        else:
            subprocess.Popen(command, stdout=FNULL, stderr=subprocess.STDOUT).communicate()

        # print command_prefix + image_file_path + ' -o ' + swap_webp_path
        # system(command_prefix + image_file_path + ' -o ' + swap_webp_path)
        # whether convert failed
        if not exists(swap_webp_path):
            # convert failed!
            print_process("NOT convert " + image_file_name + ' because convert failed!')
            return RESULT_FAILED, 0

        _reduce_size = size_diff(image_file_path, swap_webp_path)
        if _reduce_size < 0:
            # invalid convert
            print_process(
                'NOT convert ' + image_file_name + ' because the webp one is larger: ' + (-_reduce_size).__str__())
            remove(swap_webp_path)
            return RESULT_WEBP_LARGER, 0

        print_process('convert ' + image_file_name + ' and reduce size: ' + _reduce_size.__str__())
        rename(swap_webp_path, webp_file_path)
        if exists(swap_webp_path): remove(swap_webp_path)
        return RESULT_SUCCESS, _reduce_size
