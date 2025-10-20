class VariableError(Exception):
    pass


class CobaltLang:
    def __init__(self):
        self._variables = {}

    def command(self, command: str):
        if command[:4] != 'func':
            commands = command.split(',')
        else:
            commands = [command]
        
        for command in commands:
            command = command.split()
            times = 1
            
            if command[0] == 'repeat' and command[1].isdigit() and command[2] == 'times':
                times = int(command[1])
                command = command[3:]

            for i in range(times):
                self._variables['i'] = i
            
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
                            assert len(var_info) == 2
                    
                            var_name = var_info[0].replace(' ', '')
                            var_value = var_info[1].strip()
                            self._variables[var_name] = var_value
    
                        except AssertionError:
                            raise SyntaxError
                    
                        except ValueError:
                            raise ValueError('Integer variable can contain only numbers')

                    case 'bool':
                        try:
                            var_info = ''.join(command[1:]).split('=')
                            var_name = var_info[0]
                            var_value = self.__create_bool_var(var_info[1])
                            self._variables[var_name] = var_value
                        except:
                            raise SyntaxError

                    case 'func':
                        try:
                            func_info = command[1:]
                            func_name = func_info[0]
                            func_code = ' '.join(func_info[1:])
                            self._variables[func_name] = lambda: self.command(func_code)
                        except:
                            raise SyntaxError

                    case 'call':
                        try:
                            func_name = command[1]
                            self._variables[func_name]()
                        except KeyError:
                            raise NameError
        
                    case _:
                        raise SyntaxError

    def __calculate(self, string: str) -> int:
        def compress_result():
            nonlocal result
            first_num, sign, second_num = result[:3]
            new_num = None
            
            match sign:
                case '-':
                    new_num = first_num - second_num
                case '+':
                    new_num = first_num + second_num
                case '*':
                    new_num = first_num * second_num
                case '/':
                    new_num = first_num / second_num
                case '^':
                    new_num = first_num ** second_num
                case _:
                    pass

            result = [new_num, result[-1]]
            

        string = string.replace(' ', '') + '\\\\'
        number = ''
        result = []
        while string != '':
            if number != '':
                for sign in ['+', '-', '*', '/', '^', '\\']:
                    if sign == number[-1]:
                        val = number[:-1]
                        
                        if val.isdigit():
                            val = int(val)
                        elif val in self._variables.keys():
                            val = self._variables[val]
                        else:
                            raise VariableError(f'Variable {val} is not exists')
                            
                        result.append(val)
                        result.append(number[-1])
                        number = ''

                        if len(result) == 4:
                            compress_result()
                        break
                    
            number += string[0]
            string = string[1:]
        return result[0]

    def __create_bool_var(self, string: str) -> bool:
        def compress_result():
            nonlocal result
            fir, sign, sec = result[:3]
            
            match sign:
                case '--':
                    new = fir == sec
                case '!-':
                    new = fir != sec
                case '<<':
                    new = fir < sec
                case '>>':
                    new = fir > sec
                case '<-':
                    new = fir <= sec
                case '>-':
                    new = fir >= sec
                case _:
                    raise SyntaxError

            result = [new, result[-1]]

        string = string.replace(' ', '') + '\\'
        result = []
        ex = ''

        while string != '':
            ex += string[0]
            string = string[1:]

            if ex[-1] in ['<', '>', '-', '!', '\\']:
                var = ex[:-1]
                
                if ex[-1] != '\\':
                    ex += string[0]
                    string = string[1:]

                if var.isdigit():
                    var = int(var)
                elif var == 'true':
                    var = True
                elif var == 'false':
                    var = False
                elif var in self._variables.keys():
                    var = self._variables[var]
                else:
                    raise SyntaxError
                
                result.append(var)
                result.append(ex[-2:])
                ex = ''

                if len(result) == 4:
                    compress_result()

        return result[0]

    def __calc_bool_exp(self, string: str) -> bool:
        def compress_result():
            nonlocal result
            fir, sign, sec = result[:3]

            match sign:
                case '&':
                    new = fir and sec
                case '|':
                    new = fir or sec
                case _:
                    raise SyntaxError(f'Sign "{sign}" is not exists')

            result = [new, result[-1]]
        
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
                    raise VariableError('Variable is not exists')
                
                if swap: var = not var
                
                result.append(var)
                result.append(exp[-1])
                exp = ''

                if len(result) == 4:
                    compress_result()

        return result[0]
                


cobalt = CobaltLang()
while command := input('>> '):
    cobalt.command(command)

