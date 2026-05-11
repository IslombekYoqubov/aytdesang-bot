# 🤫 Ayt desang — Anonim Iqror Boti

Telegram anonim xabar boti. Python + aiogram 3 + SQLite.

---

## 📁 Fayl strukturasi

\\\
aytdesang/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── database/
│   ├── __init__.py
│   └── db.py
├── handlers/
│   ├── start.py
│   ├── sender.py
│   ├── receiver.py
│   └── chat.py
├── middlewares/
│   └── moderation.py
└── utils/
    └── helpers.py
\\\

---

## 🚀 Railway Deploy

1. [railway.app](https://railway.app) ga kiring
2. GitHub repo ni ulang
3. Environment Variables qo'shing:

| Variable | Qiymati |
|----------|---------|
| BOT_TOKEN | BotFather dan |
| BOT_USERNAME | bot username |
| ADMIN_ID | Telegram ID |
| DB_PATH | aytdesang.db |

---

## ⚙️ Local ishga tushirish

\\\ash
git clone https://github.com/IslombekYoqubov/aytdesang-bot
cd aytdesang-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
\\\

---

## 🔒 Xavfsizlik

- .env faylini hech qachon git ga push qilmang
- .gitignore da .env, *.db, venv/ bolishi kerak
