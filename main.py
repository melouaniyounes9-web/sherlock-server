from flask import Flask, request
import requests
import os

app = Flask(__name__)

SITES = {
    "GitHub": "https://github.com/{username}",
    "Twitter_X": "https://twitter.com/{username}",
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
        return "ERROR: Username cannot be empty"
        
    detected_links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for site_name, url_template in SITES.items():
        url = url_template.format(username=username)
        try:
            response = requests.get(url, headers=headers, timeout=4, allow_redirects=True)
            if response.status_code == 200:
                if site_name == "Instagram" and "login" in response.url:
                    continue
                if site_name == "TikTok" and "notfound" in response.url:
                    continue
                detected_links.append(f"[+] {site_name}: {url}")
        except Exception:
            continue

    if not detected_links:
        return f"[-] No targets resolved for: {username}"
        
    # إرجاع النتائج كـ نص مفصول بأسطر مباشرة
    return "\n".join(detected_links)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
