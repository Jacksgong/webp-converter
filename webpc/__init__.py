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
import argparse
import os
import time
from os import makedirs, remove
from os.path import exists, join
from shutil import rmtree
from sys import exit

from webpc.converter import Converter, RESULT_ALREADY_EXIST, RESULT_FAILED, RESULT_WEBP_LARGER, RESULT_WITH_TRANSPARENCY
from webpc.helper import print_blue, resource_path, colorize, CYAN, GREEN, human_bytes, copyfile_safe, handle_home_case, \
    print_warn

__version__ = '4.1.0'
__author__ = 'JacksGong'

print("-------------------------------------------------------")
print("               Webp Converter v" + __version__)
print("")
print("Thanks for using okcat! Now, the doc is available on: ")
print_blue("      https://github.com/Jacksgong/webp-converter")
print("")
print("                      Have Fun!")
print("-------------------------------------------------------")


def main():
    default_output_directory = "%s/%s" % (os.getcwd(), 'webp-converted/')
    parser = argparse.ArgumentParser(description='Converter and analytics batch of images(png/jpg) to webp')
    parser.add_argument('image_directory', nargs='*', default=[os.getcwd()], help='Origin images directory path')
    parser.add_argument('-q', '--quality-ratio', dest='quality_ratio', type=int, default=100,
                        help='Quality ratio, between 0 to 100, 100 is lossless, 0 is highest compression ratio, default value is 100')
    parser.add_argument('-o', '--output-directory', dest='output_directory',
                        default=default_output_directory,
                        help='the output directory of converted path, default value is ./webp-converted/')
    parser.add_argument('--ignore-transparency-image', dest='ignore_transparency_image', action='store_true',
                        help='Whether need to ignore images which has transparency pixel on it, default value is false')
    parser.add_argument('--r', dest='replace_origin', action='store_true',
                        help='Whether replace the origin images files directly or not, default value is false')
    parser.add_argument('--c', dest='clear_env', action='store_true',
                        help='Whether need to clean the output directory before convert images, default value is false')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Whether need to print debug message, default value is false')
    parser.add_argument('--ignore-filename-match', dest='ignore_filename_match', default='',
                        help='ignore file when the name contain the provide value(such as .9)')

    args = parser.parse_args()

    start_time = time.time()

    input_directory = handle_home_case(args.image_directory[0])
    output_directory = handle_home_case(args.output_directory)
    quality_ratio = args.quality_ratio
    ignore_transparency_image = args.ignore_transparency_image
    replace_origin = args.replace_origin
    clean_env = args.clear_env
    is_debug = args.debug
    ignore_filename_match = args.ignore_filename_match

    if replace_origin and (clean_env or output_directory != default_output_directory):
        exit(
            "the --c and -o can't company with --r, because of --r means you need to store the converted images on the origin "
            "images directory and replace the origin images directly, and -o is means you want to store the converted images "
            "on some different directory, and --c is means you want to clear the output directory you provided with -o before"
            " convert.")

    if replace_origin:
        print('origin images will be replace with webp images on ' + input_directory)
    else:
        print('origin images on ' + input_directory + ' will be converted to ' + output_directory)

    command_prefix = '%s ' % resource_path('cwebp')
    if quality_ratio >= 100:
        command_prefix += '-lossless -q 100 '
    else:
        command_prefix += '-q ' + quality_ratio.__str__() + ' '

    keep_origin_path = output_directory + 'origin/'
    convert_fail_path = output_directory + 'failed/'
    transparency_image_path = output_directory + 'transparency/'
    swap_webp_path = join(output_directory, 'swap.webp') if not replace_origin else join(input_directory, 'swap.webp')

    if clean_env and exists(output_directory):
        rmtree(output_directory)
        print("clear all env on " + output_directory)

    if not replace_origin and not exists(output_directory):
        makedirs(output_directory)

    if exists(swap_webp_path):
        remove(swap_webp_path)

    output_data = OutputData()
    try:
        loop(
            input_directory=input_directory,
            output_directory=output_directory,
            swap_webp_path=swap_webp_path,
            transparency_image_path=transparency_image_path,
            quality_ratio=quality_ratio,
            convert_fail_path=convert_fail_path,
            keep_origin_path=keep_origin_path,
            ignore_transparency_image=ignore_transparency_image,
            is_debug=is_debug,
            replace_origin=replace_origin,
            output_data=output_data,
            ignore_filename_match=ignore_filename_match
        )
    except KeyboardInterrupt:
        print('')
        print('INTERRUPT BY USER.')
        if exists(swap_webp_path):
            remove(swap_webp_path)
        pass

    output_data.dump(
        replace_origin=replace_origin,
        input_directory=input_directory,
        output_directory=output_directory,
        start_time=start_time,
        ignore_filename_match=ignore_filename_match
    )


