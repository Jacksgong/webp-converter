# Webp Converter and Scaner

> Script: [webp_converter.py](https://github.com/Jacksgong/webp-converter/blob/master/webp_converter.py)

> [中文文档](https://github.com/Jacksgong/webp-converter/blob/master/README-zh.md)

You can use this tool to converter batch images(png/jpg) to webp and output size changes.

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/webp-converter.png)


## Purpose

1. Convert batch images from PNG/JPG format to Webp format
2. WILL NOT convert images if its webp one is larger than origin one automatically(the origin one will be copied to `/webp-converted/origin/` directory)
3. WILL NOT convert images if it is failed to convert to webp one automatically(the origin image of failed one will be copied to `/webp-converted/failed` directory)
4. You can ignore all images which has transparency pixel if you want with `ignore-transparency-image: true` config(the origin image of has-transparency-image will be copied to `/webp-converted/transparency` directory)
5. Output convert result, like how much size reduces, how many files skip convert, etc...
6. You can replace the images with converted-webp image automatically if you want with `replace: true` config

## Configure

> Please refer to [.webp.conf.template](https://github.com/Jacksgong/webp-converter/blob/master/.webp.conf.template) file.

Please feel free to create the file with name `.webp.conf` on the current directory, and input following configuration:

```
# Origin images directory path
image-path: /the/origin/image/path
# Quality ratio, between 0 to 100, 100 is lossless, 0 is highest compression ratio
quality-ratio: 100
# Whether need to ignore images which has transparency pixel on it (If you set true, please make sure has already installed 'Pillow' on your Env(pip install Pillow)
ignore-transparency-image: [true/false]
# Whether replace the image-path files directly or not
replace: [true/false]
```

## Use

```
python python webp_converter.py
```

As default we will ignore some file has been converted on the `webp-converted` folder, if you want to clean it and restart convert all images, just add `-withClean` argument:

```
python webp_converter.py -withClean
```

## License

```
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
```
