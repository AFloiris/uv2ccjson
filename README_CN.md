# uv2ccjson

[中文](README_CN.md) | [English](README.md)

> 参考自: https://github.com/vankubo/uvConvertor  
> 感谢作者的开源贡献.

## 介绍

一个将 `keil5` 项目转化为 `compile_commands.json(ccjson)` 的 python脚本.  

因为直接使用 keil5 的 armcc 转化出来的 ccjson , clangd 对于部分选项无法识别,这里将 ccjson 中的 armcc 替换成了 arm-none-eabi-gcc,并使用 python 脚本将 keil5 项目转化为 ccjson.  

## 说明

该脚本的作用只在于将 keil5 的项目编译文件转化出 ccjson, 可以在 vscode 中使用 clangd 进行代码提示进行开发, 其他任何编译调试等功能还是在 keil5 中完成.

## 准备

> 1. 安装 python3.x 环境 https://www.python.org
> 2. 安装 arm-none-eabi-gcc (强烈推荐安装)(版本需要大于11) https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads


## 使用方法

0. 提示  
```sh
python uv2ccjson.py -h
```

1. 直接转化
效果与 uvConvertor 基本一致  
```sh
python uv2ccjson.py -f MDK-ARM/project.uvprojx
```

2. 使用 arm-none-eabi-gcc  
转化的 ccjson 会只保留宏定义和头文件, 使用 arm-none-eabi-gcc 尽可能减少 clangd 提示错误.
```sh
python uv2ccjson.py -f MDK-ARM/project.uvprojx --compile D:\Tools\arm-gnu-toolchain-14.2.rel1-mingw-w64-i686-arm-none-eabi\bin\arm-none-eabi-gcc.exe"
```

3. 添加 ccjson 中的编译选项  
```sh
python .\convert.py -f .\MDK-ARM\keil-test.uvprojx --compile D:\Tools\arm-gnu-toolchain-14.2.rel1-mingw-w64-i686-arm-none-eabi\bin\arm-none-eabi-gcc.exe --cflags "-g -o3"
```