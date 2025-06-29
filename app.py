from flask import Flask, request, jsonify
from executor import run_script_safely
import traceback

app = Flask(__name__)

@app.route("/execute", methods=["POST"])
def execute_script():
    # Validate request
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    data = request.get_json()
    if not data or "script" not in data:
        return jsonify({"error": "Missing 'script' in request body"}), 400

    script = data["script"]
    if not isinstance(script, str):
        return jsonify({"error": "'script' must be a string"}), 400

    if not script.strip():
        return jsonify({"error": "Script cannot be empty"}), 400

    try:
        result, stdout = run_script_safely(script)
        return jsonify({
            "result": result,
            "stdout": stdout
        })
    except ValueError as e:
        # Validation errors (missing main function, invalid JSON, etc.)
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        # Execution errors (timeout, memory limit, etc.)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)