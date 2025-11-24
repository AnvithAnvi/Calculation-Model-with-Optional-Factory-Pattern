from app.logger_config import logger

def add(x: float, y: float) -> float:
    logger.info(f"Adding {x} + {y}")
    return x + y

def subtract(x: float, y: float) -> float:
    logger.info(f"Subtracting {x} - {y}")
    return x - y

def multiply(x: float, y: float) -> float:
    logger.info(f"Multiplying {x} * {y}")
    return x * y

def divide(x: float, y: float) -> float:
    if y == 0:
        logger.error("Division by zero attempted")
        raise ZeroDivisionError("Cannot divide by zero")
    logger.info(f"Dividing {x} / {y}")
    return x / y
