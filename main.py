from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

def generate_targets(name_input):
    # تنظيف المدخلات وتوليد الاحتمالات الذكية للصيغ الثنائية
    clean_name = name_input.strip().lower()
    parts = clean_name.split()
    
    if len(parts) == 1:
        p = parts[0]
        return [p, f"{p}123", f"{p}_pro"]
    
    p1, p2 = parts[0], parts[1]
    return [
        f"{p1}_{p2}",         
        f"{p1}.{p2}",         
        f"{p1}{p2}",          
        f"{p1}{p2}123"        
    ]

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return "Error: Missing parameter 'q'."
    
    targets = generate_targets(query)
    final_results = []
    
    for target in targets:
        try:
            # تشغيل شيرلوك كأداة نظام مثبتة في الخلفية مباشرة لمنع مشاكل التحذيرات
            result = subprocess.check_output(
                ["sherlock", target, "--no-color", "--timeout", "8"], 
                stderr=subprocess.STDOUT, 
                text=True
            )
            
            for line in result.splitlines():
                if "http" in line and "[+]" in line:
                    clean_link = line.split(":")[-2] + ":" + line.split(":")[-1]
                    final_results.append(clean_link.strip())
                    
        except subprocess.CalledProcessError as e:
            if e.output:
                for line in e.output.splitlines():
                    if "http" in line and "[+]" in line:
                        clean_link = line.split(":")[-2] + ":" + line.split(":")[-1]
                        final_results.append(clean_link.strip())
        except Exception:
            pass
            
    # تنظيف المخرجات وإرسال الروابط النظيفة فقط لتطبيق الأندرويد
    if final_results:
        return "\n".join(set(final_results))
    else:
        return "[+] Scan complete. No active profiles found."

if __name__ == '__main__':
    # تهيئة المنفذ البرمجي تلقائياً حسب إعدادات خادم Render
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
