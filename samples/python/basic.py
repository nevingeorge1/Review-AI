"""Basic Python sample module for AST intelligence testing."""

import math


def calculate_circle_area(radius: float) -> float:
    """Calculate the area of a circle given its radius."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * (radius ** 2)


def format_greeting(name: str, uppercase: bool = False) -> str:
    """Return a formatted greeting message."""
    greeting = f"Hello, {name}!"
    return greeting.upper() if uppercase else greeting
