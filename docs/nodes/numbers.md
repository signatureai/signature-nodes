# Numbers Nodes

## FloatClamp

Clamps a floating-point value between specified minimum and maximum bounds.

This class provides functionality to constrain a float input within a defined range. If the input
number is less than the minimum value, it returns the minimum value. If it's greater than the
maximum value, it returns the maximum value.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | number | `FLOAT` | 0 | forceInput=True |
| required | max_value | `FLOAT` | 0 | step=0.01 |
| required | min_value | `FLOAT` | 0 | step=0.01 |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |


??? note "Source code"

    ```python
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
                    "max_value": (
                        "FLOAT",
                        {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                    ),
                    "min_value": (
                        "FLOAT",
                        {"default": 0, "min": -MAX_FLOAT, "max": MAX_FLOAT, "step": 0.01},
                    ),
                }
            }

        RETURN_TYPES = ("FLOAT",)
        FUNCTION = "execute"
        CATEGORY = NUMBERS_CAT
        DESCRIPTION = """
        Clamps a floating-point value between specified minimum and maximum bounds.
        Constrains a float input within a defined range,
        returning the min value if input is too low or max value if input is too high.
        """

        def execute(self, number: float = 0.0, max_value: float = 0.0, min_value: float = 0.0) -> tuple[float]:
            if max_value < min_value:
                raise ValueError("Max value must be greater than or equal to min value")
            if number < min_value:
                return (min_value,)
            if number > max_value:
                return (max_value,)
            return (number,)
    ```

## Int2Float

Converts an integer to a floating-point number.

