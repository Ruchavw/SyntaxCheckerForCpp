from ply import lex, yacc

# Token list 
tokens = (
    'TYPE',          # int, float
    'ID',            # identifiers
    'NUMBER',        # numbers
    'EQUALS',        # =
    'SEMICOLON',     # ;
    'COUT',          # cout
    'CIN',           # cin
    'STRING',        # "hello"
    'LSHIFT',        # <<
    'RSHIFT',        # >>
    'LPAREN',        # (
    'RPAREN',        # )
    'LBRACE',        # {
    'RBRACE',        # }
    'CLASS',         # class
    'PUBLIC',        # public
    'PRIVATE',       # private
    'PROTECTED',     # protected
    'COLON',         # :
    'RETURN',        # return
    'COMMA',         # ,
)

# Token rules 
def t_TYPE(t):
    r'int|float|void'
    return t

def t_CLASS(t):
    r'class'
    return t

def t_PUBLIC(t):
    r'public'
    return t

def t_PRIVATE(t):
    r'private'
    return t

def t_PROTECTED(t):
    r'protected'
    return t

def t_COUT(t):
    r'cout'
    return t

def t_CIN(t):
    r'cin'
    return t

def t_RETURN(t):
    r'return'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_STRING(t):
    r'"[^"]*"'
    return t

def t_NUMBER(t):
    r'\d*\.?\d+'
    t.value = float(t.value)
    return t

# Simple tokens 
t_EQUALS = r'='
t_SEMICOLON = r';'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_COLON = r':'
t_COMMA = r','
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# parser rules
def p_program(p):
    '''
    program : statement
            | program statement
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''
    statement : declaration
              | cout_statement
              | cin_statement
              | function_declaration
              | class_declaration
    '''
    p[0] = p[1]

def p_declaration(p):
    '''
    declaration : TYPE variable_list SEMICOLON
    '''
    p[0] = {
        'type': 'multiple_declaration',
        'var_type': p[1],
        'declarations': p[2],
        'line': p.lineno(1)
    }

def p_variable_list(p):
    '''
    variable_list : variable_declaration
                 | variable_list COMMA variable_declaration
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_variable_declaration(p):
    '''
    variable_declaration : ID
                       | ID EQUALS NUMBER
    '''
    if len(p) == 2:
        p[0] = {
            'name': p[1],
            'value': None
        }
    else:
        p[0] = {
            'name': p[1],
            'value': p[3]
        }

def p_cout_statement(p):
    '''
    cout_statement : COUT LSHIFT output_item SEMICOLON
    '''
    p[0] = {
        'type': 'output',
        'value': p[3],
        'line': p.lineno(1)
    }

def p_output_item(p):
    '''
    output_item : STRING
                | ID
                | NUMBER
    '''
    p[0] = p[1]

def p_cin_statement(p):
    '''
    cin_statement : CIN RSHIFT ID SEMICOLON
    '''
    p[0] = {
        'type': 'input',
        'variable': p[3],
        'line': p.lineno(1)
    }

def p_function_declaration(p):
    '''
    function_declaration : TYPE ID LPAREN parameter_list_opt RPAREN LBRACE function_body RBRACE
    '''
    p[0] = {
        'type': 'function_declaration',
        'return_type': p[1],
        'name': p[2],
        'parameters': p[4] if p[4] else [],
        'body': p[7],
        'line': p.lineno(1)
    }

def p_parameter_list_opt(p):
    '''
    parameter_list_opt : parameter_list
                      |
    '''
    p[0] = p[1] if len(p) > 1 else []

def p_parameter_list(p):
    '''
    parameter_list : TYPE ID
                  | parameter_list COMMA TYPE ID
    '''
    if len(p) == 3:
        p[0] = [{'type': p[1], 'name': p[2]}]
    else:
        p[0] = p[1] + [{'type': p[3], 'name': p[4]}]

def p_function_body(p):
    '''
    function_body : statement
                 | function_body statement
                 | return_statement
                 | function_body return_statement
                 |
    '''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_return_statement(p):
    '''
    return_statement : RETURN expression SEMICOLON
    '''
    p[0] = {
        'type': 'return',
        'value': p[2],
        'line': p.lineno(1)
    }

def p_expression(p):
    '''
    expression : NUMBER
               | ID
    '''
    p[0] = p[1]

def p_class_declaration(p):
    '''
    class_declaration : CLASS ID LBRACE class_body RBRACE SEMICOLON
    '''
    p[0] = {
        'type': 'class_declaration',
        'name': p[2],
        'body': p[4],
        'line': p.lineno(1)
    }

def p_class_body(p):
    '''
    class_body : access_specifier_section
               | class_body access_specifier_section
               |
    '''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_access_specifier_section(p):
    '''
    access_specifier_section : access_specifier COLON member_list
    '''
    p[0] = {
        'type': 'access_section',
        'access': p[1],
        'members': p[3]
    }

def p_access_specifier(p):
    '''
    access_specifier : PUBLIC
                    | PRIVATE
                    | PROTECTED
    '''
    p[0] = p[1].lower()

def p_member_list(p):
    '''
    member_list : declaration
                | member_list declaration
                | function_declaration
                | member_list function_declaration
                |
    '''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_error(p):
    if p:
        print(f"Syntax error at line {p.lineno}, token={p.type}, value='{p.value}'")
    else:
        print("Syntax error at EOF")

# Build lexer and parser
lexer = lex.lex()
parser = yacc.yacc()

def parse_cpp(text):
    return parser.parse(text, lexer=lexer)

# Example usage and testing
if __name__ == "__main__":
    test_input_valid = """
    class Student {
        private:
            int id, roll_number;
            float gpa, score, grade;
        
        public:
            int getId, setId;
            float getGpa, setGpa;
        
        protected:
            int age, semester;
    };

    int main() {
        float score = 95.5, grade = 4.0, gpa;
        int count = 1, total = 100, passed = 0;
        cout << "Enter score: ";
        cin >> score;
        return 0;
    }
    """
    
    test_input_invalid ="""
    class Student {
        private:
            int id, roll_number;
            float gpa, score, grade;
            int 23c;
        
        public:
            int getId, setId;
            float getGpa, setGpa;
            void myFunc();
        
        protected:
            int age, semester;
            
        unprotected:
            int maze;
    };
    
    void myFunc
    {
        cout << "Hello";
    }
    
    int main() {
        float score = 95.5, grade = 4.0, gpa;
        int count = 1, total = 100, passed = 0;
        cout << "Welcome"
        cout << "Enter score: ";
        cin >> score;
        cin > semester;
        return 0;
    }
    """
    
    result_valid = parse_cpp(test_input_valid)
    result_invalid = parse_cpp(test_input_invalid)
    
    def print_parsed_item(item, indent=0):
        indent_str = "  " * indent
        if isinstance(item, dict):
            print(f"{indent_str}Type: {item.get('type', 'unknown')}")
            for key, value in item.items():
                if key != 'type':
                    if isinstance(value, (list, dict)):
                        print(f"{indent_str}{key}:")
                        print_parsed_item(value, indent + 1)
                    else:
                        print(f"{indent_str}{key}: {value}")
        elif isinstance(item, list):
            for subitem in item:
                print_parsed_item(subitem, indent)

    print("\nParsed C++ Code:")
    print("=" * 50)
    print_parsed_item(result_invalid)
    print_parsed_item(result_valid)
    
