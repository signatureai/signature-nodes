import random

from ...categories import NUMBERS_CAT
from ...shared import MAX_INT


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
