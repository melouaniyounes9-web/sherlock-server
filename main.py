from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('q', '').strip()
    if not username:
        return jsonify({"results": ["Missing query"]})
    
    try:
        # تشغيل شيرلوك وتوجيه المخرجات
        # تأكد من أن الأداة مثبتة في السيرفر عبر requirements.txt (باسم sherlock)
        result = subprocess.check_output(
            ["sherlock", username, "--timeout", "5", "--no-color"], 
            stderr=subprocess.STDOUT, text=True
        )
        
        # استخراج الروابط فقط
        links = [line.strip() for line in result.splitlines() if "http" in line]
        return jsonify({"results": links})
    except Exception as e:
        return jsonify({"results": ["No match found"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
