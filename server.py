from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import json
import sys

app = Flask(__name__)
CORS(app, resources={
    r"/decode": {
        "origins": ["http://localhost:5173"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

DECODER_SCRIPT_PATH = 'server-flask\\newdecoder.py'
PYTHON_EXECUTABLE = sys.executable

@app.route('/decode', methods=['POST'])
def decode():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    text_to_decode = data.get('text', '')
    temp_file_path = "temp_input.txt"

    try:
        with open(temp_file_path, "w", encoding='utf-8') as temp_file:
            temp_file.write(text_to_decode)

        result = subprocess.run(
            [PYTHON_EXECUTABLE, DECODER_SCRIPT_PATH, '-f', temp_file_path],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )

        decoded_data_stdout = result.stdout
        try:
            decoded_json_result = json.loads(decoded_data_stdout)
            return jsonify(decoded_json_result)

        except json.JSONDecodeError as json_err:
            app.logger.error(f"Failed to decode JSON from script stdout: {json_err}")
            app.logger.error(f"Script stdout was: {decoded_data_stdout}")
            return jsonify({"error": "Internal server error: Decoder script output was not valid JSON.", "raw_output": decoded_data_stdout}), 500

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Decoder script failed with exit code {e.returncode}")
        app.logger.error(f"Stderr: {e.stderr}")
        return jsonify({"error": "Decoder script failed to execute.", "details": e.stderr}), 500

    except FileNotFoundError:
        app.logger.error("File not found. Check Python path and script path.")
        return jsonify({"error": "Could not find decoder script or python executable."}), 500

    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected internal server error occurred."}), 500

    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                app.logger.error(f"Error removing temporary file {temp_file_path}: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
