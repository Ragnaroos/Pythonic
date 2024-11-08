# Pythonic
Compiler for a Drawing Language Based on Python 3.13 - Course Design for Compiler Principles
基于python3.13的绘图语言绘图语言编译器 编译原理课程设计

![image](https://github.com/user-attachments/assets/c6fd4d6d-e420-4a7a-a4bf-0d45a77365dc)


## EBNF词法规则

本绘图语言基于python基本语句构造，去掉了部分不常用的语句。词法部分对标识符、数字和符号进行了EBNF的识别，过滤了注释和空白。

词法规则用flex文件的词法部分描述。

```c
[ \t]+				{ /* Ignore whitespace */}
\r\n?				{ line_num++; }
\n				    { line_num++; }
"#"[^"\n"]*			{ /* Ignore Python comments */ }

"def"				{ return DEF; }
"if"				{ return IF; }
"else"				{ return ELSE; }
"elif"              { return ELIF; }
"for"				{ return FOR; }
"in"                { return IN; }
"while"				{ return WHILE; }
"break"				{ return BREAK; }
"continue"			{ return CONTINUE; }
"return"			{ return RETURN; }
"pass"              { return PASS; }
"import"            { return IMPORT; }
"from"              { return FROM; }
"as"                { return AS; }

"or"                { return OR; }
"and"               { return AND; }
"not"               { return NOT; }
"True"              { return TRUE; }
"False"             { return FALSE; }
"None"              { return NONE; }
"global"            { return GLOBAL; }

[0-9]+				{ yylval.ival = atoi(yytext); return NUMBER; }
[a-zA-Z_][a-zA-Z0-9_]*	{ yylval.sval = strdup(yytext); return IDENTIFIER; }
\"[^"\n]*\"       { yylval.sval = strdup(yytext); return STRING; }
\'[^'\n]*\'       { yylval.sval = strdup(yytext); return STRING; }


"+="                   { return AUGASSIGN; }
"-="                   { return AUGASSIGN; }
"*="                   { return AUGASSIGN; }
"@="                   { return AUGASSIGN; }
"/="                   { return AUGASSIGN; }
"%="                   { return AUGASSIGN; }
"&="                   { return AUGASSIGN; }
"|="                   { return AUGASSIGN; }
"^="                   { return AUGASSIGN; }
"<<="                  { return AUGASSIGN; }
">>="                  { return AUGASSIGN; }
"**="                  { return AUGASSIGN; }
"//="                  { return AUGASSIGN; }

"=="				{ return EQ; }
"!="				{ return NOTEQ; }
"<="				{ return LTEQ; }
"<"				    { return LT; }
">"				    { return RT; }
">="				{ return RTEQ; }
":"                 { return COLON; }

"+"				{ return PLUS; }
"-"				{ return MINUS; }
"**"            { return POWER; }
"*"				{ return TIMES; }
"/"				{ return DIVIDE; }
"="				{ return ASSIGN; }
","             { return COMMA; }


";"				{ return SEMICOLON; }
"("				{ return LPAREN; }
")"				{ return RPAREN; }
"{"				{ return LBRACE; }
"}"				{ return RBRACE; }
"["             { return LBRACKET; }
"]"             { return RBRACKET; }
"."             { return DOT; }


.				{ printf("line %d: Unexpected character: %s\n", line_num, yytext); }

```

## EBNF语法规则

bison不能采用EBNF中的符号，所以bison语法规则部分对以下EBNF语法做出了同义转换。

### 基本语句

本绘图语言能够识别简单语句：赋值语句、返回语句、import语句、全局变量声明、单表达式；“pass”“break”"continue"；
复合语句：函数定义语句、if语句、for语句、while语句。

```c
file: [statements]

statements: statement statement_list
    
statement_list: statement statement_list | ε

statement: compound_stmt  | simple_stmts
    
simple_stmt: identifier_stmt
        | return_stmt
        | import_stmt
        | PASS
        | BREAK
        | CONTINUE
        | global_stmt
        ;

compound_stmt: function_def
        | if_stmt
        | for_stmt
        | while_stmt
        ;

identifier_stmt: IDENTIFIER identifier_opt
    ;

identifier_opt: ASSIGN expression 
    | AUGASSIGN expression
    | expr_rest
    ;


identifier_opt: ASSIGN expression { stat_num++; printf("stmt %d: Assignment\n", stat_num); }
    | AUGASSIGN expression { stat_num++; printf("stmt %d: Enhanced assignment\n", stat_num); }
    | expr_rest { stat_num++; printf("stmt %d: single expression\n", stat_num); }
    ;

 expr_rest:
     OR conjunction
    | AND inversion
    | NOT inversion
    | EQ sum
    | NOTEQ sum
    | LTEQ sum
	| LT sum
    | RT sum
    | RTEQ sum
    | PLUS term
    | MINUS term
    | TIMES factor
    | DIVIDE factor
    | POWER factor
    | DOT IDENTIFIER object_rest
    | LPAREN arguments RPAREN
	| LBRACKET slices RBRACKET
    ;

object_rest: /* 空 */
	| LPAREN arguments RPAREN
	;     
```

#### 赋值语句

赋值语句assignment除了能够识别单变量赋值，还能够识别增量赋值（如a+=1）。

ASSIGN指“=”，AUGASSIGN指如“+=”的增量赋值符号。

单目赋值目标single_target可以是标识符IDENTIFIER以及带括号的单目目标。

```c
assignment:
    (single_target ASSIGN)+ expression 
    | single_target AUGASSIGN expression 
    ;

single_target: IDENTIFIER
    ;
```

#### 表达式

不同于Java和C++，在Python的赋值语句里，右式可以是比较表达式。所以赋值语句assignment、if_stmt、for_stmt、for_stmt、return_stmt都使用的是同样的表达式。

表达式的定义部分参考了Python 3.10的官方EBNF文档，简化了其中的星号表达式、位运算等不会在turtle基本绘图中出现的语句。

表达式expression由逻辑或表达式disjunction组成。逻辑或表达式disjunction包括两个或多个conjunction通过逻辑OR连接的表达式。逻辑与表达式conjunction包括两个或多个inversion通过逻辑AND连接的表达式。逻辑非表达式inversion表示逻辑取反，即NOT操作符后跟另一个inversion或者一个比较表达式。

比较表达式comparison包括基本的算术表达式sum和比较操作符，比较操作符和算术表达式对compare_op_sum_pair包括一个比较操作符和一个求和表达式。求和表达式sum中的加法减法操作和项表达式。项表达式term包括乘法除法操作和因子表达式。因子表达式factor包括正负号操作和幂运算表达式。幂运算表达式power包括指数运算和基本表达式。基本表达式primary 包括对象调用、函数调用、数组索引或简单的原子。简单原子atom包括基本的数据类型，如标识符、布尔值、数字、字符串、元组、列表。

```python
expression: disjunction
    ;

disjunction: conjunction
    | conjunction OR conjunction
    ;

conjunction: inversion AND inversion
    | inversion
    ;

inversion: NOT inversion
    | comparison
    ;

comparison:sum compare_op_sum_pair
    | sum
    ;


compare_op_sum_pair: EQ sum
    | NOTEQ sum
    | LTEQ sum
    | LT sum
    | RT sum
    | RTEQ sum
    ;


sum: sum PLUS term
    | sum MINUS term
    | term
    ;

term: term TIMES factor
    | term DIVIDE factor
    | factor
    ;

factor: PLUS factor
    | MINUS factor
    | power
    ;

power:
      primary POWER factor
    | primary
    ;

primary: primary DOT IDENTIFIER
    | primary LPAREN [arguments] RPAREN
    | primary LBRACKET slices RBRACKET
    | atom
    ;

slices: expression !','
	| ','.(expression)+ [',']
    ;

atom: IDENTIFIER
    | TRUE
    | FALSE
    | NONE
    | NUMBER
    | STRING
    | tuple
    | list
    ;

tuple: LPAREN [expressions] RPAREN
    ;
    
list:  LBRACKET [expressions] RBRACKET 
    ;
    
arguments: expression COMMA arguments
    | expression
    ;
    
expressions: expression expression_list
expression_list: COMMA expression expression_list | COMMA | ε 
```

#### 返回语句

RETURN关键字与表达式expression构成返回语句。

```python
return_stmt: RETURN expression
        ;
```

#### import语句

import导入语句有直接导入语句（如import module）和模块导入语句（如from module import items）构成。

直接导入语句import_name由import关键字和带别名的点分隔模块名列表构成。点分隔模块名列表dotted_as_names是由一个或多个通过逗号分隔的、可能带有别名的点分隔模块名构成。点分隔模块名dotted_as_name即标识符。

模块导入语句import_from由关键字form、点分隔模块名、import关键字、模块导入目标。模块导入目标import_from_targets可以是一个带括号的列表，也可以是不带括号的简单列表。简单列表import_from_as_names每个导入的项可以通过 as 指定一个别名。

```python
import_stmt:
      import_name      
    | import_from       
    ;

import_name:
      IMPORT dotted_as_names
    ;

import_from:
      FROM dotted_name IMPORT import_from_targets
    ;

import_from_targets:
      LPAREN import_from_as_names COMMA RPAREN
    | import_from_as_names
    ;

import_from_as_names:
      import_from_as_name
    | import_from_as_names COMMA import_from_as_name
    ;

import_from_as_name:
      IDENTIFIER as_opt

as_opt:
      /* empty */
    | AS IDENTIFIER
    ;


dotted_as_names:
      dotted_as_name
    | dotted_as_names COMMA dotted_as_name
    ;

dotted_as_name:
      dotted_name
    | dotted_name AS IDENTIFIER
    ;

dotted_name:
      IDENTIFIER
    | dotted_name DOT IDENTIFIER
    ;
```

#### if语句

if语句有三种组成形式if、if...elif、if...else。elif可以继续进行elif嵌套。

特别地，对于语句块block通常的做法是由缩进识别块，但由于其识别过程过于繁琐，需要在bison中引入状态机判断当前缩进状态，本人在编写的过程中出现了test.py读取后行开始符号“^”无法识别导致无法进入缩进状态，遂放弃了缩进块的形式，**强制定义了block必须以{}包括的规定**，且语句块不可以为空

```python
if_stmt: IF expression COLON block elif_stmt       
    | IF expression COLON block [else_block]                   
    ;

elif_stmt: ELIF expression COLON block elif_stmt
    | ELIF expression COLON block [else_block]
    ;

else_block: ELSE COLON block
    ;
```

```python
block: LBRACE statements RBRACE
      ;
```

#### 函数定义语句

函数由def关键字、标识符、左括号、参数、右括号、冒号、语句块block构成。参数可以为空。参数列表由逗号分隔标识符。

```python
function_def: DEF IDENTIFIER LPAREN params RPAREN COLON block 
    ;


params: /* 空，没有参数 */
    | param_list
    ;

param_list: IDENTIFIER
    | param_list COMMA IDENTIFIER
    ;
```

#### for语句

for语句仅支持for...in的形式，简化掉了for...in..else。

```python
for_stmt: FOR IDENTIFIER IN expression COLON block 
```

#### while语句

while语句仅支持while...的形式，简化掉了while..else。

```python
while_stmt: WHILE expression COLON block 
```

**以上的语法规则可以被flex+bison正确识别，但是如果采用递归下降文法，需要消除其中的左递归和左公共因子。**



# 语义规则

所有语义错误均不会退出程序。

1.如果没有引入任何包，则不能进行turtle绘图操作

```python
print("Syntax Fault: 没有引入任何包！")
```

2.对于对象调用函数，因为本语法并没有定义class相关产生式，所以对象调用函数的对象只能来自于import包。

```python
print("Syntax Fualt: 未import的对象名！" + node.value.value)
```

3.import包的对象不能被赋值，这会导致后续函数调用无法运行。

```py
print("Syntax Fualt: 非法的标识符命名！"+node.value.value+" 与 import包名 "+t.value.value+" 冲突")
```

4.类型错误：当你传入的参数类型不符合函数或方法所期望的类型时， 会抛出类型错误。
对于函数setpos、towards、distance他们具有相同的参数类型(x, y=None)，x为一个数字时，y不能为空；x为元组时，y必须为空。

```python
print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) x参数为元组时，y应当为空")
print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) x参数为元组时，元组应当包含2个number")
print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) 参数应当为2个number")
print("Syntax Fault: 类型错误（Type Error）"+function_name+"(x, y=None) 有参数不是number")
```

对于函数color：

color(colorstring)：使用一个颜色字符串同时设置画笔颜色和填充颜色。 color((r, g, b))：使用一个 RGB 元组同时设置画笔颜色和填充颜色。color(r, g, b)：直接使用三个分量来同时设置画笔颜色和填充颜色。color(colorstring1, colorstring2)：分别使用两个颜色字符串设置画笔颜色和填充颜色。 color((r1, g1, b1), (r2, g2, b2))：分别使用两个 RGB 元组设置画笔颜色和填充颜色。

```python
print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用不正确的RGB元组格式")
print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用不正确的参数组合或类型")
print(f"Syntax Fault: 类型错误（Type Error）{function_name} 使用了不支持的参数类型或格式")
```

5.值错误：如果RGB的值大于1.0则值错误。

```python
print(f"Syntax Fault: 值错误（Value Error）{function_name}(r, g, b) RGB的值不应大于1.0")
```



# 绘图语言源程序示例

正确的源程序

```python
import turtle
def draw_heart(size, color1, color2):
    {turtle.speed(1)
    turtle.color(color1, color2)
    turtle.begin_fill()
    turtle.left(140)
    turtle.forward(size)
    for _ in range(200):
        {turtle.right(1)
        turtle.forward(size * 3.14 / 180 / 2)}
    turtle.left(120)
    for _ in range(200):
        {turtle.right(1)
        turtle.forward(size * 3.14 / 180 / 2)}
    turtle.forward(size)
    turtle.end_fill()}
def draw_star(size, color):
    {turtle.color(color)
    turtle.begin_fill()
    for _ in range(5):
        {turtle.forward(size)
        turtle.right(144)}
    turtle.end_fill()}
def draw_spiral(length, angle, color):
    {turtle.color(color)
    turtle.speed(5)  # 加快螺旋的绘制速度
    for i in range(length):
        {if (i / 20) - int(i / 20) == 0:  # 每20步更改一次方向
            {turtle.right(angle)}
        else:
            {turtle.forward(i / 2)  # 随着步骤增加，步长变长
            turtle.right(angle)}
        }
    }
turtle.setpos((100,100))
draw_heart(100, color1="red", color2="pink")# 调用画桃心的函数
turtle.penup()# 移动到合适位置画五角星
turtle.goto(-50, -100)
turtle.pendown()
draw_star(150, "yellow")# 调用画五角星的函数
turtle.penup()
turtle.goto(200, 200)
turtle.pendown()
draw_spiral(100, 45, "blue")# 调用画螺旋形的函数
turtle.hideturtle()# 隐藏乌龟图标并完成绘图
turtle.done()
```

打印完整的token列表、语法树、不会产生语义报错，根据语法树生成test_final.py文件该文件可以被直接运行。

token列表部分内容如下图。

<img src="C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524210549853.png" alt="image-20240524210549853" style="zoom: 67%;" />

语法树部分内容如图。

<img src="C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524210642868.png" alt="image-20240524210642868" style="zoom:67%;" />

没有打印任何语义错误，并且根据语法树生成的test_final.py可以直接运行。

![image-20240524210917631](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524210917631.png)

出现词法错误。

```python
import turtle
def draw_heart(size, color1, color2):
    {turtle.speed(1ee)# 没有这样的浮点数形式
```

<img src="C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524211436629.png" alt="image-20240524211436629" style="zoom:67%;" />

出现语法错误。缺少右括号

```python
import turtle
def draw_heart(size, color1, color2):
    {turtle.speed(1
```

报错如下图所示，在第三行期望一个右括号，但是接收的是换行符。

![image-20240524211627541](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524211627541.png)

语法错误，缺少对象的调用。

```python
import turtle
def draw_heart(size, color1, color2):
    {turtle.speed(1)
    .color(color1, color2)
```

![image-20240524211912749](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524211912749.png)

语义错误。

```python
import turtle as tt
def draw_heart(size, color1, color2):
    {turtle.speed(1) # 没有turtle对象的声明，不合理的调用
     turtle.color((1.2, 1.3, 1.4))# RGB值超出规定
............省略正确的绘图代码
turtle.setpos((100)) # 参数类型错误
```

![image-20240524212409565](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524212409565.png)

![image-20240524212447097](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524212447097.png)

# 高级语言的词法分析

#### 数据结构

用Token保存所有合法终结符。

```python
class Token:
    def __init__(self, tokentype, value=0.0, linenum=0):
        self.tokenType = tokentype
        self.value = value
        self.linenum = linenum 

    def show(self):
        print(f"{self.tokenType.name.ljust(15)} {str(self.value).ljust(15)} {str(self.linenum)}")
```

tokenType为枚举类型。

```python
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
```

#### 过滤注释的DFA

输入test.py，将所有注释过滤，获得test_filter.py。过滤注释的DFA如下图所示。

![image-20240524213012691](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524213012691.png)

定义状态枚举类型，便于完成状态转换。

```python
class LexDFA(Enum):
    Start0 = 0
    State1 = 1
    State2 = 2
```

伪代码

```python
函数 filterComment(输入字符串 string):
    初始化空字符串 filterstr 用于存储过滤后的结果
    初始化当前状态 cur_state 为 LexDFA.Start0 （非注释状态）

    遍历字符串中的每一个字符 c:
        如果当前状态是 LexDFA.Start0:
            如果字符 c 是 "#":
                将当前状态切换到 LexDFA.State1 （注释状态）
            否则:
                将字符 c 添加到 filterstr 中

        否则，如果当前状态是 LexDFA.State1:
            如果字符 c 是换行符 "\n":
                将字符 c 添加到 filterstr 中
                将当前状态切换回 LexDFA.Start0 （返回非注释状态）

    返回过滤后的字符串 filterstr
```

#### 识别token的DFA

输入过滤注释后的字符串，空格和制表符不保存为token，返回token列表。

![image-20240524214215306](C:\Users\mary\AppData\Roaming\Typora\typora-user-images\image-20240524214215306.png)

```python
函数 Lexer(输入字符串 string):
    初始化 tokens 列表用于存储识别出的tokens
    初始化当前状态为 LexDFA.Start0
    初始化行号为 1
    初始化临时字符串 tmptoken 为空
    初始化索引 i 为 0

    循环直到结束:
        c = 从 string 中获取第 i 个字符

        根据 cur_state 判断:
            如果 cur_state 是 LexDFA.Start0:
                根据字符 c 的不同类型进行判断:
                    如果 c 是换行符:
                        添加 NEWLINE token
                        行号增加
                        索引增加
                    如果 c 是空格或制表符:
                        索引增加
                    如果 c 是文件结束:
                        添加 END token
                        终止循环
                    如果 c 是字母或下划线:
                        添加到 tmptoken
                        状态转为 State1
                    如果 c 是数字:
                        添加到 tmptoken
                        状态转为 State7
                    如果 c 是点号:
                        添加到 tmptoken
                        状态转为 State13
                    如果 c 是操作符(+ - * /):
                        添加到 tmptoken
                        状态转为 State16
                    如果 c 是关系或逻辑操作符(= < > !):
                        添加到 tmptoken
                        状态转为 State19
                    如果 c 是引号:
                        状态转为 State5 或 State6
                    如果 c 是其它符号(如: , ( ) { } [ ] :):
                        添加对应的 token
                        索引增加
                        状态恢复为 Start0
                    否则:
                        打印词法错误并退出

            如果 cur_state 是 State1 (标识符或关键字状态):
                如果 c 是字母、数字或下划线:
                    继续添加到 tmptoken
                否则:
                    确定 tmptoken 是关键字还是普通标识符
                    添加到 tokens
                    清空 tmptoken
                    状态恢复为 Start0

            其它状态 (State5, State6, State7, State13, State16, State19 等):
                根据具体状态处理字符c，构建 token
                遇到结束符或特殊字符时，生成 token 并调整状态

    返回 token列表
```



# 高级语言的语法分析

#### 数据结构

type为符号类型，终结符type为TokenType的name值，非终结符为符号名称如”program“”if_stmt“。

```python
class Node:
    def __init__(self, type, children=None, value=None, imported_names=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.imported_names = imported_names if imported_names is not None else []

```

#### 递归下降的语法分析

递归下降基于LL(1)文法进行，LL(1)要求相同非终结符的产生式SELECT集不相交，消除左递归和左公共因子，从而做到每次读取一个token，就能确定使用哪一条产生式。所以需要对EBNF中的文法进行改进。对于产生式中的非终结符继续递归，终结符使用MatchToken()匹配，并FetchToken()获取下一个终结符。


program-> /* empty */ | statements END

```python
first(statements) = { DEF, IF, FOR, WHILE,
                 RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
                 IDENTIFIER,
                 TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
follow(program) = {END}
select(program->/* empty */)
	= FIRST(/* empty */)∪ FOLLOW(program)
    = {空, END}
select(program->statements)
	= FIRST(statements)
    = {DEF, IF, FOR, WHILE,
       RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
       IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}

函数 parse_program():
    # 跳过所有新行符，直到遇到非新行符
    while 当前token是 NEWLINE:
        匹配 NEWLINE token
        获取下一个 token

    # 检查当前token是否是文件结束标志 END
    if 当前token是 END:
        # 如果是，返回一个代表空程序的节点
        返回 Node("EMPTYprogram")

    # 如果当前token是可开始语句的token类型之一
    elif 当前token类型在 {
        DEF, IF, FOR, WHILE,
        RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
        IDENTIFIER,
        TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET
    } 的集合中:
        # 解析语句并构建语句节点
        statements_node = 调用 parse_statements()
        # 匹配程序结束的 END token
        if 匹配 TokenType.END:
            # 创建程序节点，附带语句子节点
            program_node = Node("program", children=[statements_node])
            # 收集所有导入的名称
            program_node.imported_names = program_node.collect_imports()
            # 返回程序节点
            返回 program_node
        else:
            # 如果没有匹配到 END token，打印语法错误并退出
            打印("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.END received ", tokenNow.tokenType)
            退出程序
    else:
        # 如果当前token不符合期望，打印语法错误并退出
        打印("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.END received ", tokenNow.tokenType)
        退出程序
```

statements->statement statements_rest

```python
first(statement) = {DEF, IF, FOR, WHILE,
                 RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
                 IDENTIFIER,
                 TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
select(statements->statement statements_rest)
	= first(statement statements_rest)
    = {DEF, IF, FOR, WHILE,
       RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
       IDENTIFIER,NOT,PLUS,MINUS
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}

函数 parse_statements():
    # 解析一个单独的语句
    statement_node = 调用 parse_statement()
    # 解析剩余的语句序列
    statements_rest_node = 调用 parser_statements_rest()
    # 创建一个 'statements' 类型的节点，将刚才解析的单独语句节点和剩余语句序列节点作为子节点
    返回 Node("statements", children=[statement_node, statements_rest_node])
```

statements_rest->  /* empty */| statements

```python
select(statements_rest->/* empty */)
	= FIRST(/* empty */) ∪ FOLLOW(statements_rest)
	= FIRST(/* empty */) ∪ FOLLOW(statements) ∪ FOLLOW(program)
    = {空, END, RBRACE}
select(statements_rest->statements)
	= first(statements) 
	= { DEF, IF, FOR, WHILE,
                 RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
                 IDENTIFIER,
                 TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
    
函数 parser_statements_rest():
    # 检查当前token是否为新行、文件结束或右花括号，这些情况表示没有更多的语句
    if 匹配 TokenType.NEWLINE 或 TokenType.END 或 TokenType.RBRACE:
        # 如果是上述情况之一，不做任何操作，表示这里是一个空的语句序列
        pass
    else:
        # 如果当前位置还有更多的语句，递归解析这些语句
        statements_node = 调用 parse_statements()
        # 创建并返回一个包含解析出的语句的节点
        返回 Node("statements_rest", children=[statements_node])
    
```

statement-> compound_stmt| simple_stmt NEWLINE

```python
select(statement-> compound_stmt) 
	= first(compound_stmt)
    = {DEF, IF, FOR, WHILE}
select(statement-> simple_stmt)  
	= first(simple_stmt)
    = {RETURN, IMPORT, PASS, BREAK, CONTINUE, GLOBAL,
       IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}

函数 parse_statement():
    # 判断当前token的类型，决定是处理复合语句还是简单语句
    if 当前token类型在 {DEF, IF, FOR, WHILE} 的集合中:
        # 处理复合语句
        compound_stmt_node = 调用 parser_compound_stmt()
        # 创建并返回包含复合语句节点的statement节点
        返回 Node("statement", children=[compound_stmt_node])
    else:
        # 处理简单语句
        simple_stmt_node = 调用 parser_simple_stmt()
        # 确保简单语句后面跟随一个新行符
        if 匹配 TokenType.NEWLINE 或 TokenType.END 或 TokenType.RBRACE:
            # 创建一个表示新行的节点
            node = Node(str(TokenType.NEWLINE), children=[], value=Token(TokenType.NEWLINE, "\n", tokenNow.linenum))
            # 如果当前token是新行符，获取下一个token
            if 匹配 TokenType.NEWLINE:
                获取下一个 token
            # 创建并返回包含简单语句节点和新行节点的statement节点
            返回 Node("statement", children=[simple_stmt_node, node])
        else:
            # 如果没有正确匹配新行符，打印语法错误并退出程序
            打印("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.NEWLINE received ", tokenNow.tokenType)
            退出程序

```

compound_stmt-> function_def| if_stmt| for_stmt| while_stmt

```python
select(compound_stmt-> function_def) 
	= first(function_def)
    = {DEF}
select(compound_stmt-> if_stmt)     
	= first(if_stmt)
    = {IF}
select(compound_stmt-> for_stmt)   
	= first(for_stmt)
    = {FOR}
select(compound_stmt-> while_stmt)  
	=  first(while_stmt)
    = {WHILE}


函数 parser_compound_stmt():
    # 根据当前 token 的类型，确定并调用相应的复合语句解析函数
    if 当前token类型是 TokenType.DEF:
        # 如果是函数定义，调用解析函数定义的函数
        function_def_node = 调用 parser_function_def()
        # 创建一个复合语句节点，并将函数定义节点作为子节点
        返回 Node("compound_stmt", children=[function_def_node])
    elif 当前token类型是 TokenType.IF:
        # 如果是if语句，调用解析if语句的函数
        if_stmt_node = 调用 parser_if_stmt()
        # 创建一个复合语句节点，并将if语句节点作为子节点
        返回 Node("compound_stmt", children=[if_stmt_node])
    elif 当前token类型是 TokenType.FOR:
        # 如果是for循环，调用解析for循环的函数
        for_stmt_node = 调用 parser_for_stmt()
        # 创建一个复合语句节点，并将for循环节点作为子节点
        返回 Node("compound_stmt", children=[for_stmt_node])
    elif 当前token类型是 TokenType.WHILE:
        # 如果是while循环，调用解析while循环的函数
        while_stmt_node = 调用 parser_while_stmt()
        # 创建一个复合语句节点，并将while循环节点作为子节点
        返回 Node("compound_stmt", children=[while_stmt_node])
```

simple_stmt-> identifier_stmt| atom_rest expr_rest|NOT inversion|PLUS factor| MINUS factor| return_stmt| import_stmt| PASS| BREAK| CONTINUE

```python
函数 parser_simple_stmt():
    # 判断当前 token 的类型，根据类型调用相应的解析函数
    if 当前token类型是 TokenType.IDENTIFIER:
        identifier_stmt_node = 调用 parser_identifier_stmt()
        返回 Node("simple_stmt", children=[identifier_stmt_node])
    elif 匹配 TokenType.NOT:
        创建节点 node 存储当前 token
        获取下一个 token
        inversion_node = 调用 parser_inversion()
        返回 Node("simple_stmt", children=[node, inversion_node])
    elif 匹配 TokenType.PLUS 或 TokenType.MINUS:
        创建节点 node 存储当前 token
        获取下一个 token
        factor_node = 调用 parser_factor()
        返回 Node("simple_stmt", children=[node, factor_node])
    elif 当前token类型是 TokenType.RETURN:
        return_stmt_node = 调用 parser_return_stmt()
        返回 Node("simple_stmt", children=[return_stmt_node])
    elif 当前token类型是 TokenType.IMPORT:
        import_stmt_node = 调用 parser_import_stmt()
        返回 Node("simple_stmt", children=[import_stmt_node])
    elif 当前token类型在 {TokenType.PASS, TokenType.BREAK, TokenType.CONTINUE} 中:
        创建节点 node 存储当前 token
        获取下一个 token
        返回 Node("simple_stmt", children=[node])
    else:
        atom_rest_node = 调用 parser_atom_rest()
        expr_rest_node = 调用 parser_expr_rest()
        返回 Node("simple_stmt", children=[atom_rest_node, expr_rest_node])
     
```

identifier_stmt-> IDENTIFIER identifier_opt

```python
select(identifier_stmt-> IDENTIFIER identifier_opt) 
	= {IDENTIFIER}
函数 parser_identifier_stmt():
    # 确认当前 token 是标识符
    匹配Token(TokenType.IDENTIFIER)
    # 创建一个节点，节点类型为当前token的类型，此节点不包含子节点，但包含当前token作为值
    node = 创建Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
    # 获取下一个token
    获取Token()
    # 解析标识符后的选项部分，可能是赋值或函数调用等
    identifier_opt_node = 调用 parser_identifier_opt()
    # 创建并返回一个包含标识符和其选项的标识符语句节点
    返回 Node("identifier_stmt", children=[node, identifier_opt_node])
```

**以上伪代码展示了根据select集合选择产生式，并对终结符的匹配和非终结符的递归的过程。以下为本语言全部的产生式及其SELECT集。**

identifier_opt-> ASSIGN expression| AUGASSIGN expression| expr_rest

    select(identifier_opt-> ASSIGN expression)
    	= {ASSIGN}
    select(identifier_opt-> AUGASSIGN expression)
    	= {AUGASSIGN}	
    select(identifier_opt-> expr_rest)
    	= FIRST(expr_rest) ∪ FOLLOW(identifier_opt)
    	= FIRST(expr_rest) ∪ FOLLOW(identifier_stmt) 
    	= FIRST(expr_rest) ∪ FOLLOW(simple_stmt) 
    	= FIRST(expr_rest) ∪ FOLLOW(statement)
    	= {空, END, RBRACE, 
    	OR, AND, NOT, 
    	EQ, NOTEQ, LTEQ, LT, RT, RTEQ,
    	PLUS, MINUS, TIMES, DIVIDE, POWER
    	DOT, LPAREN, LBRACKET}	

expr_rest-> /* 空 */| OR conjunction| AND inversion| NOT inversion| EQ sum| NOTEQ sum | LTEQ sum| LTEQ sum| LT sum| RT sum| RTEQ sum | PLUS term| MINUS term| TIMES factor| DIVIDE factor| POWER factor| DOT IDENTIFIER object_rest| LPAREN arguments RPAREN| LBRACKET slices RBRACKET

```python
select(expr_rest-> /* 空 */)
 = FIRST(/* 空 */) ∪ FOLLOW(expr_rest)
 = FIRST(/* 空 */) ∪ FOLLOW(identifier_opt)
`= {空, END, RBRACE}
# 其余略
```

object_rest-> /* 空 */| LPAREN arguments RPAREN

```python
select(object_rest-> /* 空 */)
	= FIRST(/* 空 */) ∪ FOLLOW(object_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(expr_rest)
    = {空, END, RBRACE}
select(object_rest-> LPAREN arguments RPAREN)
	= {LPAREN}
```

block-> NEWLINE LBRACE statements RBRACE

```python
select(block-> LBRACE statements RBRACE)
	= {NEWLINE}
```

expression-> disjunction

```python
select(expression-> disjunction)
	 = first(disjunction)
	 = first(conjunction)
	 = first(inversion)
	 = {NOT, PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

disjunction-> conjunction disjunction_rest

```python
select(disjunction-> conjunction disjunction_rest)
	= first(conjunction)
	= {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

disjunction_rest-> OR conjunction| /* 空 */

```python
select(disjunction_rest-> OR conjunction)
	= {OR}
select(disjunction_rest-> /* 空 */)	
	= FIRST(/* 空 */) ∪ FOLLOW(disjunction_rest)
	= FIRST(/* 空 */) ∪ FOLLOW(disjunction)
	= FIRST(/* 空 */) ∪ FOLLOW(expression)
	= {空, END, RBRACE,
	RBRACKET, COMMA, RPAREN, COLON}
```

conjunction-> inversion conjunction_rest

```python
select(conjunction-> inversion conjunction_rest)
	= first(inversion)
    = {NOT, PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

conjunction_rest->  AND inversion|  /* 空 */

```python
select(conjunction_rest->  AND inversion)
	= {AND}
select(conjunction_rest-> /* 空 */)
	= FIRST(/* 空 */) ∪ FOLLOW(conjunction_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(conjunction)
    = FIRST(/* 空 */) ∪ FOLLOW(disjunction_rest)
    = {空, END, RBRACE,
	RBRACKET, COMMA, RPAREN, COLON}
```

inversion-> NOT inversion| comparison

    select(inversion-> NOT inversion)
    	= {NOT}
    select(inversion-> comparison)
    	= first(comparison)
    	= {PLUS, MINUS,
    	   IDENTIFIER,
           TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}

comparison-> sum comparison_rest

```python
select(comparison-> sum comparison_rest)
	= first(sum)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

comparison_rest-> compare_op_sum_pair| /* 空 */

```python
select(comparison_rest-> compare_op_sum_pair)
	= {EQ, NOTEQ, LTEQ, LT, RT, RTEQ}
select(comparison_rest-> /* 空 */)    
	= FIRST(/* 空 */) ∪ FOLLOW(comparison_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(conjunction_rest)
    = {空, END, RBRACE,
	RBRACKET, COMMA, RPAREN, COLON}
```

compare_op_sum_pair-> EQ sum| NOTEQ sum| LTEQ sum| LT sum| RT sum| RTEQ sum

sum-> term sum_prime

```python
select(sum-> term sum_prime) 
	= first(term)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

sum_prime-> sum_rest sum_prime| /* 空 */

```python
select(sum_prime-> sum_rest sum_prime) 
	=  first(sum_rest)
    =  {PLUS, MINUS}
select(sum_prime-> /* 空 */) 
	= FIRST(/* 空 */) ∪ FOLLOW(sum_prime)
    = FIRST(/* 空 */) ∪ FOLLOW(sum)
    = FIRST(/* 空 */) ∪ FOLLOW(comparison_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(conjunction_rest)
    = {空, END, RBRACE,
	RBRACKET, COMMA, RPAREN, COLON}
```

sum_rest-> PLUS term| MINUS term

term-> factor term_prime

```python
select(term-> factor term_prime) 
	=  first(factor)
    =  {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

term_prime-> term_rest term_prime| /* 空 */ 

```python
select(term_prime-> term_rest term_prime) 
	=  first(term_rest)
    =  {TIMES, DIVIDE}
select(term_prime-> /* 空 */) 
	= FIRST(/* 空 */) ∪ FOLLOW(term_prime)
    = FIRST(/* 空 */) ∪ FOLLOW(sum_prime) ∪ first(sum_rest)
    = {空, END, RBRACE,
    PLUS, MINUS
	RBRACKET, COMMA, RPAREN, COLON}
```

term_rest: TIMES factor| DIVIDE factor

factor-> PLUS factor| MINUS factor| power

```python
select(factor-> PLUS factor) 
	={PLUS}
select(factor-> MINUS factor) 
	={MINUS}    
select(factor-> power) 
	={IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}       
```

power-> primary power_rest

```python
select(power-> primary power_rest) 
	= {IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

power_rest-> POWER factor| /* 空 */

```python
select(power_rest-> POWER factor) 
	= {POWER}
select(power_rest-> /* 空 */)    
	= FIRST(/* 空 */) ∪ FOLLOW(power_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(sum_prime)∪ first(sum_rest)∪ first(term_rest)
    = {空, END, RBRACE,
    PLUS, MINUS, TIMES, DIVIDE,
	RBRACKET, COMMA, RPAREN, COLON} 
```

primary-> atom primary_rest

```python
select(primary-> atom primary_rest) 
	= {IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}    
```

primary_rest->primary_operation primary_rest| /* 空 */

```py
select(primary_rest->primary_operation primary_rest)
	= {DOT, LPAREN, LBRACKET}
select(primary_rest->/* 空 */)
	= FIRST(/* 空 */) ∪ FOLLOW(primary_rest)
    = FIRST(/* 空 */) ∪ FOLLOW(sum_prime)∪ first(sum_rest)∪ first(term_rest)∪ first(power_rest)
    = {空, END, RBRACE,
    PLUS, MINUS, TIMES, DIVIDE, POWER
	RBRACKET, COMMA, RPAREN, COLON} 
```

primary_operation-> DOT IDENTIFIER| LPAREN primary_lparen_rest| LBRACKET slices RBRACKET

primary_lparen_rest-> arguments RPAREN

```python
select(primary_lparen_rest-> arguments RPAREN)
	= FIRST(arguments)
    = {空, IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

slices-> expression slices_rest

```python
select(slices-> expression slices_rest)
	= FIRST(expression)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

slices_rest-> COMMA slices| /* 空 */

```python
select(slices_rest-> COMMA slices)
	= {COMMA}
select(slices_rest-> /* 空 */)    
	= FIRST(/* 空 */) ∪ FOLLOW(slices_rest)
    = {空, RBRACKET}
```

atom-> IDENTIFIER| TRUE| FALSE| NONE| NUMBER| STRING| tuple| list

```python
select(atom->tuple)
	= {LPAREN}
select(atom->list)
	= {LBRACKET}
```

tuple-> LPAREN tuple_rest

tuple_rest-> RPAREN|  expressions RPAREN

```python
select(atom->tuple)
	= {RPAREN}
select(atom->expressions RPAREN)
	= FIRST(expressions)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

list: LBRACKET list_rest

list_rest: RBRACKET| expressions RBRACKET

```python
= FIRST(expressions)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

expressions-> expression expressions_rest

```python
= FIRST(expressions)
    = {PLUS, MINUS,
	   IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
```

expressions_rest-> COMMA expression expressions_rest| /* 空 */

```python
select(expressions_rest-> COMMA expression expressions_rest)
	= {COMMA}
select(expressions_rest->/* 空 */) 
	= FIRST(/* 空 */) ∪ FOLLOW(expressions_rest)
    = {空, RPAREN, RBRACKET}
```

arguments-> kwarg arguments_rest| /* 空 */

```python
select(arguments-> kwarg arguments_rest)
	= {IDENTIFIER,
       TRUE, FALSE, NONE, NUMBER, STRING, LPAREN, LBRACKET}
select(arguments-> /* 空 */) 
	= FIRST(/* 空 */) ∪ FOLLOW(arguments)
    = {空, RPAREN}
```

arguments_rest-> COMMA arguments| /* 空 */

```python
select(arguments_rest-> COMMA arguments)
	= {COMMA}
select(arguments_rest->/* 空 */)    
	= FIRST(/* 空 */) ∪ FOLLOW(arguments_rest)
    = {空, RPAREN}
```

kwarg-> IDENTIFIER kwarg_rest| atom_rest expr_rest

atom_rest: TRUE| FALSE| NONE| NUMBER| STRING| tuple| list

kwarg_rest-> ASSIGN expression| expr_rest

```python
select(kwarg_rest-> ASSIGN expression)
	= {ASSIGN}
select(kwarg_rest-> expr_rest)  
	= FIRST(expr_rest) ∪ FOLLOW(kwarg_rest)
    = {空, COMMA, RPAREN,  
	OR, AND, NOT, 
	EQ, NOTEQ, LTEQ, LT, RT, RTEQ,
	PLUS, MINUS, TIMES, DIVIDE, POWER
	DOT, LPAREN, LBRACKET}	
```

return_stmt-> RETURN expression

```python
select(return_stmt-> RETURN expression)
	= {RETURN}
```

import_stmt->IMPORT dotted_as_names

```python
select(import_stmt->import_name) 
	= {IMPORT}
```

dotted_as_names->dotted_as_name dotted_as_names_rest

```python
select(dotted_as_names->dotted_as_name)
	= {IDENTIFIER}
```

dotted_as_names_rest-> COMMA dotted_as_names|  /* 空 */

```python
select(dotted_as_names_rest-> COMMA dotted_as_names)
	= {COMMA}
select(dotted_as_names_rest->  /* 空 */)
	=  FIRST(/* 空 */) ∪ FOLLOW(dotted_as_names_rest)  
    =  FIRST(/* 空 */) ∪ FOLLOW(import_stmt) 
    = {空, END, RBRACE}
```

dotted_as_name->dotted_name dotted_as_name_rest

```python
select(dotted_as_name->dotted_name)
	= {IDENTIFIER}
```

dotted_as_name_rest-> AS IDENTIFIER|  /* 空 */

```python
select(dotted_as_name_rest-> AS IDENTIFIER)
	= {AS}
select(dotted_as_name_rest->  /* 空 */)    
	= FIRST(/* 空 */) ∪ FOLLOW(dotted_as_name_rest) 
    = {空, END, RBRACE, COMMA}
```

dotted_name: IDENTIFIER dotted_name_rest

dotted_name_rest-> DOT IDENTIFIER |  /* 空 */

```python
select(dotted_name_rest->DOT IDENTIFIER)
	= {DOT}
select(dotted_name_rest-> /* 空 */)
	= FIRST(/* 空 */) ∪ FOLLOW(dotted_name_rest) 
    = {空, END, RBRACE, COMMA, AS}
```

function_def: DEF IDENTIFIER LPAREN arguments RPAREN COLON block

if_stmt-> IF expression COLON block if_stmt_rest

if_stmt_rest-> elif_stmt | else_block | /* 空 */ 

```python
select(if_stmt_rest-> elif_stmt)
	= {ELIF}
select(if_stmt_rest-> else_block)
	= {ELSE}
select(if_stmt_rest-> /* 空 */ )    
	= FIRST(/* 空 */) ∪ FOLLOW(if_stmt_rest) 
    = FIRST(/* 空 */) ∪ FOLLOW(statement)
    = {空, END}
```

elif_stmt-> ELIF expression COLON block if_stmt_rest

else_block-> ELSE COLON block

for_stmt-> FOR IDENTIFIER IN expression COLON block 

while_stmt-> WHILE expression COLON block





# 语义分析



#### 动态语义分析

动态语义分析在语法树遍历过程中识别turtle对象调用的函数，根据turtle官方文档对函数参数的要求，进行语义错误的识别，参数错误分为值错误和类型错误。类型错误是指参数类型不符合函数或方法所期望的类型，值错误是指参数类型正确，但参数的值不适当或超出了允许的范围。

```python
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
            # 根据产生式遍历语法树添加终结符
            # import_stmt->IMPORT dotted_as_names
            code += generate_python_code(node.children[0], lvl) # 递归获取import
            code += " " # 因为token和语法树不保留空格，生成时需要添加
            code += generate_python_code(node.children[1], lvl)# 递归获取dotted_as_names
        elif node.type == "if_stmt":
            # # if_stmt-> IF expression COLON block if_stmt_rest
            code += generate_python_code(node.children[0], lvl)
            code += " "
            code += generate_python_code(node.children[1], lvl)
            code += generate_python_code(node.children[2], lvl)# 冒号COLON添加
            code += "\n" # 冒号COLON后添加新行
            code += generate_python_code(node.children[3], lvl)
            code += generate_python_code(node.children[4], lvl)
        elif node.type == "else_block":
             # 其余语句略
        ...........
        ...........
        elif node.type == "for_stmt":
            # 其余语句略
        ...........
        ...........
        else:
            # 非statement元素递归所有叶子节点
            for child in node.children:
                if child:
                    code += generate_python_code(child, lvl)
    return code
```

turtle_fun_syntax_anlysis(node)里通过调用check_turtle_function_syntax函数对turtle的函数调用进行语义解析。

对于函数setpos、towards、distance他们具有相同的参数类型(x, y=None)，x为一个数字时，y不能为空；x为元组时，y必须为空。

color(colorstring)：使用一个颜色字符串同时设置画笔颜色和填充颜色。 

color((r, g, b))：使用一个 RGB 元组同时设置画笔颜色和填充颜色。RGB不能大于1.0。

color(r, g, b)：直接使用三个分量来同时设置画笔颜色和填充颜色。

color(colorstring1, colorstring2)：分别使用两个颜色字符串设置画笔颜色和填充颜色。

 color((r1, g1, b1), (r2, g2, b2))：分别使用两个 RGB 元组设置画笔颜色和填充颜色。

```python
def turtle_fun_syntax_anlysis(node):
    # 处理对象.函数 调用的可能出现的错误
    # node.print_tree()
    for t in turtle_id:
        # 判断是否为函数调用语句
        is_fun = is_function_call(node)
        node_father = node
        node = node.children[0]
        # 如果是函数调用语句，且其调用对象为import的turtle
        if t.value.value==node.value.value and is_fun:
            # 提取参数 生成函数调用语句
            extracted_args = node_father.extract_arguments()
            fun_str = ""
            for arg in extracted_args:
                fun_str += str(arg.value.value)
            check_turtle_function_syntax(fun_str, t.value.value)
		........
        # 后续为静态语义分析，略
```

check_turtle_function_syntax基于函数调用语句字符串，用正则表达式进行参数分析。

```python
函数 check_turtle_function_syntax(call_str, t):
    # 解析函数调用字符串以获取函数名和参数列表
    匹配结果 = 使用正则表达式匹配 t+"\.(\w+)\((.*)\)" 匹配 call_str

    # 从匹配结果中提取函数名和参数字符串
    函数名, 参数字符串 = 匹配结果.提取组()

    # 检查是否是特定的turtle函数
    如果 函数名 在 ['setpos', 'towards', 'distance'] 中:
        尝试:
            # 从参数字符串中解析实际参数
            参数 = 解析 参数字符串 为 Python表达式
            # 检查参数是否为元组，并且长度为2
            如果 isinstance(参数, 元组) 且 len(参数) == 2:
                # 检查每个元素是否为整数或浮点数
                如果 all(isinstance(元素, (int, float)) for 元素 in 参数):
                    通过
                否则:
                    打印 "类型错误: 函数名(x, y=None) 当x为元组时，y应当为空"
            # 检查参数是否为单个元组，且仅包含一个元素
            否则 如果 isinstance(参数, 元组) 且 len(参数) == 1:
                打印 "类型错误: 函数名(x, y=None) 当x为元组时，元组应包含两个数值"
            # 检查参数是否为两个独立的数值
            否则:
                如果 not isinstance(参数, (列表, 元组)) 或 len(参数) != 2:
                    打印 "类型错误: 函数名(x, y=None) 参数应为两个数值"
                否则 如果 not all(isinstance(元素, (int, float)) for 元素 in 参数):
                    打印 "类型错误: 函数名(x, y=None) 有参数不是数值"
        除外 异常 as e:
            打印 "解析参数错误: {e}"

    # 检查函数是否为color，处理color函数的参数验证
    否则 如果 函数名 在 ['color']:
        尝试:
            参数 = 解析 参数字符串 为 Python表达式
            如果 isinstance(参数, 字符串):
                通过  # 正常使用字符串
            # 处理RGB元组参数
            否则 如果 isinstance(参数, 元组):
                如果 len(参数) == 3:
                    # 验证RGB值是否超过1.0
                    如果 any(color > 1.0 for color in 参数):
                        打印 "值错误: 函数名 RGB值不应大于1.0"
                # 处理两个RGB元组的情况
                否则 如果 len(参数) == 2 且 all(isinstance(sub, 元组) for sub in 参数):
                    如果 any(color > 1.0 for tuple_color in 参数 for color in tuple_color):
                        打印 "值错误: 函数名 RGB值不应大于1.0"
                否则:
                    打印 "类型错误: 使用不正确的RGB元组格式"
            # 处理分开的RGB分量
            否则 如果 isinstance(参数, 列表):
                如果 len(参数) == 3 且 all(isinstance(color, (int, float)) for color in 参数):
                    如果 any(color > 1.0 for color in 参数):
                        打印 "值错误: 函数名 RGB值不应大于1.0"
                # 处理两个颜色字符串的情况
                否则 如果 len(参数) == 2 且 all(isinstance(color, 字符串) for color in 参数):
                    通过  # 正常使用两个颜色字符串
                否则:
                    打印 "类型错误: 使用不正确的参数组合或类型"
            # 处理无参数调用
            否则 如果 not 参数字符串:
                通过
            否则:
                打印 "类型错误: 使用了不支持的参数类型或格式"
        除外 异常 as e:
            打印 "解析参数错误: {e}"
```



#### 静态语义分析

静态语义分析采用属性文法的方式自底向上传递import包引用的对象，首先在语法树节点设置综合属性imported_names，同时定义函数将import语句里的IDENTIFIER向上传递到语法树顶端（即Program节点）。

```python
class Node:
    def __init__(self, type, children=None, value=None, imported_names=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.imported_names = imported_names if imported_names is not None else []

    def collect_imports(self):
        # 递归收集所有子节点的imported_names
        collected_imports = list(self.imported_names)  # 现在self.imported_names已经保证是列表
        # 递归收集所有子节点的imported_names
        for child in self.children:
            if child:  # 确保child不是None
                # 合并子节点的导入名称，处理可能的NoneType错误
                child_imports = child.collect_imports()
                if child_imports is not None:
                    collected_imports.extend(child_imports)
        return collected_imports
```

在import_stmt语句的IDENTIFIER匹配过程中，将IDENTIFIER的token保存为综合属性imported_names。

```python
# import语句的产生式如下
# import_stmt->IMPORT dotted_as_names
# dotted_as_names->dotted_as_name dotted_as_names_rest
# dotted_as_names_rest-> COMMA dotted_as_names|  /* 空 */
# dotted_as_name->dotted_name dotted_as_name_rest
# dotted_as_name_rest-> AS IDENTIFIER|  /* 空 */
# dotted_name: IDENTIFIER dotted_name_rest
# 所以在dotted_name里添加综合属性
def parser_dotted_name():
    # dotted_name: IDENTIFIER dotted_name_rest
    if MatchToken(TokenType.IDENTIFIER):
        id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        dotted_name_rest_node = parser_dotted_name_rest()
        return Node("dotted_name", children=[id_node, dotted_name_rest_node], imported_names=[id_node])# 将IDENTIFIER的token保存为综合属性
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
              tokenNow.tokenType)
        exit(0)
```

如果存在as，则需要将as前的IDENTIFIER（即dotted_name的属性）替换为as后的IDENTIFIER。

```python
def parser_dotted_as_name():
    # dotted_as_name->dotted_name dotted_as_name_rest
    dotted_name_node = parser_dotted_name()
    dotted_as_name_rest = parser_dotted_as_name_rest()
    # 如果dotted_as_name_rest不为空，说明存在as语句，覆盖dotted_as_name的综合属性
    if dotted_as_name_rest!=None:
        dotted_name_node.imported_names = []
    return Node("dotted_as_name", children=[dotted_name_node, dotted_as_name_rest])

```

在program即语法树顶获取全部的综合属性，即import包的对象。

```python
statements_node = parse_statements()
        if MatchToken(TokenType.END):
            program_node = Node("program", children=[statements_node])
            # 获取全部的综合属性
            program_node.imported_names = program_node.collect_imports()
            return program_node
```

在语义分析阶段，对import包进行处理。

```python
def analyse_syntax():
    global turtle_id
    tree = getPaserTree()
    # program节点没有综合属性则报错没有引入包
    if len(tree.imported_names)<1:
        print("Syntax Fault: 没有引入任何包！")
    else:
        turtle_id = tree.imported_names
    str = generate_python_code(tree)
    write_final_file(str, "test_final.py")
```

```python
def turtle_fun_syntax_anlysis(node):
    # 处理对象.函数()调用的可能出现的错误
    # node.print_tree()
    for t in turtle_id:
        is_fun = is_function_call(node)
        node_father = node
        node = node.children[0]
        # 对于对象调用函数，因为本语法并没有定义class相关产生式，所以对象调用函数的对象只能来自于import包。

		# 如果是函数调用语句，且其调用对象为import的turtle
        if t.value.value==node.value.value and is_fun:
            # 动态语义分析，对turtle调用函数的参数进行错误分析
            # 略
            ....
        #import包的对象不能被赋值，这会导致后续函数调用无法运行。即包对象不能作为一般标识符使用
        elif t.value.value==node.value.value and not is_fun:
            print("Syntax Fualt: 非法的标识符命名！"+node.value.value+" 与 import包名 "+t.value.value+" 冲突")
        # 非turtle对象调用函数，因为本语法并没有定义class相关产生式，所以对象调用函数的对象只能来自于import包    
        elif t.value.value!=node.value.value and is_fun:
            print("Syntax Fualt: 未import的对象名！" + node.value.value)
```

