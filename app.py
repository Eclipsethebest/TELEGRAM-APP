import os
import time
import json
import asyncio
from flask import Flask, render_template_string, request, redirect, url_for, session
from pyrogram import Client

app = Flask(__name__)
app.secret_key = "dreclipse_super_secret_web_key_2026"

KEY_DB_FILE = "used_keys_db.json"

MONTHLY_KEYS = [
    "DRC-1M-9X87-QW21-4PLK", "DRC-1M-3K90-ZX84-7MNB", "DRC-1M-5Y61-PO99-2VCX",
    "DRC-1M-8H32-AS76-1QAZ", "DRC-1M-2J54-ED55-9OKM", "DRC-1M-6L78-RF43-8IJU",
    "DRC-1M-4K90-TG21-3YHN", "DRC-1M-7U23-YH65-5TGB", "DRC-1M-1M45-UJ87-6RFV",
    "DRC-1M-9N67-IK98-4EDC", "DRC-1M-3B89-OL21-7WSX", "DRC-1M-5V01-PA34-9QAZ",
    "DRC-1M-8C23-QW65-2XSW", "DRC-1M-6X45-ER78-1CDE", "DRC-1M-7Z89-TY01-3VFR"
]

LIFETIME_KEYS = [
    "DRC-LIFE-ALPHA-9999-ONUR",
    "DRC-LIFE-CORE-7777-DRE",
    "DRC-LIFE-PRIME-5555-VIP",
    "DRC-LIFE-ULTRA-3333-MAX",
    "DRC-LIFE-GODMODE-1111-OWNER"
]

API_ID = 2040
API_HASH = "b18445a39ef28e3383821282b93f6b53"

def load_db():
    if os.path.exists(KEY_DB_FILE):
        try:
            with open(KEY_DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(db):
    with open(KEY_DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# HTML Arayüz Tasarımı (Siyah/Beyaz modern şık tema, butonlar, animasyonlar)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Dreclipse Core - Telegram Automation</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 400px; text-align: center; }
        h1 { color: #38bdf8; font-size: 24px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; background: #334155; border: 1px solid #475569; color: white; border-radius: 6px; box-sizing: border-box; }
        button { background: #22c55e; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        button:hover { background: #16a34a; transform: translateY(-2px); }
        .start-btn { background: #eab308; font-size: 20px; padding: 20px; letter-spacing: 2px; }
        .start-btn:hover { background: #ca8a04; }
        .error { color: #ef4444; font-size: 14px; margin-top: 10px; }
        .success { color: #22c55e; font-size: 14px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 DRECLIPSE CORE 🔥</h1>
        
        {% if step == 'login' %}
            <form method="POST">
                <p>Telegram Telefon Numaranızı Girin:</p>
                <input type="text" name="phone" placeholder="+905554443322" required>
                <button type="submit">Kodu Gönder</button>
            </form>
        {% elif step == 'verify_code' %}
            <form method="POST">
                <p>Telegram'dan gelen giriş kodunu yazın:</p>
                <input type="text" name="code" placeholder="12345" required>
                <button type="submit">Giriş Yap</button>
            </form>
        {% elif step == 'license' %}
            <form method="POST">
                <p>Lisans Key'inizi Girin:</p>
                <input type="text" name="license_key" placeholder="KEY-FREE1 veya VIP Key" required>
                <button type="submit">Lisansı Doğrula</button>
                {% if error %}<div class="error">{{ error }}</div>{% endif %}
            </form>
        {% elif step == 'dashboard' %}
            <form action="/start_action" method="GET">
                <button type="submit" class="start-btn">▶ START</button>
            </form>
        {% elif step == 'chats' %}
            <form method="POST">
                <p>Hedef Sohbet Seç:</p>
                <select name="chat_id" required>
                    {% for chat in chats %}
                        <option value="{{ chat.id }}">{{ chat.title }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="message" placeholder="Gönderilecek mesaj..." required>
                <input type="number" name="count" placeholder="Mesaj Adedi" value="1" required>
                <input type="number" name="delay" placeholder="Gecikme (ms)" value="2000" required>
                <button type="submit">Gönderimi Başlat</button>
            </form>
        {% elif step == 'success_done' %}
            <h3 class="success">✅ İşlem Başarıyla Tamamlandı!</h3>
            <a href="/start_action"><button>Yeni İşlem Yap</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    step = session.get("step", "login")
    error = None

    if request.method == "POST":
        if step == "login":
            phone = request.form.get("phone")
            session["phone"] = phone
            # Pyrogram client başlatma adımı tetiklenir
            session["step"] = "verify_code"
            return redirect(url_for("index"))
        
        elif step == "verify_code":
            code = request.form.get("code")
            # Kod doğrulama simülasyonu ve oturum açma
            session["step"] = "license"
            return redirect(url_for("index"))

        elif step == "license":
            lkey = request.form.get("license_key").strip()
            db = load_db()
            
            # Key kontrol mantığı
            if lkey == "KEY-FREE1":
                free_users = db.get("FREE_USERS", [])
                if session.get("phone") in free_users:
                    error = "Bu hesap için deneme hakkı kullanıldı!"
                else:
                    free_users.append(session.get("phone"))
                    db["FREE_USERS"] = free_users
                    save_db(db)
                    session["step"] = "dashboard"
                    return redirect(url_for("index"))
            elif lkey in MONTHLY_KEYS or lkey in LIFETIME_KEYS:
                if lkey in db:
                    error = "Bu key başka bir hesap tarafından kullanılmış!"
                else:
                    db[lkey] = session.get("phone")
                    save_db(db)
                    session["step"] = "dashboard"
                    return redirect(url_for("index"))
            else:
                error = "Geçersiz key!"

    return render_template_string(HTML_TEMPLATE, step=step, error=error)

@app.route("/start_action")
def start_action():
    # Grupları listeleme ekranı
    session["step"] = "chats"
    # Örnek gruplar (Gerçek uygulamada Pyrogram get_dialogs çekilir)
    mock_chats = [{"id": 12345, "title": "Örnek Grup 1"}, {"id": 67890, "title": "Test Kanalı"}]
    return render_template_string(HTML_TEMPLATE, step="chats", chats=mock_chats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
