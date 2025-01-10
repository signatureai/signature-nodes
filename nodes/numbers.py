import ast
import math
import operator as op
import random

from .. import MAX_FLOAT, MAX_INT
from .categories import NUMBERS_CAT


class IntClamp:
    """Clamps an integer value between specified minimum and maximum bounds.

    This class provides functionality to constrain an integer input within a defined range. If the input
    number is less than the minimum value, it returns the minimum value. If it's greater than the
    maximum value, it returns the maximum value.

    Args:
        number (int): The input integer to be clamped.
        min_value (int): The minimum allowed value.
        max_value (int): The maximum allowed value.

    Returns:
        tuple[int]: A single-element tuple containing the clamped integer value.

    Raises:
        ValueError: If any of the inputs (number, min_value, max_value) are not integers.

    Notes:
        - The input range is limited by MAX_INT constant
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": (
                    "INT",
                    {
                        "default": 0,
                        "forceInput": True,
                        "min": -MAX_INT,
                        "max": MAX_INT,
                    },
                ),
                "min_value": (
                    "INT",
                    {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                ),
                "max_value": (
                    "INT",
                    {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, **kwargs):
        number = kwargs.get("number")
        if not isinstance(number, int):
            raise ValueError("Number must be an integer")
        min_value = kwargs.get("min_value")
        if not isinstance(min_value, int):
            raise ValueError("Min value must be an integer")
        max_value = kwargs.get("max_value")
        if not isinstance(max_value, int):
            raise ValueError("Max value must be an integer")
        if number < min_value:
            return (min_value,)
        if number > max_value:
            return (max_value,)
        return (number,)


class FloatClamp:
    """Clamps a floating-point value between specified minimum and maximum bounds.

    This class provides functionality to constrain a float input within a defined range. If the input
    number is less than the minimum value, it returns the minimum value. If it's greater than the
    maximum value, it returns the maximum value.

    Args:
        number (float): The input float to be clamped.
        min_value (float): The minimum allowed value.
        max_value (float): The maximum allowed value.

    Returns:
        tuple[float]: A single-element tuple containing the clamped float value.

    Raises:
        ValueError: If any of the inputs (number, min_value, max_value) are not floats.

    Notes:
        - The input range is limited by MAX_FLOAT constant
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": (
                    "FLOAT",
                    {
                        "default": 0,
                        "forceInput": True,
                        "min": -MAX_FLOAT,
                        "max": MAX_FLOAT,
                    },
                ),
                "min_value": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "max_value": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, **kwargs):
        number = kwargs.get("number")
        if not isinstance(number, float) and not isinstance(number, int):
            raise ValueError("Number must be a float")
        min_value = kwargs.get("min_value")
        if not isinstance(min_value, float) and not isinstance(min_value, int):
            raise ValueError("Min value must be a float")
        max_value = float(kwargs.get("max_value") or 0.0)
        if not isinstance(max_value, float) and not isinstance(max_value, int):
            raise ValueError("Max value must be a float")

        if number < min_value:
            return (min_value,)
        if number > max_value:
            return (max_value,)
        return (number,)


