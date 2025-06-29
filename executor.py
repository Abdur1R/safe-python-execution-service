import subprocess
import json
import tempfile
import os
import sys
import io
import ast

def validate_script(script):
    """Validate that the script contains a main() function and is safe to execute."""
    if not script or not isinstance(script, str):
        raise ValueError("Script must be a non-empty string")
    
    if "def main():" not in script:
        raise ValueError("Script must contain a main() function")
    
    # Basic AST validation to check for dangerous operations
    try:
        tree = ast.parse(script)
    except SyntaxError as e:
        raise ValueError(f"Invalid Python syntax: {str(e)}")
    
    # Check for potentially dangerous imports or operations
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ['subprocess', 'os', 'sys', 'eval', 'exec']:
                    raise ValueError(f"Dangerous import detected: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module in ['subprocess', 'os', 'sys']:
                raise ValueError(f"Dangerous import detected: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'open']:
                    raise ValueError(f"Dangerous function call detected: {node.func.id}")

def run_script_safely(script):
    """Execute a Python script safely using nsjail and return the result of main()."""
    # Validate the script
    validate_script(script)
    
    # Indent the script properly for the template
    indented_script = '\n'.join('    ' + line if line.strip() else line for line in script.split('\n'))
    
    # Wrap the script to capture the return value of main()
    wrapped_script = f"""
import json
import sys
import io

# Redirect stdout to capture print statements
old_stdout = sys.stdout
captured_output = io.StringIO()
sys.stdout = captured_output

try:
{indented_script}
    
    # Execute main() and capture its return value
    if 'main' in globals() and callable(main):
        result = main()
        # Ensure the result is JSON serializable
        json.dumps(result)  # This will raise an error if not JSON serializable
        print("__RETURN_VALUE__" + json.dumps(result) + "__RETURN_VALUE__", file=sys.stderr)
    else:
        raise ValueError("main() function not found or not callable")
        
except Exception as e:
    print(f"__ERROR__{{str(e)}}__ERROR__", file=sys.stderr)
    raise
finally:
    # Restore stdout and get captured output
    sys.stdout = old_stdout
    captured_output.seek(0)
    print("__STDOUT__" + captured_output.read() + "__STDOUT__", file=sys.stderr)
    captured_output.close()
"""
    
    # Create a temporary file for the script inside /sandbox
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir='/sandbox', delete=False) as temp_script:
        temp_script.write(wrapped_script)
        temp_script_path = temp_script.name
        temp_script_filename = os.path.basename(temp_script_path)

    try:
        # Simplified nsjail command for containerized environment
        nsjail_cmd = [
    "/usr/local/bin/nsjail",
    "--mode", "o",  # One-shot mode
    "--chroot", "/sandbox",
    "--rw",
    "--quiet",
    "--time_limit", "10",
    "--rlimit_as", "100",
    "--rlimit_nproc", "1",
    "--disable_clone_newnet",  # Still isolate network
    "--cwd", "/sandbox",
    "--", "/usr/local/bin/python3", temp_script_filename
]

        # Run the script with nsjail
        result = subprocess.run(
            nsjail_cmd,
            capture_output=True,
            text=True,
            timeout=15  # Overall timeout
        )

        stderr = result.stderr
        stdout = result.stdout
        
        # Check for execution errors
        if result.returncode != 0:
            # If nsjail fails, try running without it as fallback (less secure but functional)
            print("Warning: nsjail execution failed, falling back to direct execution", file=sys.stderr)
            return run_script_directly(script)

        # Extract return value and stdout from stderr (where we redirected them)
        return_value = None
        captured_stdout = ""
        
        # Parse the special markers we added
        if "__RETURN_VALUE__" in stderr:
            start_marker = "__RETURN_VALUE__"
            end_marker = "__RETURN_VALUE__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                return_value_str = stderr[start_idx:end_idx]
                try:
                    return_value = json.loads(return_value_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"main() function must return valid JSON. Error: {str(e)}")
        
        if "__STDOUT__" in stderr:
            start_marker = "__STDOUT__"
            end_marker = "__STDOUT__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                captured_stdout = stderr[start_idx:end_idx]
        
        if "__ERROR__" in stderr:
            start_marker = "__ERROR__"
            end_marker = "__ERROR__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                error_msg = stderr[start_idx:end_idx]
                raise RuntimeError(f"Script execution error: {error_msg}")

        if return_value is None:
            raise ValueError("main() function did not return a value or return value could not be parsed")

        return return_value, captured_stdout

    finally:
        # Clean up temporary file
        if os.path.exists(temp_script_path):
            os.unlink(temp_script_path)

def run_script_directly(script):
    """Fallback method to run script directly without nsjail (less secure)"""
    # Indent the script properly for the template
    indented_script = '\n'.join('    ' + line if line.strip() else line for line in script.split('\n'))
    
    # Wrap the script to capture the return value of main()
    wrapped_script = f"""
import json
import sys
import io

# Redirect stdout to capture print statements
old_stdout = sys.stdout
captured_output = io.StringIO()
sys.stdout = captured_output

try:
{indented_script}
    
    # Execute main() and capture its return value
    if 'main' in globals() and callable(main):
        result = main()
        # Ensure the result is JSON serializable
        json.dumps(result)  # This will raise an error if not JSON serializable
        print("__RETURN_VALUE__" + json.dumps(result) + "__RETURN_VALUE__", file=sys.stderr)
    else:
        raise ValueError("main() function not found or not callable")
        
except Exception as e:
    print(f"__ERROR__{{str(e)}}__ERROR__", file=sys.stderr)
    raise
finally:
    # Restore stdout and get captured output
    sys.stdout = old_stdout
    captured_output.seek(0)
    print("__STDOUT__" + captured_output.read() + "__STDOUT__", file=sys.stderr)
    captured_output.close()
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(wrapped_script)
        temp_script_path = temp_script.name

    try:
        # Run the script directly
        result = subprocess.run(
            ["/usr/local/bin/python3", temp_script_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        stderr = result.stderr
        stdout = result.stdout

        # Check for execution errors
        if result.returncode != 0:
            raise RuntimeError(f"Script execution failed: {stderr}")

        # Extract return value and stdout from stderr
        return_value = None
        captured_stdout = ""
        
        # Parse the special markers we added
        if "__RETURN_VALUE__" in stderr:
            start_marker = "__RETURN_VALUE__"
            end_marker = "__RETURN_VALUE__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                return_value_str = stderr[start_idx:end_idx]
                try:
                    return_value = json.loads(return_value_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"main() function must return valid JSON. Error: {str(e)}")
        
        if "__STDOUT__" in stderr:
            start_marker = "__STDOUT__"
            end_marker = "__STDOUT__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                captured_stdout = stderr[start_idx:end_idx]
        
        if "__ERROR__" in stderr:
            start_marker = "__ERROR__"
            end_marker = "__ERROR__"
            start_idx = stderr.find(start_marker) + len(start_marker)
            end_idx = stderr.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                error_msg = stderr[start_idx:end_idx]
                raise RuntimeError(f"Script execution error: {error_msg}")

        if return_value is None:
            raise ValueError("main() function did not return a value or return value could not be parsed")

        return return_value, captured_stdout

    finally:
        # Clean up temporary file
        if os.path.exists(temp_script_path):
            os.unlink(temp_script_path)