# APK Optimize

> APK包优化自动化脚本

## Webp转换与扫描

> 脚本: `webp_converter.py`

#### 目的

1. 批量转换PNG/JPG到Webp文件
2. 自动忽略转换以后会变大的图片(会拷贝原图到`/webp-converted/origin/`目录)
3. 自动忽略转换失败的图片(会拷贝原图到`/webp-converted/failed/`目录)
4. 输出转换结果，转换完后输出结果，如: `reduce size: 2838335 from file count: 4807 failed convert file count: 3`

#### 配置

> 可以参考`.webp.conf.template`文件

在当前目录创建配置文件`.webp.conf`并输入以下配置:

```
# 原图片的路径
image-path: /the/origin/image/path
# 保持的质量率，100为无损压缩, 0为最高压缩率
quality-ratio: 100
```

#### 执行

```
python webp_converter.py
```

默认是会断点续转，也就是转换了一半，中断了以后，下次再执行脚本会自动忽略已经转换过的(但是依然会记录统计)。
如果需要清理本地环境，从头开始转换，带上`-withClean`参数:

```
python webp_converter.py -withClean
```