class Float2Int:
    """Converts a floating-point number to an integer through truncation.

    This class handles the conversion of float values to integers by removing the decimal portion.
    The conversion is performed using Python's built-in int() function, which truncates towards zero.

    Args:
        number (float): The floating-point number to convert to an integer.

    Returns:
        tuple[int]: A single-element tuple containing the converted integer value.

    Raises:
        ValueError: If the input value is not a float.

    Notes:
        - Decimal portions are truncated, not rounded
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": ("FLOAT", {"default": 0, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "float2int"

    def execute(self, **kwargs):
        try:
            number = float(kwargs.get("number", 0.0))
            return (int(number),)
        except (TypeError, ValueError):
            raise ValueError("Number must be convertible to float")


class Int2Float:
    """Converts an integer to a floating-point number.

    This class handles the conversion of integer values to floating-point numbers using Python's
    built-in float() function.

    Args:
        number (int): The integer to convert to a float.

    Returns:
        tuple[float]: A single-element tuple containing the converted float value.

    Raises:
        ValueError: If the input value is not an integer.

    Notes:
        - The conversion is exact as all integers can be represented precisely as floats
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "number": ("INT", {"default": 0, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "int2float"

    def execute(self, **kwargs):
        try:
            number = int(kwargs.get("number", 0))
            return (float(number),)
        except (TypeError, ValueError):
            raise ValueError("Number must be convertible to integer")


class IntOperator:
    """Performs arithmetic operations on two floats and returns an integer result.

    This class supports basic arithmetic operations between two floating-point numbers and returns
    the result as an integer. The supported operations are addition, subtraction, multiplication,
    and division.

    Args:
        left (float): The left operand for the arithmetic operation.
        right (float): The right operand for the arithmetic operation.
        operator (str): The arithmetic operator to use ('+', '-', '*', or '/').

    Returns:
        tuple[int]: A single-element tuple containing the result of the operation as an integer.

    Raises:
        ValueError: If either operand is not a float or if the operator is not supported.

    Notes:
        - Division results are converted to integers
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
        - Input values are limited by MAX_FLOAT constant
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "left": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "right": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "operator": (["+", "-", "*", "/"],),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, **kwargs):
        try:
            left = float(kwargs.get("left", 0.0))
            right = float(kwargs.get("right", 0.0))
            operator = str(kwargs.get("operator", "+"))
        except (TypeError, ValueError):
            raise ValueError("Values must be convertible to floats")

        if operator == "+":
            return (int(left + right),)
        if operator == "-":
            return (int(left - right),)
        if operator == "*":
            return (int(left * right),)
        if operator == "/":
            return (int(left / right),)

        raise ValueError(f"Unsupported operator: {operator}")


class FloatOperator:
    """Performs arithmetic operations on two floating-point numbers.

    This class supports basic arithmetic operations between two floating-point numbers. The supported
    operations are addition, subtraction, multiplication, and division.

    Args:
        left (float): The left operand for the arithmetic operation.
        right (float): The right operand for the arithmetic operation.
        operator (str): The arithmetic operator to use ('+', '-', '*', or '/').

    Returns:
        tuple[float]: A single-element tuple containing the result of the operation.

    Raises:
        ValueError: If either operand is not a float or if the operator is not supported.

    Notes:
        - Division by zero will raise a Python exception
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
        - Input values are limited by MAX_FLOAT constant
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "left": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "right": (
                    "FLOAT",
                    {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                ),
                "operator": (["+", "-", "*", "/", "%"],),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, **kwargs):
        left = kwargs.get("left")
        if not isinstance(left, float):
            raise ValueError("Left must be a float")
        right = kwargs.get("right")
        if not isinstance(right, float):
            raise ValueError("Right must be a float")
        operator = kwargs.get("operator")
        if not isinstance(operator, str):
            raise ValueError("Operator must be a string")
        if operator == "+":
            return (left + right,)
        if operator == "-":
            return (left - right,)
        if operator == "*":
            return (left * right,)
        if operator == "/":
            return (left / right,)

        raise ValueError(f"Unsupported operator: {operator}")


class IntMinMax:
    """Determines the minimum or maximum value between two integers.

    This class compares two integer inputs and returns either the smaller or larger value based on
    the specified mode of operation.

    Args:
        a (int): The first integer to compare.
        b (int): The second integer to compare.
        mode (str): The comparison mode ('min' or 'max').

    Returns:
        tuple[int]: A single-element tuple containing either the minimum or maximum value.

    Raises:
        ValueError: If either input is not an integer or if the mode is not supported.

    Notes:
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "a": ("INT", {"default": 0, "forceInput": True}),
                "b": ("INT", {"default": 0, "forceInput": True}),
                "mode": (["min", "max"],),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "int_minmax"

    def execute(self, **kwargs):
        try:
            a = int(kwargs.get("a", 0))
            b = int(kwargs.get("b", 0))
            mode = str(kwargs.get("mode", "min"))
        except (TypeError, ValueError):
            raise ValueError("Values must be convertible to integers")

        if mode == "min":
            return (min(a, b),)
        if mode == "max":
            return (max(a, b),)
        raise ValueError(f"Unsupported mode: {mode}")


class FloatMinMax:
    """Determines the minimum or maximum value between two floating-point numbers.

    This class compares two float inputs and returns either the smaller or larger value based on
    the specified mode of operation.

    Args:
        a (float): The first float to compare.
        b (float): The second float to compare.
        mode (str): The comparison mode ('min' or 'max').

    Returns:
        tuple[float]: A single-element tuple containing either the minimum or maximum value.

    Raises:
        ValueError: If either input is not a float or if the mode is not supported.

    Notes:
        - The returned value is always wrapped in a tuple to maintain consistency with the node system
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "forceInput": True}),
                "b": ("FLOAT", {"default": 0.0, "forceInput": True}),
                "mode": (["min", "max"],),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    CLASS_ID = "float_minmax"

    def execute(self, **kwargs):
        try:
            a = float(kwargs.get("a", 0.0))
            b = float(kwargs.get("b", 0.0))
            mode = str(kwargs.get("mode", "min"))
        except (TypeError, ValueError):
            raise ValueError("Values must be convertible to floats")

        if mode == "min":
            return (min(a, b),)
        if mode == "max":
            return (max(a, b),)
        raise ValueError(f"Unsupported mode: {mode}")


