import numpy as np

def calculate(
    operation: str,
    a: float,
    b: float):
    
    print("Calculator tool invoked!")
    operation = operation.lower()
    
    match operation:
        case "add":
            return np.add(a, b)
        
        case "subtract":
            return np.subtract(a, b)
        
        case "multiply":
            return np.multiply(a, b)
        
        case "divide":
            if b == 0:
                raise ValueError("Zero Division Error!")
            
            return np.divide(a, b)
        
        case "mod":
            if b == 0:
                raise ValueError("Zero Mod Error!")
            
            return np.mod(a, b)
        
        case "power":
            return np.pow(a, b)

        case _:
            raise ValueError("Unsupported operation!")