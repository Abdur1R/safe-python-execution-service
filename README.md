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

## Deployment

### Google Cloud Run

1. Build and push the image to Google Container Registry:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/safe-python-execution .
docker push gcr.io/YOUR_PROJECT_ID/safe-python-execution
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy safe-python-execution \
  --image gcr.io/YOUR_PROJECT_ID/safe-python-execution \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## Security Features

- **nsjail Sandboxing**: Isolates execution environment
- **Resource Limits**: 
  - 10-second execution timeout
  - 100MB memory limit
  - Single process limit
- **Input Validation**: AST-based validation for dangerous operations
- **Non-root Execution**: Runs as user ID 1000
- **Read-only Mounts**: System directories mounted as read-only
- **Chroot Environment**: Restricted file system access

## Error Handling

The service returns appropriate HTTP status codes:

- `400 Bad Request`: Invalid input (missing main function, invalid JSON, etc.)
- `500 Internal Server Error`: Execution errors (timeout, memory limit, etc.)

## Limitations

- Scripts must contain a `main()` function
- `main()` function must return JSON-serializable data
- No access to dangerous modules (subprocess, os, sys, eval, exec)
- 10-second execution timeout
- 100MB memory limit
- Single process execution

## Troubleshooting

### Common Errors

1. **"Script must contain a main() function"**: Ensure your script defines a `main()` function
2. **"main() function must return valid JSON"**: Make sure your `main()` function returns JSON-serializable data
3. **"Dangerous import detected"**: Remove imports of subprocess, os, sys, eval, or exec
4. **"Script execution failed"**: Check for syntax errors or runtime issues in your script

### Health Check

Test if the service is running:
```bash
curl http://localhost:8080/health
```
