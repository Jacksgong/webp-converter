# Webp转换与扫描

![](https://img.shields.io/badge/webp-batch%20converter-orange.svg)
![](https://img.shields.io/badge/webp-batch%20analytics-orange.svg)
![](https://img.shields.io/badge/license-Apache2-blue.svg)
[![](https://img.shields.io/badge/readme-English-blue.svg)](https://github.com/Jacksgong/webp-converter)
[![](https://img.shields.io/badge/readme-中文-blue.svg)](https://github.com/Jacksgong/webp-converter/blob/master/README-zh.md)
[![](https://img.shields.io/badge/pip-v4.1.0%20webp--converter-yellow.svg)](https://pypi.python.org/pypi/webp-converter)

Webp批量定向转换与结果分析工具。

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/webp-converter.png)

## 目的

1. 批量转换PNG/JPG到Webp文件
2. 自动忽略转换以后会变大的图片(会拷贝原图到`[output-directory]/origin/`目录)
3. 自动忽略转换失败的图片(会拷贝原图到`[output-directory]/failed/`目录)
4. 如果你需要可以通过参数`--ignore-transparency-image: true`来不转换带有透明像素点的图片(会拷贝原图到`[output-directory]/transparency`目录)
5. 输出转换结果，转换完后输出结果
6. 如果你需要可以通过参数`--r`来自动用转换后的webp替换原图

## 安装

```shell
brew install webp
pip install webp-converter
```

## 使用

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/help.png)

#### 案例

如果你想要转换当前目录下的所有图片并且转换以后图片会变小的情况下，转换后的图片 **直接替换** 原来的图片:

```shell
webpc --r
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-1.png)

如果你想要转换当前目录下的所有图片，使用`70`的 **质量**，并且 **输出** 目录指定在`~/Downloads/test-converted` 当转换后的图片会变小的情况下:

```shell
webpc -q=70 -o=~/Downloads/test-converted/
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-2.png)

如果你想要转换当前目录下的所有图片，并且 **清除** `webp-converted`目录下的所有内容，并且将 **质量** 指定为 `95`，并且 **输出** 目录指定为 `./webp-converted`，并且 **忽略存在透明度的图片**，在转换后会变小的情况下:

```shell
webpc --c --ignore-transparency-image -q=95
```
![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-3.png)

如果你想要转换过程中忽略一些包含特殊字符的文件，可以通过`--ignore-filename-match`来做到，以下案例就是忽略文件名包含`.9`的文件:

```shell
webpc --r --ignore-filename-match='.9'
```

如果你想要转换所有 **存储在** `~/Downloads/img/test`中的图片，并且 **输出** 目录指定为 `~/Downloads/test-converted`，并且仅仅转换在输出目录中 **不存在** 的图片，在转换后会变小的情况下:

```shell
webpc -o=~/Downloads/test-converted/ ~/Downloads/img/test
```

![](https://github.com/Jacksgong/webp-converter/raw/master/arts/demo-4.png)

## 我的终端的风格配置

如果你想要适配和上面截图一样的终端风格，非常简单:

- 首先，请使用[powerlevel9k](https://github.com/bhilburn/powerlevel9k)主题(正如Powerlevel9k文档提到的安装Powerlevel9k主题，并且安装Powerline字体).
- 其次，请配置[iTerm2-Neutron](https://github.com/Ch4s3/iTerm2-Neutron)色系.
- 最后, 请配置ini的shell(如果你使用的是zsh，只需要添加下列代码到`~/.zshrc`文件中):
```
POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(dir vcs)
POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status time)
POWERLEVEL9K_TIME_FORMAT="%D{%H:%M:%S}"
POWERLEVEL9K_NODE_VERSION_BACKGROUND='022'
POWERLEVEL9K_SHORTEN_DIR_LENGTH=2
```

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
