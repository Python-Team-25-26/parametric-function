import argparse
import sys
import json
import aiohttp
import asyncio
from typing import Dict, Optional


async def http_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Отправка HTTP запроса к серверу"""
    default_url = "http://localhost:8000"
    url = f"{default_url}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.json()
                        raise ValueError(f"HTTP {response.status}: {error.get('detail', 'Unknown error')}")
            
            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error = await response.json()
                        raise ValueError(f"HTTP {response.status}: {error.get('detail', 'Unknown error')}")
            
            elif method.upper() == "PUT":
                async with session.put(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.json()
                        raise ValueError(f"HTTP {response.status}: {error.get('detail', 'Unknown error')}")
            
            elif method.upper() == "DELETE":
                async with session.delete(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.json()
                        raise ValueError(f"HTTP {response.status}: {error.get('detail', 'Unknown error')}")
        except Exception as e:
            raise ValueError(f"Request failed: {str(e)}")


async def create_function(args):
    """Создать новую функцию"""
    try:
        data = {
            "name": args.name,
            "code": args.code,
            "description": args.description or ""
        }
        
        if args.input_signature:
            data["input_signature"] = json.loads(args.input_signature)
        if args.output_signature:
            data["output_signature"] = json.loads(args.output_signature)
        if args.parameters:
            data["parameters"] = json.loads(args.parameters)
        
        result = await http_request("POST", "/functions", data)
        print(f"{result.get('message', 'Function created successfully')}")
        
        try:
            func_info = await http_request("GET", f"/functions/{args.name}")
            print(f"\nFunction data:")
            print(f"  Input signature: {func_info.get('input_signature', {})}")
            print(f"  Output signature: {func_info.get('output_signature', {})}")
            print(f"  Parameters: {json.dumps(func_info.get('parameters', []), indent=2)}")
        except:
            pass
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def get_function(args):
    """Получить информацию о функции"""
    try:
        func_info = await http_request("GET", f"/functions/{args.name}")
        
        if args.data:
            print(json.dumps(func_info, indent=2))
        else:
            print(f"Name: {func_info.get('name', 'N/A')}")
            print(f"Description: {func_info.get('description', 'N/A')}")
            print(f"Code:\n{func_info.get('code', 'N/A')}")
            
            if not args.brief:
                print(f"\nInput signature: {func_info.get('input_signature', {})}")
                print(f"Output signature: {func_info.get('output_signature', {})}")
                print(f"Parameters: {json.dumps(func_info.get('parameters', []), indent=2)}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def update_function(args):
    """Обновить функцию"""
    try:
        data = {}
        
        if args.code is not None:
            data["code"] = args.code
        if args.description is not None:
            data["description"] = args.description
        if args.input_signature:
            data["input_signature"] = json.loads(args.input_signature)
        if args.output_signature:
            data["output_signature"] = json.loads(args.output_signature)
        if args.parameters:
            data["parameters"] = json.loads(args.parameters)
        
        if not data:
            print("Nothing to update. Provide at least one field to update.")
            return
        
        result = await http_request("PUT", f"/functions/{args.name}", data)
        print(f"{result.get('message', 'Function updated successfully')}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def delete_function(args):
    """Удалить функцию"""
    try:
        result = await http_request("DELETE", f"/functions/{args.name}")
        print(f"{result.get('message', 'Function deleted successfully')}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def list_functions(args):
    """Показать список всех функций"""
    try:
        functions = await http_request("GET", "/functions")
        
        if not functions:
            print("No functions found")
            return
        
        print(f"Found {len(functions)} functions:")
        print("-" * 60)
        
        for func in functions:
            print(f"• {func.get('name', 'N/A')}")
            print(f"  Description: {func.get('description', 'N/A')}")
            
            try:
                func_detail = await http_request("GET", f"/functions/{func.get('name')}")
                print(f"  Input: {func_detail.get('input_signature', {})}")
                print(f"  Output: {func_detail.get('output_signature', {})}")
                params = func_detail.get('parameters', [])
                print(f"  Parameters: {len(params)}")
            except:
                print(f"  [Could not fetch details]")
            
            print()
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def compute_function(args):
    """Вычислить функцию"""
    try:
        if args.x:
            x_values = [float(val) for val in args.x.split(",")]
        else:
            x_values = [float(i) for i in range(10)]
        
        params = {}
        if args.params:
            for param in args.params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = float(value)
        
        data = {
            "x": x_values,
            "params": params
        }
        
        results = await http_request("POST", f"/functions/{args.name}/compute", data)
        
        print(f"Results for function '{args.name}':")
        for x_val, y_val in zip(x_values, results):
            print(f"  f({x_val}) = {y_val}")
        
        if args.output and len(results) == 1:
            print(f"\nOutput: {results[0]}")
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Computation error: {e}")
        sys.exit(1)


async def get_data(args):
    """Получить данные функции"""
    try:
        data = await http_request("GET", f"/functions/{args.name}/data")
        print(json.dumps(data, indent=2))
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="CLI for Parametric Function Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Создать функцию с автоматическим извлечением данных
  python CLI.py create --name "linear" --code "def f(x, a=1, b=0): return a*x + b"
  
  # Создать функцию с явным указанием данных
  python CLI.py create --name "linear" --code "def f(x, a=1, b=0): return a*x + b" 
    --input-signature '{"x": "float", "a": "float", "b": "float"}'
    --output-signature '{"return": "float"}' 
    --parameters '[{"name": "a", "type": "float", "default": 1.0}, {"name": "b", "type": "float", "default": 0.0}]'
  
  # Вычислить функцию
  python CLI.py compute --name "linear" --x "1,2,3,4,5" --params "a=2" "b=1"
  
  # Получить информацию о функции
  python CLI.py get --name "linear" --data
  
  # Получить данные функции
  python CLI.py data --name "linear"
  
  # Список всех функций
  python CLI.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    create_parser = subparsers.add_parser("create", help="Create a new function")
    create_parser.add_argument("--name", required=True, help="Function name")
    create_parser.add_argument("--code", required=True, help="Function code")
    create_parser.add_argument("--description", help="Function description")
    create_parser.add_argument("--input-signature", help="Input signature as JSON")
    create_parser.add_argument("--output-signature", help="Output signature as JSON")
    create_parser.add_argument("--parameters", help="Parameters list as JSON")
    
    get_parser = subparsers.add_parser("get", help="Get function details")
    get_parser.add_argument("--name", required=True, help="Function name")
    get_parser.add_argument("--data", action="store_true", help="Show data only")
    get_parser.add_argument("--brief", action="store_true", help="Brief output")
    
    update_parser = subparsers.add_parser("update", help="Update a function")
    update_parser.add_argument("--name", required=True, help="Function name")
    update_parser.add_argument("--code", help="New function code")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--input-signature", help="New input signature as JSON")
    update_parser.add_argument("--output-signature", help="New output signature as JSON")
    update_parser.add_argument("--parameters", help="New parameters list as JSON")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a function")
    delete_parser.add_argument("--name", required=True, help="Function name")
    
    list_parser = subparsers.add_parser("list", help="List all functions")
    
    compute_parser = subparsers.add_parser("compute", help="Compute a function")
    compute_parser.add_argument("--name", required=True, help="Function name")
    compute_parser.add_argument("--x", help="Comma-separated x values (e.g., '1,2,3,4,5')")
    compute_parser.add_argument("--params", nargs="*", help="Parameters as key=value pairs")
    compute_parser.add_argument("--output", action="store_true", help="Output single result only")
    
    data_parser = subparsers.add_parser("data", help="Get function data")
    data_parser.add_argument("--name", required=True, help="Function name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    command_handlers = {
        "create": create_function,
        "get": get_function,
        "update": update_function,
        "delete": delete_function,
        "list": list_functions,
        "compute": compute_function,
        "data": get_data
    }
    
    await command_handlers[args.command](args)


if __name__ == "__main__":
    asyncio.run(main())