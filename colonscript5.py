ConstantTokens = {
    ":": "colon",
    ",": "comma"
}
Digits = "1234567890"
Quotes = "\"'"
WhitelistedChar = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm_"

class Token:
    def __init__(self,type_:str,value=""):
        self.type = type_
        self.value = value
    def __repr__(self):
        return "{}:{}".format(self.type,self.value) if self.value != "" else self.type
class Lexer:
    def __init__(self,line):
        self.line = line
        self.tokens = []

        self.pos = 0
        self.char = line[0]

    def set_line(self,line):
        self.__init__(line)
    
    def advance(self):
        self.pos += 1
        self.char = self.line[self.pos] if self.pos <= len(self.line)-1 else None

    def create_number(self):
        numberstr = ""
        isfloat = False
        while True:
            if self.char == ".":
                isfloat = True
            numberstr += self.char
            self.advance()

            if self.char is None or (not self.char in Digits+"."):
                break
        
        if isfloat:
            return Token("float",float(numberstr))
        else:
            return Token("integer",int(numberstr))
    
    def create_string(self):
        quote = self.char
        string = ""
        self.advance()
        while True:
            if not (self.char == "\\" and self.line[self.pos-1] != "\\") and self.pos<len(self.line):
                string += self.char

            self.advance()

            if (self.char == quote and self.line[self.pos-1] != "\\") or self.pos>=len(self.line):
                self.advance()
                break
        
        return Token("string",str(string))
    
    def value_token(self,tok,skip_first_char=False):
        keyword = ""
        if skip_first_char: self.advance()

        while True:
            keyword += self.char
            self.advance()

            if self.char is None or (not self.char in WhitelistedChar+Digits):
                break

        return Token(tok,str(keyword))

    def create_tokens(self):
        def create_token():
            if self.char in Quotes:
                self.tokens.append(self.create_string())
            elif self.char in Digits:
                self.tokens.append(self.create_number())
            elif self.char in WhitelistedChar:
                self.tokens.append(self.value_token("keyword"))
            elif self.char == "$":
                self.tokens.append(self.value_token("reference",True))
            elif ConstantTokens.get(self.char,False):
                self.tokens.append(Token(ConstantTokens[self.char]))
                self.advance()
            else:
                self.advance()
        while True:
            if self.char is None or self.char == None:
                break
            if self.char.isspace():
                self.advance()
                continue
            create_token()

class Parent:
    def __init__(self):
        self.functions = {}
class ColonScript5:
    def __init__(self,lines:list[str]):
        self.lines = lines
        self.lexer = Lexer(lines[0])
        self.variables = {}
        self.parents = {}
        self.line_index = 0
    def bind_function(self,parent,function_name,function):
        self.parents[parent].functions[function_name]= function

    def interpret_lines(self):
        def interpret_tokens():

            lexer_tokens = self.lexer.tokens
            perceived_tokens = []
            for token in lexer_tokens:
                if token.type == "reference":
                    try:
                        perceived_tokens.append(self.variables[token.value])
                    except KeyError as e:
                        print("Line {}: {} is not a valid variable".format(self.line_index,e))
                else:
                    perceived_tokens.append(token)
            pointer = 0
            if (
                perceived_tokens[pointer].type=="keyword"
            ):
                if (
                    perceived_tokens[pointer+1].type=="colon" and
                    perceived_tokens[pointer+2].type=="keyword"
                ):
                    parent = perceived_tokens[pointer].value
                    child = perceived_tokens[pointer+2].value
                else:
                    parent = "orphanage"
                    child = perceived_tokens[pointer].value
                
                pointer += 3

                arguments = []
                while True:
                    arguments.append(perceived_tokens[pointer])
                    pointer += 1
                    if pointer >= len(perceived_tokens):
                        break
                    if perceived_tokens[pointer].type == "comma":
                        pointer += 1

                try:
                    self.parents[parent].functions[child](*arguments)
                except Exception as e:
                    print(perceived_tokens)
                    print("Line {}: {}".format(self.line_index,e))

        self.line_index = 0
        while self.line_index < len(self.lines):
            if self.lines[self.line_index].strip() == "":
                self.line_index += 1
                continue
            self.lexer.set_line(self.lines[self.line_index])
            self.lexer.create_tokens()
            interpret_tokens()
            self.line_index += 1
    
    def create_functions(self):
        def log(token):
            if token.value == "":
                print("Line {}: Expected a token with a value, got {} instead.".format(self.line_index,token))
            else:
                print(token.value)
        def set_variable(variable_name,new_value):
            if variable_name.type != "keyword":
                print("Line {}: Expected the variable_name type to be 'keyword', got {} instead.".format(self.line_index,variable_name))
                return
            if new_value.value == "":
                print("Line {}: Expected a token with a value, got {} instead.".format(self.line_index,new_value))
                return
            self.variables[variable_name.value] = new_value
        def add(variable_name,add_by):
            variable = self.variables[variable_name.value]
            varval = variable.value

            self.variables[variable_name.value] = Token(variable.type,varval+(str(add_by.value) if variable.type=="string" else add_by.value))
        def subtract(variable_name,take_away):
            variable = self.variables[variable_name.value]
            varval = variable.value

            self.variables[variable_name.value] = Token(variable.type,varval-take_away.value)
        def multiply(variable_name,multiply_by):
            variable = self.variables[variable_name.value]
            varval = variable.value

            self.variables[variable_name.value] = Token(variable.type,varval*multiply_by.value)
        def divide(variable_name,divide_by):
            variable = self.variables[variable_name.value]
            varval = variable.value

            self.variables[variable_name.value] = Token(variable.type,varval/divide_by.value)
        def goto(number):
            if number.type != "integer":
                print("Line {}: Expected the goto number type to be 'integer', got {} instead.".format(self.line_index,number))
            self.line_index = number.value
        def goto_conditional(left_compare,right_compare,number):
            if number.type != "integer":
                print("Line {}: Expected the goto number type to be 'integer', got {} instead.".format(self.line_index,number))
            if left_compare.value == right_compare.value:
                goto(number)
        def goto_iconditional(left_compare,right_compare,number):
            if number.type != "integer":
                print("Line {}: Expected the goto number type to be 'integer', got {} instead.".format(self.line_index,number))
            if left_compare.value != right_compare.value:
                goto(number)
        def keyword(variable_name,string):
            if string.type != "string":
                print("Line {}: Expected the type to be 'string', got {} instead.".format(self.line_index,string))
            if variable_name.type != "keyword":
                print("Line {}: Expected variable_name type to be 'keyword', got {} instead.".format(self.line_index,variable_name))
            self.variables[variable_name.value]=Token("keyword",string.value)
        def reference(variable_name,string):
            self.variables[variable_name.value]=self.variables[string.value]


        self.parents["o"]=Parent()
        self.parents["console"]=Parent()
        self.parents["console"].functions={
            "log":log
        }
        self.parents["variable"]=Parent()
        self.parents["variable"].functions={
            "set":set_variable,
            "add":add,
            "subtract":subtract,
            "multiply":multiply,
            "divide":divide,
            "keyword": keyword,
            "reference": reference
        }
        self.parents["o"].functions={
            "goto": goto,
            "iconditional": goto_iconditional,
            "conditional": goto_conditional
        }