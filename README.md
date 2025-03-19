# uv2ccjson

> Referenced from: https://github.com/vankubo/uvConvertor  
> Thank the author for their open-source contribution.

## Introduction

A Python script that converts a `keil5` project into `compile_commands.json (ccjson)`.

Since the ccjson generated directly using keil5's armcc cannot be fully recognized by clangd for some options, this script replaces armcc with arm-none-eabi-gcc in the ccjson and uses a Python script to convert a keil5 project into ccjson.

## Explanation

The purpose of this script is solely to convert the compilation files of a keil5 project into ccjson, which can be used with clangd for code hints during development in vscode. Any other compilation and debugging functions should still be performed in keil5.

## Preparation

> 1. Install python3.x environment https://www.python.org
> 2. Install arm-none-eabi-gcc (strongly recommended) (version needs to be greater than 11) https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads

## Usage

0. Hint  
```sh
python uv2ccjson.py -h
```

1. Direct conversion  
The effect is basically the same as uvConvertor.
```sh
python uv2ccjson.py -f MDK-ARM/project.uvprojx
```

2. Using  arm-none-eabi-gcc  
The generated ccjson will only retain macro definitions and header files. Using arm-none-eabi-gcc will try to minimize errors in clangd hints.
```sh
python uv2ccjson.py -f MDK-ARM/project.uvprojx --compile D:\Tools\arm-gnu-toolchain-14.2.rel1-mingw-w64-i686-arm-none-eabi\bin\arm-none-eabi-gcc.exe"
```

3. Adding compilation options to ccjson  
```sh
python .\convert.py -f .\MDK-ARM\keil-test.uvprojx --compile D:\Tools\arm-gnu-toolchain-14.2.rel1-mingw-w64-i686-arm-none-eabi\bin\arm-none-eabi-gcc.exe --cflags "-g -o3"
```