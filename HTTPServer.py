from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional, Any
import uvicorn
from FunctionStorage import storage, ParametricFunction
from dataclasses import dataclass

app = FastAPI(title="Parametric Function Server")

@dataclass
class FunctionCreateRequest:
    name: str
    code: str
    description: str = ""
    input_signature: Optional[Dict[str, str]] = None
    output_signature: Optional[Dict[str, str]] = None
    parameters: Optional[List[Dict[str, Any]]] = None

@dataclass
class FunctionUpdateRequest:
    code: Optional[str] = None
    description: Optional[str] = None
    input_signature: Optional[Dict[str, str]] = None
    output_signature: Optional[Dict[str, str]] = None
    parameters: Optional[List[Dict[str, Any]]] = None

@dataclass
class ComputeRequest:
    x: List[float]
    params: Dict[str, float] = None


@dataclass
class FunctionInfoResponse:
    name: str
    code: str
    description: str
    input_signature: Dict[str, str]
    output_signature: Dict[str, str]
    parameters: List[Dict[str, Any]]


def validate_function_data(data: Dict) -> Dict:
    """Валидация данных функции"""
    if 'name' not in data:
        raise HTTPException(status_code=400, detail="Field 'name' is required")
    if 'code' not in data:
        raise HTTPException(status_code=400, detail="Field 'code' is required")
    return data


@app.get("/")
async def root():
    return {"message": "Parametric Function Server"}

@app.get("/functions")
async def list_functions():
    """Получить список всех функций"""
    functions = storage.list()
    return [{"name": f.name, "description": f.description} for f in functions]

@app.get("/functions/{name}")
async def get_function(name: str):
    """Получить информацию о функции"""
    func = storage.get(name)
    if not func:
        raise HTTPException(status_code=404, detail=f"Function '{name}' not found")
    
    data = func.get_data()
    
    return FunctionInfoResponse(
        name=func.name,
        code=func.code,
        description=func.description,
        input_signature=data["input_signature"],
        output_signature=data["output_signature"],
        parameters=data["parameters"]
    )

@app.post("/functions")
async def create_function(request_data: Dict[str, Any]):
    """Создать новую функцию"""
    try:
        data = validate_function_data(request_data)
        
        func = ParametricFunction(
            name=data["name"],
            code=data["code"],
            description=data.get("description", ""),
            input_signature=data.get("input_signature"),
            output_signature=data.get("output_signature"),
            parameters=data.get("parameters")
        )
        
        storage.create(func)
        return {"message": f"Function '{data['name']}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/functions/{name}")
async def update_function(name: str, request_data: Dict[str, Any]):
    """Обновить существующую функцию"""
    try:
        updated = storage.update(
            name=name,
            code=request_data.get("code"),
            description=request_data.get("description"),
            input_signature=request_data.get("input_signature"),
            output_signature=request_data.get("output_signature"),
            parameters=request_data.get("parameters")
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"Function '{name}' not found")
        
        return {"message": f"Function '{name}' updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/functions/{name}")
async def delete_function(name: str):
    """Удалить функцию"""
    deleted = storage.delete(name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Function '{name}' not found")

    return {"message": f"Function '{name}' deleted successfully"}

@app.post("/functions/{name}/compute")
async def compute_function(name: str, request_data: Dict[str, Any]):
    """Вычислить функцию для заданных значений"""
    try:
        if 'x' not in request_data:
            raise HTTPException(status_code=400, detail="Field 'x' is required")
        
        x = request_data['x']
        params = request_data.get('params', {})
        
        if not isinstance(x, list):
            raise HTTPException(status_code=400, detail="Field 'x' must be a list")
        
        results = storage.compute(name, x, params)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing function: {str(e)}")


@app.get("/functions/{name}/data")
async def get_function_metadata(name: str):
    """Получить данные функции (сигнатуры, параметры)"""
    func = storage.get(name)
    if not func:
        raise HTTPException(status_code=404, detail=f"Function '{name}' not found")
    
    return func.get_data()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)