import json
import os
from typing import Dict, List, Optional
from ParametricFunction import ParametricFunction


class FunctionStorage:
    """Хранилище функций в памяти с сохранением в JSON"""
    
    def __init__(self, storage_file: str = "functions.json"):
        """
        :param storage_file: Путь к файлу для сохранения и загрузки функций
        :type storage_file: str
        """
        self._functions: Dict[str, ParametricFunction] = {}
        self._storage_file = storage_file
        self._load()
    
    def _load(self):
        """Загрузка функций из файла"""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, 'r') as f:
                    data = json.load(f)
                
                for func_data in data.get("functions", []):
                    func = ParametricFunction.from_dict(func_data)
                    self._functions[func.name] = func
                
                print(f"Loaded {len(self._functions)} functions from {self._storage_file}")
            except Exception as e:
                print(f"Error loading functions: {e}")
    
    def _save(self):
        """Сохранение функций в файл"""
        try:
            data = {
                "functions": [func.to_dict() for func in self._functions.values()]
            }
            
            with open(self._storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving functions: {e}")
    
    def create(self, func: ParametricFunction) -> ParametricFunction:
        """Создание новой функции"""
        if func.name in self._functions:
            raise ValueError(f"Function '{func.name}' already exists")
        
        self._functions[func.name] = func
        self._save()
        return func
    
    def get(self, name: str) -> Optional[ParametricFunction]:
        """Получение функции по имени"""
        return self._functions.get(name)
    
    def update(self, name: str, code: str = None, description: str = None) -> Optional[ParametricFunction]:
        """Обновление функции"""
        func = self._functions.get(name)
        if not func:
            return None
        
        if code is not None:
            func.code = code
            func._compiled_code = compile(code, f'<function {name}>', 'exec')
        
        if description is not None:
            func.description = description
        
        self._save()
        return func
    
    def delete(self, name: str) -> bool:
        """Удаление функции"""
        if name in self._functions:
            del self._functions[name]
            self._save()
            return True
        return False
    
    def list(self) -> List[ParametricFunction]:
        """Список всех функций"""
        return list(self._functions.values())
    
    def compute(self, name: str, x: List[float], params: Dict[str, float] = None) -> List[float]:
        """Вычисление функции"""
        func = self.get(name)
        if not func:
            raise ValueError(f"Function '{name}' not found")
        
        return func.compute(x, params)


# Глобальное хранилище
storage = FunctionStorage()