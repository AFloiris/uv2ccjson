import argparse
import os
import xml.etree.ElementTree as ET
import re
import json

uvprojx_dir = ""
uvprojx_file_path = ""
c_compiler_path = ""
use_arm_compiler = False
append_options = ""

def main():

    global uvprojx_dir
    global uvprojx_file_path
    global c_compiler_path
    global use_arm_compiler
    global append_options

    parser = argparse.ArgumentParser(description="parse .uvprojx file and generate compile_commands.json file")

    parser.add_argument(
        "-f", "--file",
        required=True,
        help=".uvprojx file path"
    )

    parser.add_argument(
        "--compile",
        default="",
        help="arm-none-eabi-gcc path (because armcc.exe is not supported by clangd)"
    )

    parser.add_argument(
        "--cflags",
        default="",
        help="append cflags to compile_command.json"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.isfile(args.file):
        print(f"Error: The file '{args.file}' does not exist.")
        return
    
    uvprojx_file_path = args.file
    # uvprojx_file 所在的全路径(不包含文件名)
    uvprojx_dir = os.path.dirname(os.path.abspath(uvprojx_file_path))
    uvprojx_dir = uvprojx_dir.replace("\\", "/")

    # 如果指定了编译器路径，则判断路径是否有效
    if args.compile:
        if not os.path.isfile(args.compile):
            print(f"Error: The file '{args.compile}' does not exist.")
            return
        c_compiler_path = args.compile
        c_compiler_path = c_compiler_path.replace("\\", "/")
        use_arm_compiler = True
    else:
        print("Warning: armcc.exe is not supported by clangd, please specify the arm-none-eabi-gcc path.")

    if args.cflags:
        append_options = args.cflags


    # 调用处理函数
    parse_uvprojx()

def parse_uvprojx():

    global uvprojx_dir
    global uvprojx_file_path
    global c_compiler_path
    global use_arm_compiler
    global append_options

    # 读取.uvprojx 文件内容
    print(f"Parse.uvprojx file: {uvprojx_file_path}")
    tree = ET.parse(uvprojx_file_path)
    root = tree.getroot()

    # TargetName
    tragetname_elm = root.find("Targets/Target/TargetName")
    if tragetname_elm is None:
        print("Error: Cannot find TargetName element in.uvprojx file.")
        exit(1)

    # 输出目录
    outputdir_elm = root.find("Targets/Target/TargetOption/TargetCommonOption/OutputDirectory")
    if outputdir_elm is None:
        print("Error: Cannot find OutputDirectory element in.uvprojx file.")
        exit(1)

    # 输出名字
    outputname_elm = root.find("Targets/Target/TargetOption/TargetCommonOption/OutputName")
    if outputname_elm is None:
        print("Error: Cannot find OutputName element in.uvprojx file.")
        exit(1)

    targetname = tragetname_elm.text
    outputdir = os.path.join(uvprojx_dir, outputdir_elm.text)
    outputdir = outputdir.replace("\\", "/")
    outputname = outputname_elm.text

    if not use_arm_compiler:
        c_compiler_path = parse_armcc(outputdir, outputname)

    # dep_file
    dep_file = os.path.join(outputdir, os.path.basename(uvprojx_file_path).replace(".uvprojx", f"_{targetname}.dep"))
    if not os.path.isfile(dep_file):
        print(f"Error: Cannot find dependency file: {dep_file}")
        exit(1)
    
    file_and_options = parse_compile_options(dep_file)
    ccjson_str = create_compile_commands_json(file_and_options)

    # 输出到文件
    ccjson_file = os.path.join("./", "compile_commands.json")
    with open(ccjson_file, "w") as file:
        file.write(ccjson_str)

    print(f"Output compile_commands.json file: {ccjson_file}")

def parse_armcc(outputdir, outputname):
    # build_log_file
    build_log_file = os.path.join(outputdir, outputname + ".build_log.htm")
    if not os.path.isfile(build_log_file):
        print(f"Error: Cannot find build log file: {build_log_file}")
        exit(1)

    # 从 build_log_file 中解析出 ToolChain Path 和 C Compiler, 拼接成完整路径
    # 正则表达式匹配工具链路径和C编译器名称
    toolchain_pattern = re.compile(r"Toolchain Path:\s*(.*)")
    c_compiler_pattern = re.compile(r"C Compiler:\s*(\S+).*")

    with open(build_log_file, "r") as file:
        for line in file:
            # 匹配工具链路径
            toolchain_match = toolchain_pattern.match(line)
            if toolchain_match:
                toolchain_path = toolchain_match.group(1).strip()

            # 匹配C编译器名称
            c_compiler_match = c_compiler_pattern.match(line)
            if c_compiler_match:
                c_compiler_name = c_compiler_match.group(1).strip()

    # 拼接C编译器路径
    if toolchain_path and c_compiler_name:
        armcc_compiler_path = f"{toolchain_path}/{c_compiler_name}"
    else:
        print("Failed to extract toolchain path or C compiler name.")
        exit(1)

    # 转化为 '/' 正斜杠
    armcc_compiler_path = armcc_compiler_path.replace("\\", "/")
    return armcc_compiler_path

def parse_compile_options(dep_file_path):

    with open(dep_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 正则表达式匹配 F (file)(address)(options)，支持跨行
    pattern = re.compile(r"F \((.*?)\)\((.*?)\)\((.*?)\)", re.DOTALL)

    results = []
    for match in pattern.finditer(content):
        file_part = match.group(1).strip()
        options_part = match.group(3).strip()

        # 统一替换反斜杠为斜杠
        file_path = file_part.replace('\\', '/')
        compile_options = options_part.replace('\\', '/')

        # 合并空白字符（包括换行、多空格等）
        compile_options = ' '.join(compile_options.split())
        # 将-I 后面的空格去掉
        compile_options = re.sub(r'-I\s+', '-I', compile_options)

        if use_arm_compiler:
            # 过滤compile_options,只保留-D和-I开头的参数(TODO: 因为使用arm-gcc 部分参数可能不适用 所以进行了过滤)
            compile_options = [opt for opt in compile_options.split() if opt.startswith('-D') or opt.startswith('-I')]
            compile_options = " ".join(compile_options)

        results.append((file_path, compile_options))

    return results

def create_compile_commands_json(commands):
    '''
    输出格式
    [
     {
         "directory": uvprojx_dir,
         "command": "c_compiler_path commands.options"
         "file": "command.file"
     }
    ]
    '''

    ccjson = []
    for file, options in commands:
        item = {
            "directory": uvprojx_dir,
            "command": f"{c_compiler_path} {options} {append_options}",
            "file": file
        }
        ccjson.append(item)

    return json.dumps(ccjson, indent=4)

if __name__ == "__main__":
    main()