from typing import Dict, List, Any, Callable, Optional
import math
import re


class ParametricFunction:
    
    def __init__(self, 
                 name: str, 
                 code: str, 
                 description: str = "",
                 input_signature: Optional[Dict[str, str]] = None,
                 output_signature: Optional[Dict[str, str]] = None,
                 parameters: Optional[List[Dict[str, Any]]] = None):
        """
        :param name: Уникальное название функции
        :param code: Код функции для выполнения
        :param description: Опциональное описание функции
        :param input_signature: Сигнатура входа (например, {"x": "float", "a": "float", "b": "float"})
        :param output_signature: Сигнатура выхода (например, {"return": "float"})
        :param parameters: Список параметров (например, [{"name": "a", "type": "float", "default": 1.0}])
        """
        self.name = name
        self.code = code
        self.description = description
        self.input_signature = input_signature or {}
        self.output_signature = output_signature or {}
        self.parameters = parameters or []
        
        if not (self.input_signature and self.output_signature and self.parameters):
            self._extract_data()
        
        self._compiled_code = compile(code, f'<function {name}>', 'exec')
        self._function_obj: Optional[Callable] = None
        self._extract_function()
    
    def _extract_data(self):
        """Автоматическое извлечение данных из кода функции"""
        try:
            func_match = re.search(r'def\s+f\s*\((.*?)\)\s*:', self.code)
            if not func_match:
                return
            
            args_str = func_match.group(1)
            
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            
            if not args:
                return
            
            # Первый аргумент - x
            x_arg = args[0]
            self.input_signature = {x_arg: "float"}
            
            # Остальные аргументы - параметры
            self.parameters = []
            for arg in args[1:]:
                if '=' in arg:
                    name, default_part = arg.split('=', 1)
                    name = name.strip()
                    default_part = default_part.strip()
                    
                    param_type = "float"
                    try:
                        default_val = float(default_part)
                    except:
                        default_val = 0.0
                        param_type = "any"
                else:
                    name = arg.strip()
                    default_val = None
                    param_type = "float"
                
                self.parameters.append({
                    "name": name,
                    "type": param_type,
                    "default": default_val
                })
                
                self.input_signature[name] = param_type
            
            self.output_signature = {"return": "float"}
            
        except Exception as e:
            print(f"Could not auto-extract data: {e}")
    
    def _extract_function(self):
        """Извлечь объект функции из скомпилированного кода"""
        global_env = {
            'math': math,
            '__builtins__': __builtins__
        }
        
        # Выполняем код функции
        exec(self._compiled_code, global_env)
        
        # В global_env должна быть функция f
        if 'f' not in global_env:
            raise ValueError("Function code must define a function named 'f'")
        
        self._function_obj = global_env['f']
    
    def get_data(self) -> Dict[str, Any]:
        """Получить данные функции (сигнатуры, параметры)"""
        return {
            "name": self.name,
            "description": self.description,
            "input_signature": self.input_signature,
            "output_signature": self.output_signature,
            "parameters": self.parameters
        }
    
    def compute(self, 
                x: List[float], 
                params: Dict[str, float] = None) -> List[float]:
        """
        Вычисляет функцию для списка значений x
        
        :param x: Список передаваемых значений
        :type x: List[float]
        :param params: Параметры для передачи в функцию
        :type params: Dict[str, float]
        :return: Вычисленные значения для списка входных значений
        :rtype: List[float]
        """
        if params is None:
            params = {}
        
        if not self._function_obj:
            raise ValueError("Function not properly initialized")
        
        results = []
        
        for xi in x:
            try:
                call_args = {'x': xi}
                call_args.update(params)
                
                result = self._function_obj(**call_args)
                
                if isinstance(result, (int, float)):
                    results.append(float(result))
                else:
                    raise ValueError(f"Function must return a number, got {type(result)}")
                    
            except Exception as e:
                raise ValueError(f"Error computing function for x={xi}: {e}")
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация функции в словарь"""
        return {
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "input_signature": self.input_signature,
            "output_signature": self.output_signature,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParametricFunction':
        """Десериализация функции из словаря"""
        return cls(
            name=data["name"],
            code=data["code"],
            description=data.get("description", ""),
            input_signature=data.get("input_signature", {}),
            output_signature=data.get("output_signature", {}),
            parameters=data.get("parameters", [])
        )