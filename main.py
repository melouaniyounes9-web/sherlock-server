from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    # استقبال اسم المستخدم وإزالة المسافات لضمان عمل أداة شيرلوك
    username = request.args.get('q', '').strip().replace(" ", "")
    
    if not username:
        return jsonify({"results": ["ERROR: Username empty"]})
    
    try:
        # استدعاء الأداة عبر python -m sherlock لضمان التشغيل داخل البيئة المترجمة
        cmd = ["python", "-m", "sherlock", username, "--timeout", "3", "--no-color"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        
        # تصفية السطور التي تحتوي على روابط المواقع المكتشفة
        links = [line.strip() for line in result.stdout.splitlines() if "http" in line]
        
        if not links:
            return jsonify({"results": [f"No accounts found for @{username}"]})
            
        return jsonify({"results": links})
        
    except subprocess.TimeoutExpired:
        return jsonify({"results": ["ERROR: Scan timeout exceeded"]})
    except Exception as e:
        return jsonify({"results": [f"ERROR: {str(e)}"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
