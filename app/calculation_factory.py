# app/calculation_factory.py
from app.operations import add, subtract, multiply, divide, modulus, exponent
from app.schemas import OperationType

class CalculationFactory:
    """
    Factory to instantiate the correct calculation logic based on operation type.
    """
    
    @staticmethod
    def calculate(a: float, b: float, operation: OperationType) -> float:
        """
        Executes the math operation and returns the result.
        Validates input logic (like division by zero) via the underlying operations.
        """
        if operation == OperationType.ADD:
            return add(a, b)
        elif operation == OperationType.SUBTRACT:
            return subtract(a, b)
        elif operation == OperationType.MULTIPLY:
            return multiply(a, b)
        elif operation == OperationType.DIVIDE:
            return divide(a, b)
        elif operation == OperationType.MODULUS:
            return modulus(a, b)
        elif operation == OperationType.EXPONENT:
            return exponent(a, b)
        else:
            raise ValueError(f"Unknown operation type: {operation}")