import aiosqlite
import time
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                created_at  INTEGER DEFAULT (strftime('%s','now')),
                is_banned   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id       INTEGER,
                receiver_id     INTEGER NOT NULL,
                text            TEXT NOT NULL,
                created_at      INTEGER DEFAULT (strftime('%s','now')),
                is_read         INTEGER DEFAULT 0,
                reply_chain_id  INTEGER DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS anon_chats (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                initiator_id    INTEGER NOT NULL,
                target_id       INTEGER NOT NULL,
                message_id      INTEGER NOT NULL,
                created_at      INTEGER DEFAULT (strftime('%s','now')),
                is_active       INTEGER DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
            CREATE INDEX IF NOT EXISTS idx_messages_sender   ON messages(sender_id);
            CREATE TABLE IF NOT EXISTS reactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id      INTEGER NOT NULL,
                reactor_id  INTEGER NOT NULL,
                emoji       TEXT NOT NULL,
                created_at  INTEGER DEFAULT (strftime('%s','now')),
                UNIQUE(msg_id, reactor_id)
            );
        """)
        await db.commit()


async def upsert_user(user_id: int, username: str | None, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO users (user_id, username, full_name)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   username  = excluded.username,
                   full_name = excluded.full_name""",
            (user_id, username, full_name),
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def is_banned(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return bool(row and row[0])


async def ban_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
        )
        await db.commit()


async def save_message(
    sender_id: int | None,
    receiver_id: int,
    text: str,
    reply_chain_id: int | None = None,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO messages (sender_id, receiver_id, text, reply_chain_id)
               VALUES (?, ?, ?, ?)""",
            (sender_id, receiver_id, text, reply_chain_id),
        )
        await db.commit()
        return cur.lastrowid


async def get_message(msg_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE id = ?", (msg_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def mark_read(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,)
        )
        await db.commit()


async def get_unread_count(receiver_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0",
            (receiver_id,),
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def count_pending_messages(receiver_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0",
            (receiver_id,),
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def create_anon_chat(
    initiator_id: int, target_id: int, message_id: int
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO anon_chats (initiator_id, target_id, message_id)
               VALUES (?, ?, ?)""",
            (initiator_id, target_id, message_id),
        )
        await db.commit()
        return cur.lastrowid


async def get_anon_chat(chat_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM anon_chats WHERE id = ?", (chat_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None
async def save_reaction(msg_id: int, reactor_id: int, emoji: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO reactions (msg_id, reactor_id, emoji)
               VALUES (?, ?, ?)
               ON CONFLICT(msg_id, reactor_id) DO UPDATE SET emoji = excluded.emoji""",
            (msg_id, reactor_id, emoji),
        )
        await db.commit()


async def get_reaction(msg_id: int, reactor_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT emoji FROM reactions WHERE msg_id = ? AND reactor_id = ?",
            (msg_id, reactor_id),
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None
