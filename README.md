# 🤫 Ayt desang — Anonim Iqror Boti

Telegram anonim xabar boti. Python + aiogram 3 + SQLite.

---

## 📁 Fayl strukturasi

```
aytdesang/
├── main.py                  # Entry point
├── config.py                # Sozlamalar (.env o'qiydi)
├── requirements.txt
├── .env.example             # → .env ga ko'chirish
├── database/
│   ├── __init__.py
│   └── db.py                # Barcha DB operatsiyalari
├── handlers/
│   ├── start.py             # /start, link generation
│   ├── sender.py            # Anonim xabar yuborish (FSM)
│   ├── receiver.py          # Inbox, /next, share, report
│   └── chat.py              # Anonim reply/chat (FSM)
├── middlewares/
│   └── moderation.py        # Toxic filter + ban check
└── utils/
    └── helpers.py           # Keyboard builders, share text
```

---

## 🚀 Serverga deploy qilish (Ubuntu 22.04 / 24.04)

### 1. Server tayyorlash

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

### 2. Kodni yuklash

```bash
cd ~
git clone <YOUR_REPO_URL> aytdesang
# yoki scp/ftp orqali papkani yuklang
cd aytdesang
```

### 3. Virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. .env sozlash

```bash
cp .env.example .env
nano .env
```

`.env` ichida to'ldiring:
```
BOT_TOKEN=7xxxxxxxxx:AAF...     # @BotFather dan oling
BOT_USERNAME=aytdesang_bot      # @ belgisisiz
ADMIN_ID=123456789              # Sizning Telegram ID (@userinfobot dan bilib oling)
DB_PATH=aytdesang.db
```

### 5. Bir marta sinab ko'ring

```bash
source venv/bin/activate
python main.py
```

Bot ishlayotganini ko'rsangiz → `Ctrl+C` bosib to'xtating, keyingi bosqichga o'ting.

---

## ⚙️ systemd service (bot doim ishlab tursin)

### Service fayl yaratish

```bash
sudo nano /etc/systemd/system/aytdesang.service
```

Quyidagini yozing (username va path ni o'zgartiring):

```ini
[Unit]
Description=Ayt Desang Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_LINUX_USERNAME
WorkingDirectory=/home/YOUR_LINUX_USERNAME/aytdesang
ExecStart=/home/YOUR_LINUX_USERNAME/aytdesang/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### Ishga tushirish

```bash
sudo systemctl daemon-reload
sudo systemctl enable aytdesang
sudo systemctl start aytdesang
```

### Status tekshirish

```bash
sudo systemctl status aytdesang

# Real-time loglar:
sudo journalctl -u aytdesang -f
```

---

## 🔄 Kodni yangilash

```bash
cd ~/aytdesang
git pull                          # yoki yangi fayllarni yuklang

sudo systemctl restart aytdesang
sudo systemctl status aytdesang
```

---

## 📊 Admin buyruqlari

Bot ichida admin (ADMIN_ID) qila oladigan narsalar:
- Har bir report adminga Telegram xabari orqali keladi
- Foydalanuvchini ban qilish uchun DB ga to'g'ridan kirish mumkin:

```bash
cd ~/aytdesang
source venv/bin/activate
python3 -c "
import asyncio
from database import ban_user
asyncio.run(ban_user(USER_ID_HERE))
print('Banned!')
"
```

---

## 🔒 Xavfsizlik

- `.env` faylini **hech qachon** git ga push qilmang
- `.gitignore` ga qo'shing:

```
.env
*.db
__pycache__/
venv/
*.pyc
```

---

## 💰 Monetizatsiya (keyingi versiya)

V2 uchun qo'shish rejalashtirilgan:
- Hint packs (Telegram Stars orqali to'lov)
- VIP reveal
- Premium inbox

---

## 📞 Muammo bo'lsa

```bash
# Loglarni ko'rish
sudo journalctl -u aytdesang -n 100

# Botni qayta ishga tushirish
sudo systemctl restart aytdesang

# DB ni tekshirish
sqlite3 ~/aytdesang/aytdesang.db ".tables"
sqlite3 ~/aytdesang/aytdesang.db "SELECT COUNT(*) FROM users;"
sqlite3 ~/aytdesang/aytdesang.db "SELECT COUNT(*) FROM messages;"
```
