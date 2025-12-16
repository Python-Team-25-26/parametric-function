import requests

BASE_URL = "http://127.0.0.1:8000"

# Общие параметры для всех запросов
REQUEST_KWARGS = {
    "proxies": {
        "http": "",
        "https": ""
    },
    "timeout": 5
}


def create_function():
    payload = {
        "name": "quadratic",
        "code": "def f(x, a=1, b=0, c=0): return a*x*x + b*x + c",
        "description": "Quadratic function"
    }

    r = requests.post(
        f"{BASE_URL}/functions",
        json=payload,
        **REQUEST_KWARGS
    )

    print("CREATE status:", r.status_code)
    print("CREATE response:", r.text)


def compute_function():
    payload = {
        "x": [0, 1, 2, 3],
        "params": {"a": 2, "b": 3, "c": 1}
    }

    r = requests.post(
        f"{BASE_URL}/functions/quadratic/compute",
        json=payload,
        **REQUEST_KWARGS
    )

    print("COMPUTE status:", r.status_code)
    print("COMPUTE response:", r.text)


if __name__ == "__main__":
    create_function()
    compute_function()
