import json
import os
from typing import Dict, List, Optional, Any
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
                with open(self._storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                loaded_count = 0
                for func_data in data.get("functions", []):
                    try:
                        func = ParametricFunction.from_dict(func_data)
                        self._functions[func.name] = func
                        loaded_count += 1
                    except Exception as e:
                        print(f"Could not load function {func_data.get('name', 'unknown')}: {e}")
                
                print(f"Loaded {loaded_count} functions from {self._storage_file}")
            except Exception as e:
                print(f"Error loading functions: {e}")
    
    def _save(self):
        """Сохранение функций в файл"""
        try:
            data = {
                "functions": [func.to_dict() for func in self._functions.values()]
            }
            
            with open(self._storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
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
    
    def update(self, 
               name: str, 
               code: str = None, 
               description: str = None,
               input_signature: Optional[Dict[str, str]] = None,
               output_signature: Optional[Dict[str, str]] = None,
               parameters: Optional[List[Dict[str, Any]]] = None) -> Optional[ParametricFunction]:
        """Обновление функции"""
        func = self._functions.get(name)
        if not func:
            return None
        
        updated = False
        
        if code is not None:
            try:
                new_func = ParametricFunction(
                    name=name, 
                    code=code,
                    description=description or func.description,
                    input_signature=input_signature or func.input_signature,
                    output_signature=output_signature or func.output_signature,
                    parameters=parameters or func.parameters
                )
                self._functions[name] = new_func
                updated = True
            except Exception as e:
                raise ValueError(f"Invalid function code: {e}")
        else:
            if description is not None:
                func.description = description
                updated = True
            
            if input_signature is not None:
                func.input_signature = input_signature
                updated = True
            
            if output_signature is not None:
                func.output_signature = output_signature
                updated = True
            
            if parameters is not None:
                func.parameters = parameters
                updated = True
        
        if updated:
            self._save()
        
        return self._functions.get(name)
    
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