from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
import concurrent.futures
import re
import os

app = Flask(__name__)

def generate_mutations(raw_input):
    """تحويل الحواف الصوتية المزخرفة وإنشاء احتمالات حقيقية مع اللاحقات الرقمية الشائعة"""
    clean_base = unidecode(raw_input.strip().lower()).replace(" ", "")
    if not clean_base:
        return []
        
    mutations = [clean_base]
    # أرقام الهوية والسنوات الشائعة جداً في حسابات الأشخاص والمفقودين
    suffixes = ["123", "99", "2000", "2001", "2002", "2003", "2004", "2005", "_official"]
    
    for s in suffixes:
        mutations.append(f"{clean_base}{s}")
        mutations.append(f"{clean_base}_{s}")
        
    return list(set(mutations))

def execute_google_dork(username):
    """إجراء فحص عميق حقيقي داخل فهرس قوقل لضمان جودة وصحة الروابط"""
    matched_records = []
    platforms = {
        "instagram.com": "Instagram",
        "tiktok.com": "TikTok",
        "facebook.com": "Facebook",
        "twitter.com": "Twitter_X",
        "reddit.com": "Reddit",
        "telegram.me": "Telegram",
        "t.me": "Telegram"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # بناء الاستعلام المركب للبحث داخل قوقل عن المنصات المستهدفة
    site_query = " OR ".join([f"site:{p}" for p in platforms.keys()])
    search_url = f"https://www.google.com/search?q={site_query} \"{username}\""
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # التحقق من أن الرابط ينتمي لإحدى المنصات وليس رابطاً داخلياً لقوقل
                for domain, plat_name in platforms.items():
                    if domain in href and "google.com" not in href:
                        clean_url_match = re.search(r'(https?://[^\s&]+)', href)
                        if clean_url_match:
                            final_url = clean_url_match.group(1)
                            
                            # حساب دقة المطابقة بناءً على احتواء الرابط على النمط البرمجي للاسم
                            confidence = 90 if username in final_url.lower() else 75
                            matched_records.append({
                                "platform": plat_name,
                                "url": final_url,
                                "confidence": confidence
                            })
    except Exception:
        pass
        
    return matched_records

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"results": []})

    # 1. توليد كافة الاحتمالات الصوتية والرقمية للاسم
    target_variants = generate_mutations(query)
    
    all_results = []
    
    # 2. إطلاق فحص متوازي فائق السرعة عبر خيوط المعالجة الـ Threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures_results = executor.map(execute_google_dork, target_variants)
        for res in futures_results:
            if res:
                all_results.extend(res)
                
    # إزالة الروابط المكررة لضمان نظافة ونقاء البيانات المستخرجة
    seen_urls = set()
    unique_results = []
    for item in all_results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_results.append(item)

    # إرجاع النتيجة بصيغة JSON مهيكلة للتكامل الكامل مع الداشبورد
    return jsonify({"results": unique_results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
