import argparse
import sys
import json
from FunctionStorage import storage, ParametricFunction


def create_function(args):
    """Создать новую функцию"""
    try:
        input_signature = None
        output_signature = None
        parameters = None
        
        if args.input_signature:
            input_signature = json.loads(args.input_signature)
        if args.output_signature:
            output_signature = json.loads(args.output_signature)
        if args.parameters:
            parameters = json.loads(args.parameters)
        
        func = ParametricFunction(
            name=args.name,
            code=args.code,
            description=args.description or "",
            input_signature=input_signature,
            output_signature=output_signature,
            parameters=parameters
        )
        
        storage.create(func)
        print(f"Function '{args.name}' created successfully")
        
        data = func.get_data()
        print(f"\nFunction data:")
        print(f"  Input signature: {data['input_signature']}")
        print(f"  Output signature: {data['output_signature']}")
        print(f"  Parameters: {json.dumps(data['parameters'], indent=2)}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_function(args):
    """Получить информацию о функции"""
    func = storage.get(args.name)
    if not func:
        print(f"Function '{args.name}' not found")
        sys.exit(1)
    
    if args.data:
        data = func.get_data()
        print(json.dumps(data, indent=2))
    else:
        print(f"Name: {func.name}")
        print(f"Description: {func.description}")
        print(f"Code:\n{func.code}")
        
        if not args.brief:
            data = func.get_data()
            print(f"\nInput signature: {data['input_signature']}")
            print(f"Output signature: {data['output_signature']}")
            print(f"Parameters: {json.dumps(data['parameters'], indent=2)}")


def update_function(args):
    """Обновить функцию"""
    input_signature = None
    output_signature = None
    parameters = None
    
    if args.input_signature:
        try:
            input_signature = json.loads(args.input_signature)
        except json.JSONDecodeError as e:
            print(f"Invalid input_signature JSON: {e}")
            sys.exit(1)
    
    if args.output_signature:
        try:
            output_signature = json.loads(args.output_signature)
        except json.JSONDecodeError as e:
            print(f"Invalid output_signature JSON: {e}")
            sys.exit(1)
    
    if args.parameters:
        try:
            parameters = json.loads(args.parameters)
        except json.JSONDecodeError as e:
            print(f"Invalid parameters JSON: {e}")
            sys.exit(1)
    
    updated = storage.update(
        name=args.name,
        code=args.code,
        description=args.description,
        input_signature=input_signature,
        output_signature=output_signature,
        parameters=parameters
    )
    
    if updated:
        print(f"Function '{args.name}' updated successfully")
    else:
        print(f"Function '{args.name}' not found")
        sys.exit(1)


def delete_function(args):
    """Удалить функцию"""
    if storage.delete(args.name):
        print(f"Function '{args.name}' deleted successfully")
    else:
        print(f"Function '{args.name}' not found")
        sys.exit(1)


def list_functions(args):
    """Показать список всех функций"""
    functions = storage.list()
    if not functions:
        print("No functions found")
        return
    
    print(f"Found {len(functions)} functions:")
    print("-" * 60)
    for func in functions:
        data = func.get_data()
        print(f"• {func.name}")
        print(f"  Description: {func.description}")
        print(f"  Input: {data['input_signature']}")
        print(f"  Output: {data['output_signature']}")
        print(f"  Parameters: {len(data['parameters'])}")
        print()


def compute_function(args):
    """Вычислить функцию"""
    try:
        if args.x:
            x_values = [float(val) for val in args.x.split(",")]
        else:
            x_values = [float(i) for i in range(10)]  # По умолчанию 0-9
        
        params = {}
        if args.params:
            for param in args.params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = float(value)
        
        results = storage.compute(args.name, x_values, params)
        
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


def main():
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
        "compute": compute_function
    }
    
    command_handlers[args.command](args)

if __name__ == "__main__":
    main()