#!/usr/bin/env python3
"""
Example usage of the Safe Python Execution Service
"""

import requests
import json

# Service URL (change this to your deployed service URL)
SERVICE_URL = "http://localhost:8080"

def execute_script(script):
    """Execute a Python script via the API"""
    payload = {"script": script}
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Script executed successfully!")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
            if result['stdout']:
                print(f"Stdout: {result['stdout']}")
        else:
            print(f"✗ Script execution failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to service. Make sure it's running on localhost:8080")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def example_1_basic():
    """Basic example with simple return"""
    print("\n" + "="*50)
    print("Example 1: Basic Return")
    print("="*50)
    
    script = """
def main():
    return {"message": "Hello from Python!", "status": "success"}
"""
    execute_script(script)

def example_2_with_print():
    """Example with print statements"""
    print("\n" + "="*50)
    print("Example 2: With Print Statements")
    print("="*50)
    
    script = """
def main():
    print("Starting calculation...")
    result = 10 + 20
    print(f"Calculation result: {result}")
    return {"sum": result, "message": "Calculation completed"}
"""
    execute_script(script)

def example_3_numpy():
    """Example using numpy"""
    print("\n" + "="*50)
    print("Example 3: Using NumPy")
    print("="*50)
    
    script = """
import numpy as np

def main():
    print("Creating numpy array...")
    arr = np.array([1, 2, 3, 4, 5])
    print(f"Array: {arr}")
    
    return {
        "array": arr.tolist(),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "sum": int(np.sum(arr))
    }
"""
    execute_script(script)

def example_4_pandas():
    """Example using pandas"""
    print("\n" + "="*50)
    print("Example 4: Using Pandas")
    print("="*50)
    
    script = """
import pandas as pd

def main():
    print("Creating DataFrame...")
    data = {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "city": ["NYC", "LA", "Chicago"]
    }
    df = pd.DataFrame(data)
    print(f"DataFrame shape: {df.shape}")
    
    return {
        "data": df.to_dict('records'),
        "summary": {
            "count": len(df),
            "columns": df.columns.tolist(),
            "age_mean": float(df['age'].mean())
        }
    }
"""
    execute_script(script)

def example_5_error_handling():
    """Example showing error handling"""
    print("\n" + "="*50)
    print("Example 5: Error Handling")
    print("="*50)
    
    # Test script without main function
    script = """
def other_function():
    return "This should fail"
"""
    execute_script(script)

if __name__ == "__main__":
    print("Safe Python Execution Service - Examples")
    print("Make sure the service is running on localhost:8080")
    
    example_1_basic()
    example_2_with_print()
    example_3_numpy()
    example_4_pandas()
    example_5_error_handling()
    
    print("\n" + "="*50)
    print("Examples completed!")
    print("To run the service locally:")
    print("docker run -p 8080:8080 safe-python-execution") 