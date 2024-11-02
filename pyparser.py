import sys

from pylex import Lexer, write_string_to_file
from pylex import Token
from pylex import TokenType
from pylex import read_file_to_string
from pylex import filterComment


class Node:
    def __init__(self, type, children=None, value=None, imported_names=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.imported_names = imported_names if imported_names is not None else []

    def add_child(self, node):
        self.children.append(node)

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

    def print_tree(self, level=0):
        indent = ' ' * (level * 4)  # 每一级增加4个空格的缩进
        if self.value:
            # 当存在 value 时，它是一个 Token 对象
            value_str = f"{self.value.tokenType.value}【{self.value.value}】, Line: {self.value.linenum}"
        else:
            value_str = "None"

            # 打印节点信息
        print(f"{indent}{self.type}({value_str})")
        for child in self.children:
            if child is not None:
                child.print_tree(level + 1)


    def extract_arguments(self):
        # 初始化一个列表来存储所有终结符节点
        argument_nodes = []

        # 定义一个辅助函数来递归遍历所有子节点
        def traverse(node):
            if node is None:
                return  # 如果节点为None，直接返回不做处理
            # 如果节点是终结符，添加到列表中
            if node.value is not None:
                argument_nodes.append(node)
            # 否则递归遍历该节点的所有子节点
            else:
                for child in node.children:
                    traverse(child)  # 只有当child不为None时，才进行递归
        # 从根节点开始遍历
        traverse(self)
        return argument_nodes


def FetchToken():
	global tokenNow
	try:
		tokenNow = next(tokenIter)
		return tokenNow
	except StopIteration:
		sys.exit()

def MatchToken(tokenType, show=False):
	if show:
		tokenNow.show()
	if tokenNow.tokenType==tokenType:
		return True
	else:
		return False

def parse_program():
    # program-> /* empty */ | statements END
    while tokenNow.tokenType == TokenType.NEWLINE:
        MatchToken(TokenType.NEWLINE)
        FetchToken()
    if tokenNow.tokenType==TokenType.END:
        return Node("EMPTYprogram")
    elif tokenNow.tokenType in {
        TokenType.DEF, TokenType.IF, TokenType.FOR, TokenType.WHILE,
        TokenType.RETURN, TokenType.IMPORT, TokenType.PASS, TokenType.BREAK, TokenType.CONTINUE, TokenType.GLOBAL,
        TokenType.IDENTIFIER,
        TokenType.TRUE, TokenType.FALSE, TokenType.NONE, TokenType.NUMBER, TokenType.STRING, TokenType.LPAREN, TokenType.LBRACKET
    }:
        statements_node = parse_statements()
        if MatchToken(TokenType.END):
            program_node = Node("program", children=[statements_node])
            program_node.imported_names = program_node.collect_imports()
            return program_node
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.END received ", tokenNow.tokenType)
            exit(0)
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.END received ", tokenNow.tokenType)
        exit(0)

def parse_statements():
    # statements->statement statements_rest
    statement_node = parse_statement()
    statements_rest_node = parser_statements_rest()
    return Node("statements", children=[statement_node, statements_rest_node])

def parse_statement():
    # statement-> compound_stmt| simple_stmt NEWLINE
    if tokenNow.tokenType in {
        TokenType.DEF, TokenType.IF, TokenType.FOR, TokenType.WHILE,
        }:
        compound_stmt_node = parser_compound_stmt()
        return Node("statement", children=[compound_stmt_node])
    else:
        simple_stmt_node = parser_simple_stmt()
        if MatchToken(TokenType.NEWLINE) or MatchToken(TokenType.END) or MatchToken(TokenType.RBRACE):
            node = Node(str(TokenType.NEWLINE), children=[], value=Token(TokenType.NEWLINE, "\n", tokenNow.linenum))
            if MatchToken(TokenType.NEWLINE):
                FetchToken()
            return Node("statement", children=[simple_stmt_node, node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.NEWLINE received ", tokenNow.tokenType)
            exit(0)

def parser_statements_rest():
    # statements_rest->  /* empty */| statements
    if MatchToken(TokenType.NEWLINE) or MatchToken(TokenType.END) or MatchToken(TokenType.RBRACE):
        pass
    else:
        statements_node = parse_statements()
        return Node("statements_rest", children=[statements_node])

def parser_compound_stmt():
    # compound_stmt-> function_def| if_stmt| for_stmt| while_stmt
    if tokenNow.tokenType==TokenType.DEF:
        function_def_node = parser_function_def()
        return Node("compound_stmt", children=[function_def_node])
    elif tokenNow.tokenType==TokenType.IF:
        if_stmt_node = parser_if_stmt()
        return Node("compound_stmt", children=[if_stmt_node])
    elif tokenNow.tokenType==TokenType.FOR:
        for_stmt_node = parser_for_stmt()
        return Node("compound_stmt", children=[for_stmt_node])
    elif tokenNow.tokenType==TokenType.WHILE:
        while_stmt_node = parser_while_stmt()
        return Node("compound_stmt", children=[while_stmt_node])


def parser_simple_stmt():
    # simple_stmt-> identifier_stmt| atom_rest expr_rest
    # |NOT inversion|PLUS factor| MINUS factor
    # | return_stmt| import_stmt| PASS| BREAK| CONTINUE| global_stmt
    if tokenNow.tokenType==TokenType.IDENTIFIER:
        identifier_stmt_node = parser_identifier_stmt()
        return Node("simple_stmt", children=[identifier_stmt_node])
    elif MatchToken(TokenType.NOT):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        inversion_node = parser_inversion()
        return Node("simple_stmt", children=[node, inversion_node])
    elif MatchToken(TokenType.PLUS) or MatchToken(TokenType.MINUS):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        factor_node = parser_factor()
        return Node("simple_stmt", children=[node, factor_node])
    elif tokenNow.tokenType==TokenType.RETURN:
        return_stmt_node = parser_return_stmt()
        return Node("simple_stmt", children=[return_stmt_node])
    elif tokenNow.tokenType==TokenType.IMPORT:
        import_stmt_node = parser_import_stmt()
        return Node("simple_stmt", children=[import_stmt_node])
    # elif tokenNow.tokenType==TokenType.GLOBAL:
    #     global_stmt_node = parser_global_stmt()
    #     return Node("simple_stmt", children=[global_stmt_node])
    elif tokenNow.tokenType in {
        TokenType.PASS, TokenType.BREAK, TokenType.CONTINUE
    }:
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("simple_stmt", children=[node])
    else:
        atom_rest_node = parser_atom_rest()
        expr_rest = parser_expr_rest()
        return Node("simple_stmt", children=[atom_rest_node, expr_rest])

def parser_identifier_stmt():
    # identifier_stmt-> IDENTIFIER identifier_opt
    MatchToken(TokenType.IDENTIFIER)
    node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
    FetchToken()
    identifier_opt_node = parser_identifier_opt()
    return Node("identifier_stmt", children=[node, identifier_opt_node])

def parser_identifier_opt():
    # identifier_opt-> ASSIGN expression| AUGASSIGN expression| expr_rest
    if MatchToken(TokenType.ASSIGN):
        node = Node(str(tokenNow.tokenType), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        return Node("identifier_opt", children=[node, expression_node])
    elif MatchToken(TokenType.AUGASSIGN):
        node = Node(str(tokenNow.tokenType), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        return Node("identifier_opt", children=[node, expression_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ, TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ,
        TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.POWER,
        TokenType.DOT, TokenType.LPAREN, TokenType.LBRACKET
    }:
        expr_rest_node = parser_expr_rest()
        return Node("identifier_opt", children=[expr_rest_node])

def parser_expr_rest():
    # expr_rest-> /* 空 */
    if tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    # expr_rest->(OR|AND|NOT|EQ...)expression
    elif tokenNow.tokenType in {
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ,
        TokenType.LT, TokenType.LTEQ, TokenType.RT, TokenType.RTEQ,
        TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.POWER,
    }:
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        exp_node = parser_expression()
        return Node("expr_rest", children=[node, exp_node])
    # DOT IDENTIFIER object_rest
    elif MatchToken(TokenType.DOT):
        dot_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            object_rest_node = parser_object_rest()
            return Node("expr_rest", children=[dot_node, id_node, object_rest_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)
    #  LPAREN arguments RPAREN
    elif MatchToken(TokenType.LPAREN):
        lparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        arguments_node = parser_arguments()
        if MatchToken(TokenType.RPAREN):
            rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("expr_rest", children=[lparen_node, arguments_node, rparen_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN received ",
                  tokenNow.tokenType)
            exit(0)
    # LBRACKET slices RBRACKET
    else:
        lbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        slices_node = parser_slices()
        if MatchToken(TokenType.RBRACKET):
            rbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("expr_rest", children=[lbracket_node, slices_node, rbracket_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RBRACKET received ",
                  tokenNow.tokenType)
            exit(0)

def parser_object_rest():
    # object_rest-> /* 空 */| LPAREN arguments RPAREN
    if tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,
    }:
        pass
    elif MatchToken(TokenType.LPAREN):
        lparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        arguments_node = parser_arguments()
        if MatchToken(TokenType.RPAREN):
            rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("object_rest", children=[lparen_node, arguments_node, rparen_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN received ",
                  tokenNow.tokenType)
            exit(0)

def parser_block():
    # block-> NEWLINE LBRACE statements RBRACE
    if MatchToken(TokenType.NEWLINE):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.LBRACE):
            lbrace_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            statements_node = parse_statements()
            if(MatchToken(TokenType.RBRACE)):
                rbrace_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                FetchToken()
                if MatchToken(TokenType.NEWLINE):
                    newline_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                    FetchToken()
                    return Node("block", children=[lbrace_node, statements_node, rbrace_node, newline_node])
                else:
                    print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.NEWLINE received ",
                          tokenNow.tokenType)
                    exit(0)
            else:
                print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RBRACE received ",
                      tokenNow.tokenType)
                exit(0)
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.LBRACE received ",
                  tokenNow.tokenType)
            exit(0)


def parser_expression():
    # expression-> disjunction
    disjunction_node = parser_disjunction()
    return Node("expression", children=[disjunction_node])

def parser_disjunction():
    # disjunction-> conjunction disjunction_rest
    conjunction_node = parser_conjunction()
    disjunction_rest_node = parser_disjunction_rest()
    return Node("disjunction", children=[conjunction_node, disjunction_rest_node])

def parser_disjunction_rest():
    # disjunction_rest-> OR conjunction| /* 空 */
    if MatchToken(TokenType.OR):
        or_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        conjunction_node = parser_conjunction()
        return Node("disjunction_rest", children=[or_node, conjunction_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_conjunction():
    # conjunction-> inversion conjunction_rest
    inversion_node = parser_inversion()
    conjunction_rest_node = parser_conjunction_rest()
    return Node("conjunction", children=[inversion_node, conjunction_rest_node])

def parser_conjunction_rest():
    # conjunction_rest->  AND inversion|  /* 空 */
    if MatchToken(TokenType.AND):
        and_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        inversion_node = parser_inversion()
        return Node("conjunction_rest", children=[and_node, inversion_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.OR,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_inversion():
    # inversion-> NOT inversion| comparison
    if MatchToken(TokenType.NOT):
        not_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        inversion_node = parser_inversion()
        return Node("inversion", children=[not_node, inversion_node])
    else:
        comparison_node = parser_comparison()
        return Node("inversion", children=[comparison_node])

def parser_comparison():
    # comparison-> sum comparison_rest
    sum_node = parser_sum()
    comparison_rest_node = parser_comparison_rest()
    return Node("comparison", children=[sum_node, comparison_rest_node])

def parser_comparison_rest():
    # comparison_rest-> /* 空 */|EQ sum| NOTEQ sum| LTEQ sum| LT sum| RT sum| RTEQ sum
    if tokenNow.tokenType in {
        TokenType.EQ, TokenType.NOTEQ,
        TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ
    }:
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        sum_node = parser_sum()
        return Node("comparison_rest", children=[node, sum_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.OR, TokenType.NOT, TokenType.AND,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_sum():
    # sum-> term sum_prime
    term_node = parser_term()
    sum_prime_node = parser_sum_prime()
    return Node("sum", children=[term_node, sum_prime_node])

def parser_sum_prime():
    # sum_prime-> sum_rest sum_prime| /* 空 */
    if tokenNow.tokenType==TokenType.PLUS or tokenNow.tokenType==TokenType.MINUS:
        sum_rest_node = parser_sum_rest()
        sum_prime_node = parser_sum_prime()
        return Node("sum_prime", children=[sum_rest_node, sum_prime_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ, TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_sum_rest():
    # sum_rest-> PLUS term| MINUS term
    if MatchToken(TokenType.PLUS) or MatchToken(TokenType.MINUS):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        term_node = parser_term()
        return Node("sum_rest", children=[node, term_node])

def parser_term():
    # term-> factor term_prime
    factor_node = parser_factor()
    term_prime_node = parser_term_prime()
    return Node("term", children=[factor_node, term_prime_node])

def parser_term_prime():
    # term_prime-> term_rest term_prime| /* 空 */
    if tokenNow.tokenType==TokenType.TIMES or tokenNow.tokenType==TokenType.DIVIDE:
        term_rest_node = parser_term_rest()
        term_prime_node = parser_term_prime()
        return Node("term_prime", children=[term_rest_node, term_prime_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.PLUS, TokenType.MINUS,
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ, TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)


def parser_term_rest():
    # term_rest: TIMES factor| DIVIDE factor
    if MatchToken(TokenType.TIMES) or MatchToken(TokenType.DIVIDE):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        factor_node = parser_factor()
        return Node("term_rest", children=[node, factor_node])

def parser_factor():
    # factor-> PLUS factor| MINUS factor| power
    if MatchToken(TokenType.PLUS) or MatchToken(TokenType.MINUS):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        factor_node = parser_factor()
        return Node("factor", children=[node, factor_node])
    else:
        power_node = parser_power()
        return Node("factor", children=[power_node])

def parser_power():
    # power-> primary power_rest
    primary_node = parser_primary()
    power_rest_node = parser_power_rest()
    return Node("power", children=[primary_node, power_rest_node])

def parser_power_rest():
    # power_rest-> POWER factor| /* 空 */
    if MatchToken(TokenType.POWER):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        factor_node = parser_factor()
        return Node("power_rest", children=[node, factor_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ, TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_primary():
    # primary-> atom primary_rest
    atom_node = parser_atom()
    primary_rest_node = parser_primary_rest()
    return Node("primary", children=[atom_node, primary_rest_node])

def parser_primary_rest():
    # primary_rest->primary_operation primary_rest| /* 空 */
    if tokenNow.tokenType in {
        TokenType.DOT, TokenType.LPAREN, TokenType.LBRACKET
    }:
        primary_operation_node = parser_primary_operation()
        primary_rest_node = parser_primary_rest()
        return Node("primary_rest", children=[primary_operation_node, primary_rest_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE,TokenType.IN,
        TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.POWER,
        TokenType.OR, TokenType.AND, TokenType.NOT,
        TokenType.EQ, TokenType.NOTEQ, TokenType.LTEQ, TokenType.LT, TokenType.RT, TokenType.RTEQ,
        TokenType.RBRACKET, TokenType.COMMA, TokenType.RPAREN, TokenType.COLON
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)


def parser_primary_operation():
    # primary_operation-> DOT IDENTIFIER| LPAREN primary_lparen_rest| LBRACKET slices RBRACKET
    if MatchToken(TokenType.DOT):
        dot_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("primary_operation", children=[dot_node, id_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)
    elif MatchToken(TokenType.LPAREN):
        lparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        primary_lparen_rest_node = parser_primary_lparen_rest()
        return Node("primary_operation", children=[lparen_node, primary_lparen_rest_node])
    elif MatchToken(TokenType.LBRACKET):
        lbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        slices_node = parser_slices()
        if MatchToken(TokenType.RBRACKET):
            rbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("primary_operation", children=[lbracket_node, slices_node, rbracket_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RBRACKET received ",
                  tokenNow.tokenType)
            exit(0)

def parser_primary_lparen_rest():
    # primary_lparen_rest-> arguments RPAREN
    arguments_node = parser_arguments()
    if MatchToken(TokenType.RPAREN):
        rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("primary_lparen_rest", children=[arguments_node, rparen_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN received ",
              tokenNow.tokenType)
        exit(0)

def parser_slices():
    # slices-> expression slices_rest
    expression_node = parser_expression()
    slices_rest_node = parser_slices_rest()
    return Node("slices", children=[expression_node, slices_rest_node])

def parser_slices_rest():
    # slices_rest-> COMMA slices| /* 空 */
    if MatchToken(TokenType.COMMA):
        comma_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        slices_node = parser_slices()
        return Node("slices_rest", children=[comma_node, slices_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACKET
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_atom():
    # atom-> IDENTIFIER| TRUE| FALSE| NONE| NUMBER| STRING| tuple| list
    if tokenNow.tokenType in{
        TokenType.IDENTIFIER, TokenType.TRUE, TokenType.FALSE,
        TokenType.NONE, TokenType.NUMBER, TokenType.STRING,
    }:
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("atom", children=[node])
    elif tokenNow.tokenType==TokenType.LPAREN:
        tuple_node = parser_tuple()
        return Node("atom", children=[tuple_node])
    elif tokenNow.tokenType==TokenType.LBRACKET:
        list_node = parser_list()
        return Node("atom", children=[list_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_tuple():
    # tuple-> LPAREN tuple_rest
    if MatchToken(TokenType.LPAREN):
        lparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        tuple_rest_node = parser_tuple_rest()
        return Node("tuple", children=[lparen_node, tuple_rest_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.LPAREN received ",
              tokenNow.tokenType)
        exit(0)


def parser_tuple_rest():
    # tuple_rest-> RPAREN|  expressions RPAREN
    if MatchToken(TokenType.RPAREN):
        rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("tuple_rest", children=[rparen_node])
    else:
        expressions_node = parser_expressions()
        if MatchToken(TokenType.RPAREN):
            rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("tuple_rest", children=[expressions_node, rparen_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN received ",
                  tokenNow.tokenType)
            exit(0)


def parser_list():
    # list: LBRACKET list_rest
    if MatchToken(TokenType.LBRACKET):
        lbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        list_rest_node = parser_list_rest()
        return Node("list", children=[lbracket_node, list_rest_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.LBRACKET received ",
              tokenNow.tokenType)
        exit(0)



def parser_list_rest():
    # list_rest: RBRACKET| expressions RBRACKET
    if MatchToken(TokenType.RBRACE):
        rbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("list_rest", children=[rbracket_node])
    else:
        expressions_node = parser_expressions()
        if MatchToken(TokenType.RBRACKET):
            rbracket_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("list_rest", children=[expressions_node, rbracket_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RBRACKET received ",
                  tokenNow.tokenType)
            exit(0)

def parser_expressions():
    # expressions-> expression expressions_rest
    expression_node = parser_expression()
    expressions_rest_node = parser_expressions_rest()
    return Node("expressions", children=[expression_node, expressions_rest_node])

def parser_expressions_rest():
    # expressions_rest-> COMMA expression expressions_rest| /* 空 */
    if MatchToken(TokenType.COMMA):
        comma_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        expressions_rest_node = parser_expressions_rest()
        return Node("expressions_rest", children=[comma_node, expression_node, expressions_rest_node])
    elif tokenNow.tokenType in {
        TokenType.RPAREN, TokenType.RBRACKET,
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RBRACKET received ",
              tokenNow.tokenType)
        exit(0)

def parser_arguments():
    # arguments-> kwarg arguments_rest| /* 空 */
    if MatchToken(TokenType.RPAREN):
        pass
    else:
        kwarg_node = parser_kwarg()
        arguments_rest_node = parser_arguments_rest()
        return Node("arguments", children=[kwarg_node, arguments_rest_node])

def parser_arguments_rest():
    # arguments_rest-> COMMA arguments| /* 空 */
    if MatchToken(TokenType.COMMA):
        comma_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        arguments_node = parser_arguments()
        return Node("arguments_rest", children=[comma_node, arguments_node])
    elif MatchToken(TokenType.RPAREN):
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN 或 TokenType.COMMA received ",
              tokenNow.tokenType)
        exit(0)

def parser_kwarg():
    # kwarg-> IDENTIFIER kwarg_rest| atom_rest expr_rest
    # |NOT inversion|PLUS factor| MINUS factor
    if MatchToken(TokenType.IDENTIFIER):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        kwarg_rest_node = parser_kwarg_rest()
        return Node("kwarg", children=[node, kwarg_rest_node])
    elif MatchToken(TokenType.NOT):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        inversion_node = parser_inversion()
        return Node("kwarg", children=[node, inversion_node])
    elif MatchToken(TokenType.PLUS) or MatchToken(TokenType.MINUS):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        factor_node = parser_factor()
        return Node("kwarg", children=[node, factor_node])
    else:
        atom_rest_node = parser_atom_rest()
        expr_rest_node = parser_expr_rest()
        return Node("kwarg", children=[atom_rest_node, expr_rest_node])

def parser_atom_rest():
    # atom_rest: TRUE| FALSE| NONE| NUMBER| STRING| tuple| list
    if tokenNow.tokenType in{
        TokenType.TRUE, TokenType.FALSE,
        TokenType.NONE, TokenType.NUMBER, TokenType.STRING,
    }:
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        return Node("atom_rest", children=[node])
    elif tokenNow.tokenType==TokenType.LPAREN:
        tuple_node = parser_tuple()
        return Node("atom_rest", children=[tuple_node])
    elif tokenNow.tokenType==TokenType.LBRACKET:
        list_node = parser_list()
        return Node("atom_rest", children=[list_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)


def parser_kwarg_rest():
    # kwarg_rest-> ASSIGN expression| expr_rest
    if MatchToken(TokenType.ASSIGN):
        assign_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        return Node("kwarg_rest", children=[assign_node, expression_node])
    else:
        expr_rest_node = parser_expr_rest()
        return Node("kwarg_rest", children=[expr_rest_node])

def parser_return_stmt():
    # return_stmt-> RETURN expression
    if MatchToken(TokenType.RETURN):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        return Node("return_stmt", children=[node, expression_node])

def parser_import_stmt():
    # import_stmt->IMPORT dotted_as_names
    if MatchToken(TokenType.IMPORT):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        dotted_as_names_node = parser_dotted_as_names()
        return Node("import_stmt", children=[node, dotted_as_names_node])

def parser_dotted_as_names():
    # dotted_as_names->dotted_as_name dotted_as_names_rest
    dotted_as_name_node = parser_dotted_as_name()
    dotted_as_names_rest_node = parser_dotted_as_names_rest()
    return Node("dotted_as_names", children=[dotted_as_name_node, dotted_as_names_rest_node])

def parser_dotted_as_names_rest():
    # dotted_as_names_rest-> COMMA dotted_as_names|  /* 空 */
    if MatchToken(TokenType.COMMA):
        node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        dotted_as_names_node = parser_dotted_as_names()
        return Node("dotted_as_names_rest", children=[node, dotted_as_names_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_dotted_as_name():
    # dotted_as_name->dotted_name dotted_as_name_rest
    dotted_name_node = parser_dotted_name()
    dotted_as_name_rest = parser_dotted_as_name_rest()
    if dotted_as_name_rest!=None:
        dotted_name_node.imported_names = []
    return Node("dotted_as_name", children=[dotted_name_node, dotted_as_name_rest])

def parser_dotted_as_name_rest():
    # dotted_as_name_rest-> AS IDENTIFIER|  /* 空 */
    if MatchToken(TokenType.AS):
        as_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("dotted_as_name_rest", children=[as_node, id_node], imported_names=[id_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.COMMA
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_dotted_name():
    # dotted_name: IDENTIFIER dotted_name_rest
    if MatchToken(TokenType.IDENTIFIER):
        id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        dotted_name_rest_node = parser_dotted_name_rest()
        return Node("dotted_name", children=[id_node, dotted_name_rest_node], imported_names=[id_node])
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
              tokenNow.tokenType)
        exit(0)


def parser_dotted_name_rest():
    # dotted_name_rest-> DOT IDENTIFIER |  /* 空 */
    if MatchToken(TokenType.DOT):
        dot_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            return Node("dotted_name_rest", children=[dot_node, id_node] )
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.COMMA, TokenType.AS
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)


def parser_function_def():
    # function_def-> DEF IDENTIFIER LPAREN arguments RPAREN COLON block
    if MatchToken(TokenType.DEF):
        def_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            if MatchToken(TokenType.LPAREN):
                lparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                FetchToken()
                arguments_node = parser_arguments()
                if MatchToken(TokenType.RPAREN):
                    rparen_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                    FetchToken()
                    if MatchToken(TokenType.COLON):
                        colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                        FetchToken()
                        block_node = parser_block()
                        return Node("function_def", children=[def_node, id_node, lparen_node, arguments_node, rparen_node, colon_node, block_node])
                    else:
                        print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                              tokenNow.tokenType)
                        exit(0)
                else:
                    print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.RPAREN received ",
                          tokenNow.tokenType)
                    exit(0)
            else:
                print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.LPAREN received ",
                      tokenNow.tokenType)
                exit(0)
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)


def parser_if_stmt():
    # if_stmt-> IF expression COLON block if_stmt_rest
    if MatchToken(TokenType.IF):
        if_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        if MatchToken(TokenType.COLON):
            colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            block_node = parser_block()
            if_stmt_rest_node = parser_if_stmt_rest()
            return Node("if_stmt", children=[if_node, expression_node, colon_node, block_node, if_stmt_rest_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                  tokenNow.tokenType)
            exit(0)

def parser_if_stmt_rest():
    # if_stmt_rest-> elif_stmt | else_block | /* 空 */
    if tokenNow.tokenType==TokenType.ELIF:
        elif_stmt_node = parser_elif_stmt()
        return Node("if_stmt_rest", children=[elif_stmt_node])
    elif tokenNow.tokenType==TokenType.ELSE:
        else_block_node = parser_else_block()
        return Node("else_block_node", children=[else_block_node])
    elif tokenNow.tokenType in {
        TokenType.NEWLINE, TokenType.END, TokenType.RBRACE
    }:
        pass
    else:
        print("line " + str(tokenNow.linenum) + " 语法错误：received ",
              tokenNow.tokenType)
        exit(0)

def parser_elif_stmt():
    # elif_stmt: ELIF expression COLON block if_stmt_rest
    if MatchToken(TokenType.ELIF):
        elif_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        if MatchToken(TokenType.COLON):
            colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            block_node = parser_block()
            if_stmt_rest_node = parser_if_stmt_rest()
            return Node("elif_stmt", children=[elif_node, expression_node, colon_node, block_node, if_stmt_rest_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                  tokenNow.tokenType)
            exit(0)

def parser_else_block():
    # else_block-> ELSE COLON block
    if MatchToken(TokenType.ELSE):
        else_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.COLON):
            colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            block_node = parser_block()
            return Node("else_block", children=[else_node, colon_node, block_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                  tokenNow.tokenType)
            exit(0)

def parser_for_stmt():
    # for_stmt: FOR IDENTIFIER IN expression COLON block
    if MatchToken(TokenType.FOR):
        for_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        if MatchToken(TokenType.IDENTIFIER):
            id_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            if MatchToken(TokenType.IN):
                in_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                FetchToken()
                expression_node = parser_expression()
                if MatchToken(TokenType.COLON):
                    colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
                    FetchToken()
                    block_node = parser_block()
                    return Node("for_stmt", children=[for_node, id_node, in_node, expression_node, colon_node, block_node])
                else:
                    print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                          tokenNow.tokenType)
                    exit(0)
            else:
                print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IN received ",
                      tokenNow.tokenType)
                exit(0)
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.IDENTIFIER received ",
                  tokenNow.tokenType)
            exit(0)


def parser_while_stmt():
    # while_stmt: WHILE expression COLON block
    if MatchToken(TokenType.WHILE):
        while_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
        FetchToken()
        expression_node = parser_expression()
        if MatchToken(TokenType.COLON):
            colon_node = Node(str(tokenNow.tokenType.name), children=[], value=tokenNow)
            FetchToken()
            block_node = parser_block()
            return Node("for_stmt", children=[while_node, expression_node, colon_node, block_node])
        else:
            print("line " + str(tokenNow.linenum) + " 语法错误：Expected TokenType.COLON received ",
                  tokenNow.tokenType)
            exit(0)


def Parser(string):
    global tokenIter  # 正确缩进，与函数内其他代码对齐

    # 调用词法分析器得到记号表
    tokenList = Lexer(string)
    tokenIter = iter(tokenList)

    FetchToken()
    return parse_program()



def getPaserTree():
    str = read_file_to_string("test.py")
    str = filterComment(str)
    write_string_to_file(str, "test_filter.py")
    tree = Parser(str)
    tree.print_tree(0)
    return tree

getPaserTree()
