from flask import Flask, request, jsonify
import json
import os
import sys

# إضافة مسار مجلد شيرلوك المحتوي على السكربتات لضمان الاستيراد المحلي
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'sherlock')))

app = Flask(__name__)

# مسار ملف المواقع الافتراضي داخل مجلد شيرلوك
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'sherlock', 'resources', 'data.json')
if not os.path.exists(DATA_FILE_PATH):
    # مسار بديل في حال اختلاف الهيكلية
    DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'data.json')

@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('q', '').strip().replace(" ", "")
    if not username:
        return jsonify({"results": ["ERROR: Username cannot be empty"]})
        
    try:
        import requests
        
        # قراءة قاعدة بيانات المواقع من شيرلوك محلياً
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            sites_data = json.load(f)
            
        detected_links = []
        # نأخذ عينة من أشهر 15 موقعاً لضمان سرعة الاستجابة وعدم حدوث Timeout في السيرفر المجاني
        target_sites = list(sites_data.items())[:15] 
        
        for site_name, site_info in target_sites:
            # بناء رابط الفحص الخاص بالمستخدم
            url = site_info["url"].format(username=username)
            error_type = site_info.get("errorType")
            
            try:
                # إرسال طلب فحص سريع بمحددات هاكر مخصصة (User-Agent)
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                response = requests.get(url, headers=headers, timeout=4)
                
                # التحقق من وجود الحساب بناءً على كود الحالة الاستجابية للموقع
                if error_type == "status_code":
                    if response.status_code == 200:
                        detected_links.append(f"{site_name}: {url}")
                elif error_type == "message":
                    error_msg = site_info.get("errorMsg")
                    if error_msg and error_msg not in response.text:
                        detected_links.append(f"{site_name}: {url}")
                else:
                    if response.status_code == 200:
                        detected_links.append(f"{site_name}: {url}")
                        
            except Exception:
                continue # تخطي أي موقع يسبب بطء أو حظر للشبكة
                
        if not detected_links:
            return jsonify({"results": [f"No targets found for: {username}"]})
            
        return jsonify({"results": detected_links})
        
    except Exception as e:
        return jsonify({"results": [f"SYSTEM_ERROR: {str(e)}"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
