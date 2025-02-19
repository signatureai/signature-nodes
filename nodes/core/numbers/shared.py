import math
import operator as op

from ...utils import clamp

BASIC_OPERATORS = {
    "+": op.add,
    "-": op.sub,
    "*": op.mul,
    "/": op.truediv,
}


OP_FUNCTIONS = {
    "min": min,
    "max": max,
    "round": round,
    "sum": sum,
    "len": len,
    "log": math.log,
    "abs": abs,
    "clamp": clamp,
}
