def add(a, b):
    """두 숫자의 합을 반환합니다."""
    return a + b

def subtract(a, b):
    """두 숫자의 차이를 반환합니다."""
    return a - b

def multiply(a, b):
    """두 숫자의 곱을 반환합니다."""
    return a * b

def divide(a, b):
    """두 숫자를 나눈 결과를 반환합니다. 0으로 나눌 경우 오류를 반환합니다."""
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다.")
    return a / b