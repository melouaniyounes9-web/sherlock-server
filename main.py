from flask import Flask, request, jsonify
import os
import sys

# استيراد شيرلوك برمجياً لضمان العمل داخل Render بدون subprocess
try:
    from sherlock.sherlock import Sherlock
    from sherlock.sites import SitesInformation
except ImportError:
    # محاولة إضافة المسار إذا كانت البيئة مختلفة
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'sherlock')))
    from sherlock import Sherlock
    from sherlock.sites import SitesInformation

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    # تنظيف المدخلات وإزالة الفراغات تماماً
    username = request.args.get('q', '').strip().replace(" ", "")
    if not username:
        return jsonify({"results": ["ERROR: Username cannot be empty"]})
    
    try:
        # تحميل قائمة المواقع المدعومة من شيرلوك
        sites = SitesInformation()
        
        # إنشاء كائن الفحص وضبط المهلة
        sherlock = Sherlock(sites)
        
        # تنفيذ الفحص البرمجي المباشر
        results = sherlock.search(username, timeout=3)
        
        # استخراج الروابط المكتشفة بنجاح فقط
        detected_links = []
        for site_name, site_data in results.items():
            if site_data.get('status') == 'CLAIMED': # الحساب موجود
                url = site_data.get('url_user')
                if url:
                    detected_links.append(f"{site_name}: {url}")
        
        if not detected_links:
            return jsonify({"results": [f"No targets found for: {username}"]})
            
        return jsonify({"results": detected_links})
        
    except Exception as e:
        return jsonify({"results": [f"SYSTEM_ERROR: {str(e)}"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
