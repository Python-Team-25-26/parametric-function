import json
from typing import Dict, List, Any, Callable


class ParametricFunction:
    
    def __init__(self, 
                 name: str, 
                 code: str, 
                 description: str = ""):
        """
        Docstring for __init__
        
        :param name: Уникальное название функции
        :type name: str
        :param code: Код функции для выполнения
        :type code: str
        :param description: Опциональное описание функции
        :type description: str
        """
        self.name = name
        self.code = code
        self.description = description
        self._compiled_code = compile(code, f'<function {name}>', 'exec')
    
    def compute(self, 
                x: List[float], 
                params: Dict[str, float] = None) -> List[float]:
        """
        Вычисляет функцию для списка значений x
        
        :param x: Список передаваемых значений
        :type x: List[float]
        :param params: Параметры для передачи в функци.
        :type params: Dict[str, float]
        :return: Вычисленные значения для списка входных значений
        :rtype: List[float]
        
        """
        if params is None:
            params = {}
        
        results = []
        
        global_env = {
            'math': __import__('math'),
            'x': 0.0,  # Будет переопределяться для каждого значения
            **params
        }
        
        # Выполняем код функции
        exec(self._compiled_code, global_env)
        
        # В global_env должна быть функция f
        if 'f' not in global_env:
            raise ValueError("Function code must define a function named 'f'")
        
        f = global_env['f']
        
        for xi in x:
            try:
                global_env['x'] = xi
                result = f(xi, **params)
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
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParametricFunction':
        """Десериализация функции из словаря"""
        return cls(
            name=data["name"],
            code=data["code"],
            description=data.get("description", "")
        )