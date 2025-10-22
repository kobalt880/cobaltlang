class VariableError(Exception):
    pass


class CobaltLang:
    def __init__(self):
        self._variables = {'i': 0}
        
    def command(self, command: str):
        # executing test
        if command == '' or command == '#':
            return

        # function and spliting test
        if command[:4] != 'func' and command[:3] != 'str':
            commands = command.split(',')
        else:
            commands = [command]
        
        for command in commands:
            command = command.split()
            times = 1
            chan_var = 'i'

            # cycle test
            if command[0] == 'repeat' and command[1] != '' and command[2] == 'times':
                iter_info = command[1].split('-')
                
                if iter_info[0].isdigit():
                    times = int(iter_info[0])
                elif iter_info[0] in self._variables.keys():
                    times = self._variables[iter_info[0]]
                else:
                    raise VariableError(f'Variable {iter_info[0]} is not exists')

                if len(iter_info) >= 2:
                    chan_var = iter_info[1]
                command = command[3:]

            # start executing
            for i in range(times):
                if times > 1 or chan_var != 'i':
                    self._variables[chan_var] = i

                # define command
                match command[0]:
                    case 'show':
                        try:
                            variable = self._variables[command[1]]
                            print(variable)
                        except KeyError:
                            raise VariableError(f'Variable {command[1]} is not exists')
                
                    case 'remove':
                        try:
                            del self._variables[command[1]]
                        except KeyError:
                            raise VariableError(f'Variable {command[1]} is not exists')
                
                    case 'int':
                        try:
                            var_info = ''.join(command[1:]).split('=')
                            assert len(var_info) == 2
                    
                            var_name = var_info[0]
                            var_value = self.__calculate(var_info[1])
                            self._variables[var_name] = var_value

                        except AssertionError:
                            raise SyntaxError
                
                        except ValueError:
                            raise ValueError('Integer variable can contain only numbers')

                    case 'str':
                        try:
                            var_info = ' '.join(command[1:]).split('=')
                            assert len(var_info) >= 2
                    
                            var_name = var_info[0].replace(' ', '')
                            var_value = '='.join(var_info[1:]).strip()
                            self._variables[var_name] = var_value
    
                        except AssertionError:
                            raise SyntaxError('String var is not created: invalid syntax')
                    
                    case 'comp':
                        try:
                            var_info = ''.join(command[1:]).split('=')
                            assert len(var_info) == 2
                            
                            var_name = var_info[0]
                            var_value = self.__calc_comparison(var_info[1])
                            self._variables[var_name] = var_value
                        except AssertionError:
                            raise SyntaxError('Comparison var is not created: invalid syntax')

                    case 'bool':
                        try:
                            var_info = ''.join(command[1:]).split('=')
                            assert len(var_info) == 2
                            
                            var_name = var_info[0]
                            var_value = self.__calc_bool_exp(var_info[1])
                            self._variables[var_name] = var_value
                        except AssertionError:
                            raise SyntaxError('Boolean var is not created: invalid syntax')

                    case 'int-input':
                        try:
                            var_name = command[1]
                            var_value = int(input('>> '))
                            self.command(f'int {var_name} = {var_value}')
                            
                        except IndexError:
                            raise SyntaxError('Variable name not given')

                        except ValueError:
                            raise ValueError('Integer expected')

                    case 'func':
                        func_info = command[1:]
                        func_name = func_info[0]
                        func_code = ' '.join(func_info[1:])
                        self._variables[func_name] = lambda: self.command(func_code)

                    case 'call':
                        try:
                            func_name = command[1]
                            self._variables[func_name]()
                        except KeyError:
                            raise NameError('Function not found')

                    case 'if':
                        if_block = ' '.join(command[1:]).split(' then ')
                        if_block = [if_block[0]] + if_block[1].split(' else ')
                        expression = if_block[0].strip()
                        action = if_block[1].strip()
                        else_action = if_block[2].strip()

                        if self.__calc_bool_exp(expression):
                            self.command(action)
                        else:
                            self.command(else_action)
                        
                    case _:
                        raise SyntaxError('Invalid command')

            # zeroing out variable
            if times > 1:
                self._variables['i'] = 0
            
    def interprent(self, code: str):
        strings = code.split('\n')

        for string_number, string in enumerate(strings):
            try:
                self.command(string)
            except (SyntaxError, VariableError, NameError, ValueError) as er:
                print(f'Exception on {string_number + 1}th string: {er}')
                break


    def __compress_result(self, result: list) -> list:
        first, sign, second = result[:3]
        new_num = None
            
        match sign:
            case '-':
                new = first - second
            case '+':
                new = first + second
            case '*':
                new = first * second
            case '/':
                new = first / second
            case '^':
                new = first ** second
            case '%':
                new = first % second
            case ':':
                new = first // second
            case '--':
                new = first == second
            case '!-':
                new = first != second
            case '<<':
                new = first < second
            case '>>':
                new = first > second
            case '<-':
                new = first <= second
            case '>-':
                new = first >= second
            case '&':
                new = first and second
            case '|':
                new = first or second
            case _:
                raise SyntaxError('Operation {sign} is not exists')

        return [new, result[-1]] 
        

    def __calculate(self, string: str) -> int:
        if string[0] == '-':
            string = '0' + string
            
        string = string.replace(' ', '') + '\\'
        number = ''
        result = []
        while string != '':
            number += string[0]
            string = string[1:]
            
            if number[-1] in ['+', '-', '*', '/', '^', '%', ':', '\\']:
                var = number[:-1]
                        
                if var.isdigit():
                    var = int(var)
                elif var in self._variables.keys():
                    var = self._variables[var]
                elif var == '':
                    raise SyntaxError('Incorrectly entered expression')
                else:
                    raise VariableError(f'Variable {var} is not exists')
                            
                result.append(var)
                result.append(number[-1])
                number = ''

                if len(result) == 4:
                    result = self.__compress_result(result)
                    
        return result[0]

    def __calc_comparison(self, string: str) -> bool:
        string = string.replace(' ', '') + '\\'
        result = []
        exp = ''

        while string != '':
            exp += string[0]
            string = string[1:]

            if exp[-1] in ['<', '>', '-', '!', '\\']:
                var = exp[:-1]
                
                if exp[-1] != '\\':
                    exp += string[0]
                    string = string[1:]

                if var.isdigit():
                    var = int(var)
                elif var == 'true':
                    var = True
                elif var == 'false':
                    var = False
                elif var in self._variables.keys():
                    var = self._variables[var]
                elif var == '':
                    raise SyntaxError('Incorrectly entered expression')
                else:
                    raise VariableError(f'Variable {var} is not exists')
                
                result.append(var)
                result.append(exp[-2:])
                exp = ''

                if len(result) == 4:
                    result = self.__compress_result(result)

        return result[0]

    def __calc_bool_exp(self, string: str) -> bool:
        string = string.replace(' ', '') + '\\'
        result = []
        exp = ''

        while string != '':
            exp += string[0]
            string = string[1:]

            if exp[-1] in ['&', '|', '\\']:
                var = exp[:-1]
                swap = var[0] == '!'
                if swap: var = var[1:]

                if var in self._variables.keys():
                    var = bool(self._variables[var])
                elif var == 'true':
                    var = True
                elif var == 'false':
                    var = False
                else:
                    raise VariableError(f'Variable {var} is not exists')
                
                if swap: var = not var
                
                result.append(var)
                result.append(exp[-1])
                exp = ''

                if len(result) == 4:
                    result = self.__compress_result(result)

        return result[0]
                
