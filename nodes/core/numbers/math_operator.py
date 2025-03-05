import ast
import math
import operator as op
import string

from .... import MAX_FLOAT
from ...categories import NUMBERS_CAT
from .shared import OP_FUNCTIONS


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
        - Supports exponential and logarithmic functions: base**exponent, log(base, value)
        - Includes functions: min(), max(), round(), sum(), len(), clamp(value, min, max)
        - Variables are limited by MAX_FLOAT constant
        - NaN results are converted to 0.0
    """

    @classmethod
    def INPUT_TYPES(cls):
        input_letters = string.ascii_lowercase[:10]  # Get an array of all letters from a to j
        inputs = {
            "required": {
                "num_slots": ([str(i) for i in range(1, 11)], {"default": "1"}),
                "value": ("STRING", {"default": ""}),
            },
            "optional": {},
        }

        for letter in input_letters:
            inputs["optional"].update(
                {
                    letter: (
                        "INT,FLOAT",
                        {
                            "default": 0,
                            "min": -MAX_FLOAT,
                            "max": MAX_FLOAT,
                            "step": 0.01,
                            "forceInput": True,
                        },
                    )
                }
            )

        return inputs

    RETURN_TYPES = (
        "INT",
        "FLOAT",
    )
    FUNCTION = "execute"
    CATEGORY = NUMBERS_CAT
    DESCRIPTION = """Evaluates mathematical expressions with support for variables and multiple operators.

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
        - Supports exponential and logarithmic functions: base**exponent, log(base, value)
        - Includes functions: min(), max(), round(), sum(), len(), clamp(value, min, max)
        - Variables are limited by MAX_FLOAT constant
        - NaN results are converted to 0.0
    """

    def execute(self, num_slots: str = "1", value: str = "", **kwargs) -> tuple[int, float]:
        if int(num_slots) != len(kwargs.keys()):
            raise ValueError("Number of inputs is not equal to number of slots")

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

        def eval_(node):
            if isinstance(node, ast.Constant):  # number
                return node.n
            if isinstance(node, ast.Name):  # variable
                return kwargs.get(node.id)
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
                if node.func.id in OP_FUNCTIONS:  # type: ignore
                    args = [eval_(arg) for arg in node.args]
                    return OP_FUNCTIONS[node.func.id](*args)  # type: ignore
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
            result,  # type: ignore
        )
