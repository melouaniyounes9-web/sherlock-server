from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# قائمة بالمنصات الشهيرة وبنية الروابط الخاصة بها للتحقق السريع
SITES = {
    "GitHub": "https://github.com/{username}",
    "Twitter/X": "https://twitter.com/{username}",
    "Instagram": "https://www.instagram.com/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Pinterest": "https://www.pinterest.com/{username}",
    "YouTube": "https://www.youtube.com/@{username}",
    "Telegram": "https://t.me/{username}",
    "Snapchat": "https://www.snapchat.com/add/{username}",
    "Steam": "https://steamcommunity.com/id/{username}"
}

@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('q', '').strip().replace(" ", "")
    if not username:
        return jsonify({"results": ["ERROR: Username cannot be empty"]})
        
    detected_links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # فحص الحسابات عبر إرسال طلبات حقيقية
    for site_name, url_template in SITES.items():
        url = url_template.format(username=username)
        try:
            # استخدام طلب من نوع GET مع مهلة زمنية قصيرة لمنع تعليق التطبيق
            response = requests.get(url, headers=headers, timeout=3, allow_redirects=True)
            
            # إذا كانت الاستجابة 200 (موجود) ولم يتم توجيهه لصفحة الخطأ الرئيسية للموقع
            if response.status_code == 200:
                # فلترة لبعض المواقع التي تعطي 200 حتى لو الحساب غير موجود (مثل تيك توك أو إنستغرام في بعض الحالات)
                if site_name == "Instagram" and "login" in response.url:
                    continue
                if site_name == "TikTok" and "notfound" in response.url:
                    continue
                
                detected_links.append(f"{site_name}: {url}")
        except Exception:
            continue

    if not detected_links:
        return jsonify({"results": [f"No targets found for: {username}"]})
        
    return jsonify({"results": detected_links})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