class OutputData:
    all_reduce_size = 0
    valid_convert_file_count = 0
    failed_convert_count = 0
    scan_file_count = 0
    skip_file_count = 0
    skip_transparency_file_count = 0
    skip_ignore_match_name_file_count = 0

    def __init__(self):
        pass

    def dump(self, replace_origin, input_directory, output_directory, start_time, ignore_filename_match):
        print('-----------------------------------------------')
        print(' ')
        if replace_origin:
            colorize('Replace %s image files on %s' % (self.valid_convert_file_count, input_directory),
                     fg=CYAN)
        else:
            print(get_result('All files handled on: ', output_directory, fg=CYAN))

        print(get_result('Consume: ', (time.time() - start_time), _format='%s%.3fs', fg=CYAN))
        print(' ')
        print(get_result('Scan files count: ', self.scan_file_count))
        print(get_result('Converted files count: ', self.valid_convert_file_count))
        print(get_result('Reduce size: ', human_bytes(self.all_reduce_size)))
        print(get_result('Skip files(because convert failed) count: ', self.failed_convert_count))
        print(get_result('Skip files(because the webp one is greater than origin one) count: ', self.skip_file_count))
        if self.skip_transparency_file_count > 0:
            print(get_result('Skip files(because there is transparency) count: ', self.skip_transparency_file_count))
        if self.skip_ignore_match_name_file_count > 0:
            print(get_result('Skip files(because their name contain %s) count: ' % ignore_filename_match,
                             self.skip_ignore_match_name_file_count))
        print (' ')
        print ('-----------------------------------------------')


def get_result(title, message, _format='%s%s', fg=GREEN):
    return _format % (colorize(title, fg=fg), message)


def loop(input_directory, output_directory, swap_webp_path, transparency_image_path, quality_ratio, convert_fail_path,
         keep_origin_path, ignore_transparency_image, is_debug,
         replace_origin, output_data, ignore_filename_match):
    handler = Converter(swap_webp_path, quality_ratio)
    for subdir, dirs, files in os.walk(input_directory):
        for file_name in files:
            if file_name == '.DS_Store':
                continue
            if ignore_filename_match != '' and file_name.__contains__(ignore_filename_match):
                if is_debug:
                    print('ignore %s because it contain %s' % (file_name, ignore_filename_match))
                output_data.skip_ignore_match_name_file_count += 1
                continue
            if not file_name.endswith('.jpg') and not file_name.endswith('.png'):
                continue

            if output_directory in subdir:
                continue

            output_data.scan_file_count += 1
            input_file_path = join(subdir, file_name)
            output_file_name = file_name.rsplit('.', 1)[0] + '.webp'
            if replace_origin:
                output_file_path = join(subdir, output_file_name)
            else:
                output_file_path = join(output_directory, output_file_name)

            result, reduce_size = handler.convert(ignore_transparency_image, input_file_path, file_name,
                                                  output_file_path, is_debug)
            if reduce_size > 0:
                output_data.all_reduce_size += reduce_size
                if result != RESULT_ALREADY_EXIST:
                    output_data.valid_convert_file_count += 1
            elif result == RESULT_FAILED:
                output_data.failed_convert_count += 1
            elif result == RESULT_WEBP_LARGER:
                output_data.skip_file_count += 1
            elif result == RESULT_WITH_TRANSPARENCY:
                output_data.skip_transparency_file_count += 1

            if replace_origin:
                if reduce_size > 0:
                    remove(input_file_path)
            else:
                if result == RESULT_WITH_TRANSPARENCY:
                    copyfile_safe(input_file_path, transparency_image_path, file_name)
                elif result == RESULT_FAILED:
                    copyfile_safe(input_file_path, convert_fail_path, file_name)
                elif result == RESULT_WEBP_LARGER:
                    copyfile_safe(input_file_path, keep_origin_path, file_name)
