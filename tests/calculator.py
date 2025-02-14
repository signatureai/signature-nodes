class Calculator:
    @staticmethod
    def add(x: float, y: float) -> float:
        return x + y

    @staticmethod
    def subtract(x: float, y: float) -> float:
        return x - y

    @staticmethod
    def multiply(x: float, y: float) -> float:
        return x * y

    @staticmethod
    def divide(x: float, y: float) -> float:
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
