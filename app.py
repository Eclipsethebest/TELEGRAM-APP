import os
import json
import asyncio
from flask import Flask, render_template_string, request, redirect, url_for, session
from pyrogram import Client

app = Flask(__name__)
app.secret_key = "dreclipse_super_secret_web_key_2026"

KEY_DB_FILE = "used_keys_db.json"
SESSION_NAME = "dreclipse_web_session"

API_ID = 2040
API_HASH = "b18445a39ef28e3383821282b93f6b53"

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

# Yardımcı Asenkron Pyrogram Fonksiyonları
async def send_code_async(phone):
    client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await client.connect()
    sent_code = await client.send_code(phone)
    phone_code_hash = sent_code.phone_code_hash
    await client.disconnect()
    return phone_code_hash

async def sign_in_async(phone, phone_code_hash, code):
    client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    try:
        await client.sign_in(phone, phone_code_hash, code)
    except Exception as e:
        # Şifre (2FA) gerekebilir
        pass
    me = await client.get_me()
    await client.disconnect()
    return me.id, me.first_name

async def fetch_dialogs_async():
    client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append({
            "id": dialog.chat.id,
            "title": dialog.chat.title or dialog.chat.first_name or "İsimsiz Sohbet",
            "type": str(dialog.chat.type.value)
        })
    await client.disconnect()
    return dialogs

async def send_messages_async(chat_id, message, count, delay_ms):
    client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    delay_sec = delay_ms / 1000.0
    for _ in range(count):
        await client.send_message(chat_id, message)
        await asyncio.sleep(delay_sec)
    await client.disconnect()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dreclipse Core - Real Telegram Automation</title>
    <style>
        * { box-sizing: border-box; }
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
        .container { background: #1e293b; padding: 30px 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); width: 100%; max-width: 420px; text-align: center; }
        h1 { color: #38bdf8; font-size: 26px; margin-bottom: 20px; font-weight: 800; letter-spacing: 1px; }
        p { font-size: 15px; color: #cbd5e1; margin-bottom: 15px; }
        input, select { width: 100%; padding: 15px; margin: 10px 0; background: #0f172a; border: 1px solid #475569; color: white; border-radius: 8px; font-size: 16px; outline: none; }
        input:focus, select:focus { border-color: #38bdf8; }
        button { background: #22c55e; color: white; border: none; padding: 15px; width: 100%; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 15px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3); }
        button:hover { background: #16a34a; transform: translateY(-2px); }
        .start-btn { background: #eab308; font-size: 22px; padding: 22px; letter-spacing: 2px; box-shadow: 0 4px 15px rgba(234, 179, 8, 0.4); }
        .start-btn:hover { background: #ca8a04; }
        .error { color: #ef4444; font-size: 14px; margin-top: 10px; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 6px; }
        .success { color: #22c55e; font-size: 18px; margin-bottom: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 DRECLIPSE CORE 🔥</h1>
        
        {% if step == 'login' %}
            <form method="POST">
                <p>Telegram Telefon Numaranızı Girin:</p>
                <input type="text" name="phone" placeholder="+905554443322" required>
                <button type="submit">Telegram Kodu İste</button>
                {% if error %}<div class="error">{{ error }}</div>{% endif %}
            </form>
        {% elif step == 'verify_code' %}
            <form method="POST">
                <p>Telegram'dan gelen giriş kodunu yazın:</p>
                <input type="text" name="code" placeholder="12345" required>
                <button type="submit">Hesabı Bağla</button>
                {% if error %}<div class="error">{{ error }}</div>{% endif %}
            </form>
        {% elif step == 'license' %}
            <form method="POST">
                <p>Bağlanan: <b>{{ user_name }}</b><br>Lisans Key'inizi Girin:</p>
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
                <p>Hedef Sohbet / Grup Seç:</p>
                <select name="chat_id" required>
                    {% for chat in chats %}
                        <option value="{{ chat.id }}">{{ chat.title }} ({{ chat.type }})</option>
                    {% endfor %}
                </select>
                <input type="text" name="message" placeholder="Gönderilecek mesaj..." required>
                <input type="number" name="count" placeholder="Mesaj Adedi" value="1" required>
                <input type="number" name="delay" placeholder="Gecikme (ms)" value="2000" required>
                <button type="submit">Gönderimi Başlat</button>
            </form>
        {% elif step == 'success_done' %}
            <div class="success">🚀 Mesajlar Gerçek Olarak Gönderildi!</div>
            <a href="/start_action" style="text-decoration: none;"><button>Yeni İşlem Yap</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    step = session.get("step", "login")
    error = None
    user_name = session.get("user_name", "")

    if request.method == "POST":
        if step == "login":
            phone = request.form.get("phone").strip()
            if phone:
                try:
                    hash_code = asyncio.run(send_code_async(phone))
                    session["phone"] = phone
                    session["phone_code_hash"] = hash_code
                    session["step"] = "verify_code"
                    return redirect(url_for("index"))
                except Exception as e:
                    error = f"Hata: {str(e)}"
            else:
                error = "Geçerli bir telefon numarası girin!"

        elif step == "verify_code":
            code = request.form.get("code").strip()
            phone = session.get("phone")
            phone_code_hash = session.get("phone_code_hash")
            try:
                uid, name = asyncio.run(sign_in_async(phone, phone_code_hash, code))
                session["user_id"] = str(uid)
                session["user_name"] = name
                session["step"] = "license"
                return redirect(url_for("index"))
            except Exception as e:
                error = f"Kod Hatalı: {str(e)}"

        elif step == "license":
            lkey = request.form.get("license_key").strip()
            db = load_db()
            user_id = session.get("user_id")
            
            if lkey == "KEY-FREE1":
                free_users = db.get("FREE_USERS", [])
                if user_id in free_users:
                    error = "Bu hesap için deneme hakkı kullanıldı!"
                else:
                    free_users.append(user_id)
                    db["FREE_USERS"] = free_users
                    save_db(db)
                    session["step"] = "dashboard"
                    return redirect(url_for("index"))
            elif lkey in MONTHLY_KEYS or lkey in LIFETIME_KEYS:
                if lkey in db:
                    if db[lkey] == user_id:
                        session["step"] = "dashboard"
                        return redirect(url_for("index"))
                    else:
                        error = "Bu key başka bir hesaba mühürlenmiş!"
                else:
                    db[lkey] = user_id
                    save_db(db)
                    session["step"] = "dashboard"
                    return redirect(url_for("index"))
            else:
                error = "Geçersiz key!"

    return render_template_string(HTML_TEMPLATE, step=step, error=error, user_name=user_name)

@app.route("/start_action", methods=["GET", "POST"])
def start_action():
    if request.method == "POST":
        chat_id = int(request.form.get("chat_id"))
        message = request.form.get("message")
        count = int(request.form.get("count"))
        delay = int(request.form.get("delay"))
        
        try:
            asyncio.run(send_messages_async(chat_id, message, count, delay))
            session["step"] = "success_done"
            return redirect(url_for("start_action"))
        except Exception as e:
            return f"Gönderim Hatası: {e}"
    
    try:
        chats = asyncio.run(fetch_dialogs_async())
        session["step"] = "chats"
        return render_template_string(HTML_TEMPLATE, step="chats", chats=chats)
    except Exception as e:
        return f"Sohbetler yüklenemedi: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
