from enum import Enum


class TokenType(Enum):
    # TokenType.PLUS.value ->+
    # TokenType.PLUS.name ->PLUS
    IDENTIFIER = "标识符"
    NUMBER = "常数"
    STRING = "字符串"
    # 操作符
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    DIVIDE = '/'
    AUGASSIGN = '增量赋值'
    ASSIGN = '='
    SEMICOLON = ';'
    COLON = ':'
    POWER = '**'
    COMMA = ','
    # 括号和分隔符
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    LBRACKET = '['
    RBRACKET = ']'
    DOT = '.'
    # 关键字
    DEF = 'def'
    IF = 'if'
    ELSE = 'else'
    ELIF = 'elif'
    FOR = 'for'
    IN = 'in'
    WHILE = 'while'
    BREAK = 'break'
    CONTINUE = 'continue'
    RETURN = 'return'
    PASS = 'pass'
    IMPORT = 'import'
    AS = 'as'
    GLOBAL = 'global'
    TRUE = 'True'
    FALSE = 'False'
    NONE = 'None'
    # 逻辑和比较运算符
    OR = 'or'
    AND = 'and'
    NOT = 'not'
    EQ = '=='
    NOTEQ = '!='
    LTEQ = '<='
    LT = '<'
    RT = '>'
    RTEQ = '>='
    # 特殊符号
    END = 'EOF'  # 文件结束符
    NEWLINE = '\n'
    EMPTY = '空白'  # 用于表示空白字符，如空格、制表符或换行符

class LexDFA(Enum):
    Start0 = 0
    State1 = 1
    State2 = 2
    State3 = 3
    State4= 4
    State5 = 5
    State6 = 6
    State7 = 7
    State8 = 8
    State9 = 9
    State10 = 10
    State11 = 11
    State12 = 12
    State13 = 13
    State14 = 14
    State15 = 15
    State16 = 16
    State17 = 17
    State18 = 18
    State19 = 19
    State20 = 20
    State21 = 21
    State22 = 22
    State23 = 23
    Error = 24


class Token:
    def __init__(self, tokentype, value=0.0, linenum=0):
        self.tokenType = tokentype
        self.value = value
        self.linenum = linenum  # 确保此行的缩进与其他行一致

    def show(self):
        print(f"{self.tokenType.name.ljust(15)} {str(self.value).ljust(15)} {str(self.linenum)}")

def getChar(str, pos):
	if pos<len(str):
		return str[pos]
	else:
		return ""

