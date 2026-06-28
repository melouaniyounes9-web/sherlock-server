from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('q', '').strip()
    if not username:
        return jsonify({"results": []})
    
    try:
        # تشغيل شيرلوك مع طلب إخراج النتائج في الشاشة (stdout) مباشرة
        # وتجاهل أي محاولة للكتابة في ملفات JSON
        cmd = ["sherlock", username, "--no-color", "--timeout", "3"]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        
        # استخراج السطور التي تحتوي على روابط فقط
        links = [line.strip() for line in result.splitlines() if "http" in line]
        
        return jsonify({"results": links})
    except Exception as e:
        # إرجاع الخطأ كقائمة فارغة حتى لا يتعطل التطبيق
        return jsonify({"results": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
