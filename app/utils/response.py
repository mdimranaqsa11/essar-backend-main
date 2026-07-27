from typing import Any


def success(response: Any = None, message: str = "Success") -> dict:
    """Standard success envelope used by every endpoint.

    Shape: { "status": true, "message": "...", "response": <data> }
    `response` is the actual data (a Pydantic Out model, a list, or None).
    """
    return {"status": True, "message": message, "response": response}


def error(message: str = "Something went wrong", response: Any = None) -> dict:
    """Standard error envelope. Used by the global exception handlers."""
    return {"status": False, "message": message, "response": response}
