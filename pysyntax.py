import re

from pylex import Lexer, write_string_to_file
from pylex import TokenType
from pylex import read_file_to_string
from pylex import filterComment
from pyparser import Parser, FetchToken, parse_program, getPaserTree

# 根据语法树生成可执行文件
def generate_python_code(node, lvl=0):
    code = ""
    # 终结符node.value为token 非终结符为None
    if node.value!=None:
        if str(node.value.value)=="{" or str(node.value.value)=="}":
            return code
        elif node.value.tokenType.value == "字符串":
            code += "\"" + node.value.value + "\""
        elif node.value.tokenType.value == "常数":
            # token创建时所以数字均为float 检查是否小数点后全为0
            if node.value.value.is_integer():
                code += str(int(node.value.value))  # 将其转为整数
            else:
                code += str(node.value.value)  # 保持为浮点数
        else:
            code += str(node.value.value)
        return code
    else:
        # identifier_stmt后可能为函数调用
        if node.type == "identifier_stmt":
            turtle_fun_syntax_anlysis(node)
        # 每句statement根据block层数进行缩进
        if node.type == "statement":
            for child in node.children:
                if child:
                    # lvl = 0 没有缩进
                    code += lvl*"    "+ generate_python_code(child, lvl)
        elif node.type == "block":
            for child in node.children:
                if child:
                    code += generate_python_code(child, lvl+1)
        elif node.type == "import_stmt":
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
        elif node.type == "if_stmt":
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
            code += generate_python_code(node.children[2], lvl)
            code += "\n"
            code += generate_python_code(node.children[3], lvl)
            code += generate_python_code(node.children[4], lvl)
        elif node.type == "else_block":
            code += lvl*"    "+generate_python_code(node.children[0], lvl)
            code += generate_python_code(node.children[1], lvl)
            code += "\n"
            code += generate_python_code(node.children[2], lvl)
        elif node.type == "for_stmt":
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
            code += " "
            code += generate_python_code(node.children[2], lvl)
            code += " "
            code += generate_python_code(node.children[3], lvl)
            code += generate_python_code(node.children[4], lvl)
            code += "\n"
            code += generate_python_code(node.children[5], lvl)
        elif node.type == "while_stmt":
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
            code += "\n"
            code += generate_python_code(node.children[1], lvl)
        elif node.type == "function_def":
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
            code += generate_python_code(node.children[2], lvl)
            code += generate_python_code(node.children[3], lvl)
            code += generate_python_code(node.children[4], lvl)
            code += generate_python_code(node.children[5], lvl)
            code += "\n"
            code += generate_python_code(node.children[6], lvl)
        else:
            for child in node.children:
                if child:
                    code += generate_python_code(child, lvl)
    return code


def turtle_fun_syntax_anlysis(node):
    # 处理对象.函数()调用的可能出现的错误
    # node.print_tree()
    for t in turtle_id:
        is_fun = is_function_call(node)
        node_father = node
        node = node.children[0]
        if t.value.value==node.value.value and is_fun:
            extracted_args = node_father.extract_arguments()
            fun_str = ""
            for arg in extracted_args:
                fun_str += str(arg.value.value)
            check_turtle_function_syntax(fun_str, t.value.value)
        elif t.value.value==node.value.value and not is_fun:
            print("Syntax Fualt: 非法的标识符命名！"+node.value.value+" 与 import包名 "+t.value.value+" 冲突")
        elif t.value.value!=node.value.value and is_fun:
            print("Syntax Fualt: 未import的对象名！" + node.value.value)

    # print(node.children[0].value.value)
    # print(turtle_id[0].value.value)

def is_function_call(node):
    if node!=None:
        if node.type=="DOT":
            return True
        # 否则递归检查所有子节点
        else:
            for child in node.children:
                if is_function_call(child):  # 如果任何子节点含有 'DOT'
                    return True
    return False  # 如果没有找到 'DOT' 类型的节点

def check_turtle_function_syntax(call_str, t):
    # 解析函数名和参数
    match = re.match(t+"\.(\w+)\((.*)\)", call_str)


    function_name, arguments_str = match.groups()
    # 检查函数是否为我们需要验证的函数
    if function_name in ['setpos', 'towards', 'distance']:
        # 尝试解析参数，假设参数为两个数字或一个元组
        try:
            # 从字符串转换参数为实际的Python表达式
            arguments = eval(arguments_str)
            if isinstance(arguments, tuple) and len(arguments) == 2:
                # 参数是一个元组，期望x为元组，y为空
                if isinstance(arguments[0], (int, float)) and isinstance(arguments[1], (int, float)):
                    pass
                else:
                    print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) x参数为元组时，y应当为空")
            elif isinstance(arguments, (tuple)) and len(arguments) == 1:
                # 参数是单个元素的列表或元组，错误情形
                print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) x参数为元组时，元组应当包含2个number")
            else:
                # 参数是两个分开的数字
                if not isinstance(arguments, (list, tuple)) or len(arguments) != 2:
                    print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) 参数应当为2个number")
                elif not all(isinstance(arg, (int, float)) for arg in arguments):
                    print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) 有参数不是number")
                else:
                    pass
        except Exception as e:
            print(f"Error parsing arguments: {e}")
    elif function_name in ['color']:
        try:
            # 解析参数
            arguments = eval(arguments_str)

            # 根据参数类型和数量分情况处理
            if isinstance(arguments, str):
                # 单个字符串参数，正常，无需额外动作
                pass
            elif isinstance(arguments, tuple):
                if len(arguments) == 3:
                    # 单个RGB元组
                    if any(color > 1.0 for color in arguments):
                        print(f"Syntax Fault: 值错误（Value Error）{function_name}(r, g, b) RGB的值不应大于1.0")
                elif len(arguments) == 2 and all(isinstance(sub, tuple) for sub in arguments):
                    # 两个RGB元组
                    if any(color > 1.0 for tuple_color in arguments for color in tuple_color):
                        print(
                            f"Syntax Fault: 值错误（Value Error）{function_name}((r1, g1, b1), (r2, g2, b2)) RGB的值不应大于1.0")
                else:
                    print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用不正确的RGB元组格式")
            elif isinstance(arguments, list):
                if len(arguments) == 3 and all(isinstance(color, (int, float)) for color in arguments):
                    # 分开的三个RGB分量
                    if any(color > 1.0 for color in arguments):
                        print(f"Syntax Fault: 值错误（Value Error）{function_name}(r, g, b) RGB的值不应大于1.0")
                elif len(arguments) == 2 and all(isinstance(color, str) for color in arguments):
                    # 两个颜色字符串，正常，无需额外动作
                    pass
                else:
                    print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用不正确的参数组合或类型")
            elif not arguments_str:  # 检查是否没有参数
                # 无参数调用
                pass
            else:
                print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用了不支持的参数类型或格式")
        except Exception as e:
            pass


def analyse_tree():
    str = read_file_to_string("test.py")
    str = filterComment(str)
    write_string_to_file(str, "test_filter.py")
    tokenlist = Lexer(str)
    tokenIter = iter(tokenlist)

    FetchToken()
    return parse_program()

def analyse_syntax():
    global turtle_id
    tree = getPaserTree()
    if len(tree.imported_names)<1:
        print("Syntax Fault: 没有引入任何包！")
    else:
        turtle_id = tree.imported_names
    str = generate_python_code(tree)
    write_final_file(str, "test_final.py")

def write_final_file(content, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError:
        return "文件写入失败。"

analyse_syntax()