class RandomNumber:
    """Generates a random integer and its floating-point representation.

    This class produces a random integer between 0 and MAX_INT and provides both the integer value
    and its floating-point equivalent.

    Returns:
        tuple[int, float]: A tuple containing the random integer and its float representation.

    Notes:
        - The random value is regenerated each time IS_CHANGED is called
        - The maximum value is limited by MAX_INT constant
        - No parameters are required for this operation
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {"required": {}}

    RETURN_TYPES = (
        "INT",
        "FLOAT",
    )
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    @staticmethod
    def get_random():
        result = random.randint(0, MAX_INT)
        return (
            result,
            float(result),
        )

    def execute(self):
        return RandomNumber.get_random()

    @classmethod
    def IS_CHANGED(cls):  # type: ignore
        return RandomNumber.get_random()


class MathOperator:
    """Evaluates mathematical expressions with support for variables and multiple operators.

    This class provides a powerful expression evaluator that supports variables (a, b, c, d) and
    various mathematical operations. It can handle arithmetic, comparison, and logical operations.

    Args:
        a (float, optional): Value for variable 'a'. Defaults to 0.0.
        b (float, optional): Value for variable 'b'. Defaults to 0.0.
        c (float, optional): Value for variable 'c'. Defaults to 0.0.
        d (float, optional): Value for variable 'd'. Defaults to 0.0.
        value (str): The mathematical expression to evaluate.

    Returns:
        tuple[int, float]: A tuple containing both integer and float representations of the result.

    Raises:
        ValueError: If the expression contains unsupported operations or invalid syntax.

    Notes:
        - Supports standard arithmetic operators: +, -, *, /, //, %, **
        - Supports comparison operators: ==, !=, <, <=, >, >=
        - Supports logical operators: and, or, not
        - Supports bitwise XOR operator: ^
        - Includes functions: min(), max(), round(), sum(), len()
        - Variables are limited by MAX_FLOAT constant
        - NaN results are converted to 0.0
    """

    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "optional": {
                "a": ("FLOAT", {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01}),
                "b": ("FLOAT", {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01}),
                "c": ("FLOAT", {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01}),
                "d": ("FLOAT", {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01}),
            },
            "required": {
                "value": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = (
        "INT",
        "FLOAT",
    )
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT

    def execute(self, **kwargs):
        try:
            a = float(kwargs.get("a", 0.0))
            b = float(kwargs.get("b", 0.0))
            c = float(kwargs.get("c", 0.0))
            d = float(kwargs.get("d", 0.0))
            value = str(kwargs.get("value", "")).strip()
        except (TypeError, ValueError):
            raise ValueError("Values must be convertible to floats")

        def safe_xor(x, y):
            if isinstance(x, float) or isinstance(y, float):
                # Convert to integers if either operand is a float
                return float(int(x) ^ int(y))
            return op.xor(x, y)

        operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.FloorDiv: op.floordiv,
            ast.Pow: op.pow,
            ast.USub: op.neg,
            ast.Mod: op.mod,
            ast.Eq: op.eq,
            ast.NotEq: op.ne,
            ast.Lt: op.lt,
            ast.LtE: op.le,
            ast.Gt: op.gt,
            ast.GtE: op.ge,
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
            ast.Not: op.not_,
            ast.BitXor: safe_xor,  # Use the safe_xor function
        }

        op_functions = {
            "min": min,
            "max": max,
            "round": round,
            "sum": sum,
            "len": len,
        }

        def eval_(node):
            if isinstance(node, ast.Num):  # number
                return node.n
            if isinstance(node, ast.Name):  # variable
                if node.id == "a":
                    return a
                if node.id == "b":
                    return b
                if node.id == "c":
                    return c
                if node.id == "d":
                    return d
            if isinstance(node, ast.BinOp):  # <left> <operator> <right>
                return operators[type(node.op)](eval_(node.left), eval_(node.right))  # type: ignore
            if isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
                return operators[type(node.op)](eval_(node.operand))  # type: ignore
            if isinstance(node, ast.Compare):  # comparison operators
                left = eval_(node.left)
                for operator, comparator in zip(node.ops, node.comparators):
                    if not operators[type(operator)](left, eval_(comparator)):  # type: ignore
                        return 0
                return 1
            if isinstance(node, ast.BoolOp):  # boolean operators (And, Or)
                values = [eval_(value) for value in node.values]
                return operators[type(node.op)](*values)  # type: ignore
            if isinstance(node, ast.Call):  # custom function
                if node.func.id in op_functions:  # type: ignore
                    args = [eval_(arg) for arg in node.args]
                    return op_functions[node.func.id](*args)  # type: ignore
            if isinstance(node, ast.Subscript):  # indexing or slicing
                value = eval_(node.value)
                if isinstance(node.slice, ast.Constant):
                    return value[node.slice.value]
                return 0
            return 0

        result = eval_(ast.parse(value, mode="eval").body)

        if math.isnan(result):  # type: ignore
            result = 0.0

        return (
            round(result),  # type: ignore
            result,
        )  # type: ignore
