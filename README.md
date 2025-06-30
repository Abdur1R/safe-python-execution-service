# Safe Python Execution Service

A secure Python API service that executes arbitrary Python code in a sandboxed environment and returns the result of the `main()` function. The service uses nsjail for security isolation and supports basic libraries like pandas and numpy.

## Features

- **Secure Execution**: Uses nsjail for sandboxed execution with resource limits
- **Input Validation**: Validates scripts for dangerous operations and syntax
- **JSON Return**: Expects and validates that `main()` function returns JSON-serializable data
- **Stdout Capture**: Captures print statements separately from the return value
- **Resource Limits**: 10-second timeout, 100MB memory limit, single process
- **Basic Libraries**: Supports pandas, numpy, and other safe Python libraries

## API Endpoints

### POST /execute

Executes a Python script and returns the result of the `main()` function.

**Request Body:**
```json
{
  "script": "def main():\n    return {'message': 'Hello, World!'}"
}
```

**Response:**
```json
{
  "result": {"message": "Hello, World!"},
  "stdout": "Any print statements from the script"
}
```

**Error Response:**
```json
{
  "error": "Error message describing what went wrong"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Requirements

Your Python script must:

1. Contain a `main()` function
2. Have the `main()` function return JSON-serializable data
3. Not use dangerous imports (subprocess, os, sys, eval, exec)
4. Have valid Python syntax

## Examples

### Basic Example

```bash
curl -X POST https://your-service-url/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from Python!\"}"
  }'
```

### Using Pandas and Numpy

```bash
curl -X POST https://your-service-url/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import pandas as pd\nimport numpy as np\n\ndef main():\n    df = pd.DataFrame({\"A\": [1, 2, 3], \"B\": [4, 5, 6]})\n    print(\"DataFrame created\")\n    return {\"sum\": df.sum().to_dict(), \"mean\": df.mean().to_dict()}"
  }'
```

### Mathematical Calculation

```bash
curl -X POST https://your-service-url/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import numpy as np\n\ndef main():\n    numbers = [1, 2, 3, 4, 5]\n    print(f\"Processing {len(numbers)} numbers\")\n    return {\"sum\": sum(numbers), \"mean\": np.mean(numbers), \"std\": np.std(numbers)}"
  }'
```

## Local Development

### Prerequisites

- Docker

### Running Locally

1. Build the Docker image:
```bash
docker build -t safe-python-execution .
```

2. Run the service:
```bash
docker run -p 8080:8080 safe-python-execution
```

3. Test the service:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"status\": \"success\"}"
  }'
```

### You can access this API Service using below url (It's deployed in google cloud):

https://safe-python-execution-59672737869.us-central1.run.app/execute