# 用状态机获取token
def Lexer(string):
    tokens = []  # 识别出的token
    cur_state = LexDFA.Start0
    linenum = 1
    tmptoken = ""
    i = 0

    while True:
        c = getChar(string, i)

        if cur_state == LexDFA.Start0:
            if c=="\n" :
                tokens.append(Token(TokenType.NEWLINE, c, linenum))
                linenum+=1
                i += 1
                cur_state = LexDFA.Start0
            elif  c == " " or c=="\t":
                i += 1
                cur_state = LexDFA.Start0
            elif c=="":
                tokens.append(Token(TokenType.END, c, linenum))
                break
            elif c== "_" or c.isalpha():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State1
            elif c.isdigit():
                tmptoken+=c
                i += 1
                cur_state = LexDFA.State7
            elif c==".":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State13
            elif c=="+" or c=="-" or c=="*" or c=="/":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State16
            elif c=="=" or c=="<" or c==">" or c=="!":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State19
            elif c=="\"":
                i += 1
                cur_state = LexDFA.State5
            elif c=="\'":
                i += 1
                cur_state = LexDFA.State6
            elif c==":":
                tmptoken += c
                tokens.append(Token(TokenType.COLON, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c==",":
                tmptoken += c
                tokens.append(Token(TokenType.COMMA, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="(":
                tmptoken += c
                tokens.append(Token(TokenType.LPAREN, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c==")":
                tmptoken += c
                tokens.append(Token(TokenType.RPAREN, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="{":
                tmptoken += c
                tokens.append(Token(TokenType.LBRACE, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="}":
                tmptoken += c
                tokens.append(Token(TokenType.RBRACE, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="[":
                tmptoken += c
                tokens.append(Token(TokenType.LBRACKET, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="]":
                tmptoken += c
                tokens.append(Token(TokenType.RBRACKET, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            else:
                print("line " + str(linenum) + " 词法错误: " + tmptoken + c)
                exit(0)

        elif cur_state == LexDFA.State1:
            if c== "_" or c.isalpha() or c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State1
            else:# ID识别结束
                # 判断tmptoken是否为关键字
                if tmptoken.upper() in TokenType.__members__:
                    token_type = TokenType[tmptoken.upper()]  # 获取相应的枚举类型
                    tokens.append(Token(token_type, tmptoken, linenum))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, tmptoken, linenum))
                # 重置tmptoken
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state == LexDFA.State5:
            if c!="\"" and c!="\n":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State5
            elif c=="\"":
                tokens.append(Token(TokenType.STRING, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="\n":
                print("line " + str(linenum) + " 词法错误: " + tmptoken + c)
                exit(0)

        elif cur_state == LexDFA.State6:
            if c!="\'" and c!="\n":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State6
            elif c=="\'":
                tokens.append(Token(TokenType.STRING, tmptoken, linenum))
                tmptoken = ""
                i += 1
                cur_state = LexDFA.Start0
            elif c=="\n":
                print("line " + str(linenum) + " 词法错误: " + tmptoken + c)
                exit(0)

        elif cur_state == LexDFA.State7:
            if c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State7
            elif c==".":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State8
            elif c=="e" or c=="E":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State11
            else:
                tokens.append(Token(TokenType.NUMBER, float(tmptoken), linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state == LexDFA.State8:
            if c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State9
            else:
                tokens.append(Token(TokenType.NUMBER, float(tmptoken), linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state==LexDFA.State9:
            if c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State9
            elif c=="e" or c=="E":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State11
            else:
                tokens.append(Token(TokenType.NUMBER, float(tmptoken), linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state==LexDFA.State11:
            if c.isdigit() or c=="-":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State12
            else:
                print("line "+str(linenum) +" 词法错误: "+tmptoken+c)
                exit(0)

        elif cur_state== LexDFA.State12:
            if c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State12
            else:
                tokens.append(Token(TokenType.NUMBER, float(tmptoken), linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state==LexDFA.State13:
            if c.isdigit():
                tmptoken += c
                i += 1
                cur_state = LexDFA.State14
            else:
                tokens.append(Token(TokenType.DOT, tmptoken, linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0

        elif cur_state == LexDFA.State16:
            if c=="=":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State17
            else:
                if tmptoken=="+":
                    tokens.append(Token(TokenType.PLUS, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                elif tmptoken=="-":
                    tokens.append(Token(TokenType.MINUS, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                elif tmptoken=="*":
                    tokens.append(Token(TokenType.TIMES, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                else:
                    tokens.append(Token(TokenType.DIVIDE, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0

        elif cur_state == LexDFA.State17:
            tokens.append(Token(TokenType.AUGASSIGN, tmptoken, linenum))
            tmptoken = ""
            cur_state = LexDFA.Start0

        elif cur_state == LexDFA.State19:
            if c=="=":
                tmptoken += c
                i += 1
                cur_state = LexDFA.State20
            else:
                if tmptoken=="=":
                    tokens.append(Token(TokenType.ASSIGN, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                elif tmptoken=="<":
                    tokens.append(Token(TokenType.LT. tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                elif tmptoken == ">":
                    tokens.append(Token(TokenType.RT, tmptoken, linenum))
                    tmptoken = ""
                    cur_state = LexDFA.Start0
                else:
                    print("line " + str(linenum) + " 词法错误: " + tmptoken + c)
                    exit(0)

        elif cur_state == LexDFA.State20:
            if tmptoken=="==":
                tokens.append(Token(TokenType.EQ, tmptoken, linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0
            elif tmptoken=="<=":
                tokens.append(Token(TokenType.LTEQ, tmptoken, linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0
            elif tmptoken==">=":
                tokens.append(Token(TokenType.RTEQ, tmptoken, linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0
            elif tmptoken=="!=":
                tokens.append(Token(TokenType.NOTEQ, tmptoken, linenum))
                tmptoken = ""
                cur_state = LexDFA.Start0



    return tokens;


# 过滤注释
def filterComment(string):
    filterstr = ""
    cur_state = LexDFA.Start0

    for c in string:
        if cur_state == LexDFA.Start0:
            if c=="#":
                cur_state = LexDFA.State1
            else:
                filterstr+=c
        elif cur_state == LexDFA.State1:
            if c=="\n":
                filterstr+=c
                cur_state = LexDFA.Start0

    return filterstr

def read_file_to_string(filename):
    """读取指定文件的全部内容并返回一个字符串。"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "文件未找到。"
    except IOError:
        return "文件读取中出现错误。"
    except Exception as e:
        return f"发生未知错误: {e}"
# 将过滤后的内容写入新文件
def write_string_to_file(content, filename):
    """将字符串写入指定文件。"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError:
        return "文件写入失败。"

    content = content.replace("{", "")
    content = content.replace("}", "")
    try:
        with open("test_run.py", 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError:
        return "文件写入失败。"




def getTokenList():
    str = read_file_to_string("test.py")
    str = filterComment(str)
    write_string_to_file(str, "test_filter.py")
    tokens = Lexer(str)
    for token in tokens:
        token.show()
    return tokens


getTokenList()