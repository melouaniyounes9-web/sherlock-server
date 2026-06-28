import os
import subprocess
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Sherlock Cloud Server is Live and Running smoothly!"

@app.route('/search', methods=['GET'])
def search_username():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Missing parameter 'q'"}), 400

    print(f"Target Username received: {query}")

    # Run Sherlock CLI inside Render container
    try:
        command = ["sherlock", query, "--json", "output.json", "--timeout", "1"]
        subprocess.run(command, check=False)
        
        # Check and parse results
        output_file = f"{query}.json"
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter and collect only found profile links
            found_urls = []
            for site, info in data.items():
                if info.get("status") == "CLAIMED":
                    found_urls.append(info.get("url_user"))
            
            # Clean up the generated file to save space
            os.remove(output_file)
            return jsonify({"results": found_urls})
            
        return jsonify({"results": []})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