This class handles the conversion of integer values to floating-point numbers using Python's
built-in float() function.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | number | `INT` | 0 | forceInput=True |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts an integer to a floating-point number.
        Transforms integer values to their exact floating-point representation.
        Useful when numeric operations require float inputs.
        """

        def execute(self, number: int = 0) -> tuple[float]:
            try:
                return (float(number),)
            except (TypeError, ValueError):
                raise ValueError("Number must be convertible to integer")
    ```

## IntMinMax

Determines the minimum or maximum value between two integers.

This class compares two integer inputs and returns either the smaller or larger value based on
the specified mode of operation.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | a | `INT` | 0 | forceInput=True |
| required | b | `INT` | 0 | forceInput=True |
| required | mode | `LIST` | min |  |

### Returns

| Name | Type |
|------|------|
| int | `INT` |


??? note "Source code"

    ```python
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
                    "mode": (["min", "max"], {"default": "min"}),
                }
            }

        RETURN_TYPES = ("INT",)
        FUNCTION = "execute"
        CATEGORY = NUMBERS_CAT
        CLASS_ID = "int_minmax"
        DESCRIPTION = """
        Determines the minimum or maximum value between two integers.
        Compares two integer inputs and returns either the smaller or larger value based on the specified mode of operation.
        """

        def execute(self, a: int = 0, b: int = 0, mode: str = "min") -> tuple[int]:
            if mode in OP_FUNCTIONS:
                return (OP_FUNCTIONS[mode](a, b),)
            raise ValueError(f"Unsupported mode: {mode}")
    ```

## RandomNumber

Generates a random integer and its floating-point representation.

This class produces a random integer between 0 and MAX_INT and provides both the integer value
and its floating-point equivalent.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|

### Returns

| Name | Type |
|------|------|
| int | `INT` |
| float | `FLOAT` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Generates a random integer and its floating-point representation.
        Produces a random integer between 0 and MAX_INT and provides both the integer value and its float equivalent.
        The value changes each time the node is evaluated.
        """

        @staticmethod
        def get_random() -> tuple[int, float]:
            result = random.randint(0, MAX_INT)
            return (
                result,
                float(result),
            )

        def execute(self) -> tuple[int, float]:
            return RandomNumber.get_random()

        @classmethod
        def IS_CHANGED(cls) -> tuple[int, float]:  # type: ignore
            return RandomNumber.get_random()
    ```

## FloatMinMax

Determines the minimum or maximum value between two floating-point numbers.

This class compares two float inputs and returns either the smaller or larger value based on
the specified mode of operation.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | a | `FLOAT` | 0.0 | forceInput=True |
| required | b | `FLOAT` | 0.0 | forceInput=True |
| required | mode | `LIST` | min |  |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |


??? note "Source code"

    ```python
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
                    "mode": (["min", "max"], {"default": "min"}),
                }
            }

        RETURN_TYPES = ("FLOAT",)
        FUNCTION = "execute"
        CATEGORY = NUMBERS_CAT
        CLASS_ID = "float_minmax"
        DESCRIPTION = """
        Determines the minimum or maximum value between two floating-point numbers.
        Compares two float inputs and returns either the smaller or larger value based on the specified mode of operation.
        """

        def execute(self, a: float = 0.0, b: float = 0.0, mode: str = "min") -> tuple[float]:
            if mode in OP_FUNCTIONS:
                return (OP_FUNCTIONS[mode](a, b),)
            raise ValueError(f"Unsupported mode: {mode}")
    ```

## IntClamp

Clamps an integer value between specified minimum and maximum bounds.

This class provides functionality to constrain an integer input within a defined range. If the input
number is less than the minimum value, it returns the minimum value. If it's greater than the
maximum value, it returns the maximum value.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | number | `INT` | 0 | forceInput=True |
| required | max_value | `INT` | 0 | step=1 |
| required | min_value | `INT` | 0 | step=1 |

### Returns

| Name | Type |
|------|------|
| int | `INT` |


??? note "Source code"

    ```python
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
                    "max_value": (
                        "INT",
                        {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                    ),
                    "min_value": (
                        "INT",
                        {"default": 0, "min": -MAX_INT, "max": MAX_INT, "step": 1},
                    ),
                }
            }

        RETURN_TYPES = ("INT",)
        FUNCTION = "execute"
        CATEGORY = NUMBERS_CAT
        DESCRIPTION = """
        Clamps an integer value between specified minimum and maximum bounds.
        Constrains an integer input within a defined range,
        returning the min value if input is too low or max value if input is too high.
        """

        def execute(self, number: int = 0, max_value: int = 0, min_value: int = 0) -> tuple[int]:
            if max_value < min_value:
                raise ValueError("Max value must be greater than or equal to min value")
            if number < min_value:
                return (min_value,)
            if number > max_value:
                return (max_value,)
            return (number,)
    ```

## FloatOperator

Performs arithmetic operations on two floating-point numbers.

This class supports basic arithmetic operations between two floating-point numbers. The supported
operations are addition, subtraction, multiplication, and division.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | left | `FLOAT` | 0 | step=0.01 |
| required | right | `FLOAT` | 0 | step=0.01 |
| required | operator | `LIST` |  |  |

### Returns

| Name | Type |
|------|------|
| float | `FLOAT` |


??? note "Source code"

    ```python
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
        DEPRECATED = True
        DESCRIPTION = """
        Performs arithmetic operations on two floating-point numbers.
        Supports addition, subtraction, multiplication, division, and modulo operations between two float values.
        Returns the calculated result.
        """

        def execute(self, left: float = 0.0, right: float = 0.0, operator: str = "+") -> tuple[float]:
            if operator in BASIC_OPERATORS:
                return (BASIC_OPERATORS[operator](left, right),)

            raise ValueError(f"Unsupported operator: {operator}")
    ```

## MathOperator

Evaluates mathematical expressions with support for variables and multiple operators.

This class provides a powerful expression evaluator that supports variables (a, b, c, d) and
various mathematical operations. It can handle arithmetic, comparison, and logical operations.

### Returns

| Name | Type |
|------|------|
| int | `INT` |
| float | `FLOAT` |


??? note "Source code"

    ```python
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
    ```

## IntOperator

Performs arithmetic operations on two floats and returns an integer result.

This class supports basic arithmetic operations between two floating-point numbers and returns
the result as an integer. The supported operations are addition, subtraction, multiplication,
and division.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | left | `FLOAT` | 0 | step=0.01 |
| required | right | `FLOAT` | 0 | step=0.01 |
| required | operator | `LIST` |  |  |

### Returns

| Name | Type |
|------|------|
| int | `INT` |


??? note "Source code"

    ```python
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
        DEPRECATED = True
        DESCRIPTION = """
        Performs arithmetic operations on two floats and returns an integer result.
        Supports addition, subtraction, multiplication, and division between two float values.
        Returns the calculated result as an integer.
        """

        def execute(self, left: float = 0.0, right: float = 0.0, operator: str = "+") -> tuple[int]:
            if operator in BASIC_OPERATORS:
                return (int(BASIC_OPERATORS[operator](left, right)),)

            raise ValueError(f"Unsupported operator: {operator}")
    ```

## Float2Int

Converts a floating-point number to an integer through truncation.

This class handles the conversion of float values to integers by removing the decimal portion.
The conversion is performed using Python's built-in int() function, which truncates towards zero.

### Inputs

| Group | Name | Type | Default | Extras |
|-------|------|------|---------|--------|
| required | number | `FLOAT` | 0 | forceInput=True |

### Returns

| Name | Type |
|------|------|
| int | `INT` |


??? note "Source code"

    ```python
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
        DESCRIPTION = """
        Converts a floating-point number to an integer through truncation.
        Removes the decimal portion of a float value, truncating towards zero rather than rounding.
        Useful for workflows requiring integer values.
        """

        def execute(self, number: float = 0.0) -> tuple[int]:
            try:
                return (int(number),)
            except (TypeError, ValueError):
                raise ValueError("Number must be convertible to float")

    ```
