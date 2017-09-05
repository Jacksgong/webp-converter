# Webp Converter and Scanner

An powerful webp batch converter and differ analytics

> [中文文档](https://github.com/Jacksgong/webp-converter/blob/master/README-zh.md)

You can use this tool to converter batch images(png/jpg) to webp and output size changes.

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/webp-converter.png)


## Purpose

1. Convert batch images from PNG/JPG format to Webp format
2. WILL NOT convert images if its webp one is larger than origin one automatically(the origin one will be copied to `[output-directory]/origin/` directory)
3. WILL NOT convert images if it is failed to convert to webp one automatically(the origin image of failed one will be copied to `[output-directory]/failed` directory)
4. You can ignore all images which has transparency pixel if you want with `--ignore-transparency-image` config(the origin image of has-transparency-image will be copied to `/webp-converted/transparency` directory)
5. Output convert result, like how much size reduces, how many files skip convert, etc...
6. You can replace the images with converted-webp image automatically if you want with `replace: true` config

## Install

```shell
brew install webp
pip install webp-converter
```

## Use

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/help.png)

#### Example

If you just want to convert all images on the current files when it can be smaller after converted and **replace** the origin one:

```shell
webpc --r
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-1.png)


If you just want to convert all images on the current folder and with **quality-ratio** to `70` and **output** to `~/Downloads/test-converted` when it can be smaller after converted:

```shell
webpc -q=70 -o=~/Downloads/test-converted/
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-2.png)


If you just want to convert all images on the current folder and with **clean** the `webp-converted` folder if it exist and with **quality-ratio** to `95` and **output** to `./webp-converted` and **ignore images when it has transparency** on it when it can be smaller after converted:

```shell
webpc --c --ignore-transparency-image -q=95
```
![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-3.png)

If you want to convert all **images on** `~/Downloads/img/test` folder and **output** converted result to `~/Downloads/test-converted` folder and only converted origin images when it isn't has **same name** `.webp` file on `~/Downloads/test-converted` folder(just not with `--c` argument) when it can be smaller after converted:


```shell
webpc -o=~/Downloads/test-converted/ ~/Downloads/img/test
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-4.png)

## License

```
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
```
