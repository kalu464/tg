import asyncio, json, os, random, time
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import RetryAfter, Forbidden, BadRequest
import logging

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
    "8127451836:AAEtOmTDQ1xDq6z4Pt7RKTxe3wB8YkL7dSE",
    "8246543045:AAF-gybz6GSgwwzhGmzn9DICUCWVgTKtDFs",
    "8305497032:AAFijf94xkkug77Idd1qcAlyTqrk_G8XE_E",
    "8469860479:AAHO7arZqtSpC1YdFPw36p87voZz1FU3q3U",
    "8532194758:AAGEXqB6J-LAcJKP_UboPfa5KuGzwWxQ1jc",
    "8086748561:AAGzYA_aKDkMuHFl6msgTDDJ6bXiDh3q2Jo",
    "7786059783:AAGSJJ2fAcuIvF2kipYUrSOsy47VGVWprlM",
    "8352371524:AAHqqH0p5DP9Vl-oH-iHp3-McFfLYW-tcUI",
    "8582214609:AAGjz4Uk8hx2ydrca_b7Q4g65RxSRBz2sUE",
    "8521358090:AAF8zZxbArck9amgU0ozLEfmTfIP61YsQEQ",
    "8555351575:AAFhyq3fAIT8uo3WrevbYxokpRaXuxqY0cw",
]

# PEHLA TOKEN = MASTER BOT (commands receive + reply karta hai)
# Baaki sab WORKER BOTS (sirf kaam karte hain, koi reply nahi)
MASTER_TOKEN = TOKENS[0]

OWNER_ID = 5915051224
SUDO_FILE = "sudo.json"

# ---------------------------
# RAID TEXTS
# ---------------------------
RAID_TEXTS = [
    "NOBI IS  FUCKING YOUR MOM LIL NIGGA 🥱🤬🖕🏻",
    "😂😂😂😂SON OF MY SLUT 😂😂😂😂",
    "YOUR MOMS BUSY WITH ME LIL BRO 😌",
    "TMKC MAAR LUNGEE RAND KA BACCH3  !!🔥😂🩴",
    "😉😈🔥هههههههههههههه Teri maa रंडी",
    "😏𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "🥹😜HLO BBY MAJEE A RAHE HAI CHUDD NA MAI?",
    "🤬🖕🏻AAJ TERI MA NOBI PAPA SAI CHUDE GI ",
    "ITNI JALDI CHUDD GYA TU?🤮",
    "FASS FASS CHUDDD AAB TU 🤣😭",
    "RAAND KA BACCHE , NOBI PAPA JINDE BAAD BOL 🤣🖕",
    "TERI MA RUNDI?OKH?NOBI PAPA OP BOL 🤮🤢",
    "TERI MA KI CHUT MAI LODE OkH?",
    "AWAZ NICHE KR , TERI BAAP NOBI HERE 👿",
    "SAWAL MT PUCH , CHUP CHAAP CHUDD TU 😍",
]

# ---------------------------
# NCEMO EMOJIS
# ---------------------------
NCEMO_EMOJIS = [
    "🔥","⚡","💥","💀","🕊","💫","🌪","🐉","👑","🌟","💎","🎭","🚀","✨","🔮",
    "🎯","🌀","🐺","🦅","🐍","🎇","🎆","💠","💣","🧨","🎉","🎊","🌈","🌊","🌙",
    "⭐","🌞","🌝","🌛","🌚","☄️","🌋","🏆","🥇","🎖️","🏅","🎗️","🏵️","🌺","🌸",
    "🌼","🌻","🌹","⚓","🛡️","⚔️","🪄","🧿","🪶","🕹️","🎮","🎲","🧩","🎵","🎶",
    "🎼","🎧","🎤","🎷","🎸","🎺","🥁","📯","📀","📣","📯","🛸","🛰️","🏹","🗡️",
    "🛡️","🩸","⚗️","🔭","🔬","💉","🧪","📚","📖","📝","✒️","🖋️","🖊️","✏️","📐",
    "📏","🧭","🔧","⚙️","🔩","🧱","🏗️","🏛️","🧭","🗺️","🧭","🔔","🔕","💡","🔦"
]

# ---------------------------
# GLOBAL STATE
# ---------------------------
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}
with open(SUDO_FILE, "w") as f:
    json.dump(list(SUDO_USERS), f)

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

group_tasks = {}          # chat_id -> bot_id -> task
slide_targets = set()
slidespam_targets = set()
swipe_mode = {}
spam_tasks = {}           # chat_id -> bot_id -> task

# Yahan worker bots store honge (sirf Bot objects, no Application)
worker_bots: list[Bot] = []
# Master application
master_app: Application = None

logging.basicConfig(level=logging.WARNING)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            return await update.message.reply_text("❌ You are not sudo, bitch.")
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid != OWNER_ID:
            return await update.message.reply_text("❌ Only owner can do this.")
        return await func(update, context)
    return wrapper

# ---------------------------
# HELPER: get all bots (master + workers)
# ---------------------------
def all_bots() -> list[Bot]:
    bots = []
    if master_app and master_app.bot:
        bots.append(master_app.bot)
    bots.extend(worker_bots)
    return bots

# ---------------------------
# LOOP FUNCTION — no artificial delay, Telegram flood-wait handle karta hai
# ---------------------------
async def bot_loop(bot: Bot, chat_id: int, base: str, mode: str):
    i = 0
    while True:
        try:
            if mode == "raid":
                text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            else:
                text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            # Minimal yield to keep event loop responsive
            await asyncio.sleep(0)
        except RetryAfter as e:
            # Telegram ne flood wait bola — exactly utna hi ruko
            await asyncio.sleep(e.retry_after)
        except asyncio.CancelledError:
            break
        except (Forbidden, BadRequest) as e:
            print(f"[SKIP] Bot {bot.id} can't set title in {chat_id}: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[WARN] Bot {bot.id} in chat {chat_id}: {e}")
            await asyncio.sleep(1)

# ---------------------------
# SPAM LOOP — continuous, flood-wait handle
# ---------------------------
async def spam_loop_fn(bot: Bot, chat_id: int, texts: list[str]):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id, texts[i % len(texts)])
            i += 1
            await asyncio.sleep(0)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except asyncio.CancelledError:
            break
        except (Forbidden, BadRequest) as e:
            print(f"[SKIP] Bot {bot.id} spam in {chat_id}: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[WARN] Bot {bot.id} spam in {chat_id}: {e}")
            await asyncio.sleep(1)

# ---------------------------
# COMMANDS (MASTER BOT ONLY RESPOND KARTA HAI)
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𓆩𓆩⃟⚡𝐍𝐎𝐁𝐈𝐗 ~ भगवान हूँ - 🔱 ⃟𓆪𓆪\n"
        "✨ Welcome! Use /help to explore the command menu."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𓆩𓆩⃟⚡𝐍𝐎𝐁𝐈𝐗 ~ भगवान हूँ - 🔱 ⃟𓆪𓆪\n"
        "           ✦ ᴏғғɪᴄɪᴀʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ ✦\n"
        "────────────────────────────────\n\n"
        "⚡ 𝐆𝐂 𝐋𝐎𝐎𝐏𝐒\n"
        "/gcnc <text>\n"
        "/ncemo <text>\n"
        "/stopgcnc\n"
        "/stopall\n"
        "/status\n"
        f"/gcspam <text>\n"
        "/stopspam\n\n"
        "🎯 𝐒𝐋𝐈𝐃𝐄 & 𝐒𝐏𝐀𝐌\n"
        "/targetslide (reply)\n"
        "/stopslide (reply)\n"
        "/slidespam (reply)\n"
        "/stopslidespam (reply)\n\n"
        "⚡ 𝐒𝐖𝐈𝐏𝐄 𝐌𝐎𝐃𝐄\n"
        "/swipe <name>\n"
        "/stopswipe\n\n"
        "👑 𝐒𝐔𝐃𝐎 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓\n"
        "/addsudo (reply)\n"
        "/delsudo (reply)\n"
        "/listsudo\n\n"
        "🛠 𝐌𝐈𝐒𝐂\n"
        "/myid\n"
        "/ping\n\n"
        "────────────────────────────────\n"
        "✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ɴᴏʙɪx ✦"
    )

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    latency = int((end_time - start_time) * 1000)
    await msg.edit_text(f"🏓 Pong! ✅ {latency} ms")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

# --- GC Loops ---
@only_sudo
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gcnc <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    bots = all_bots()
    group_tasks.setdefault(chat_id, {})
    started = 0
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raid"))
            group_tasks[chat_id][bot.id] = task
            started += 1
    await update.message.reply_text(f"🔄 GC loop started — {started} bots running parallel!")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    bots = all_bots()
    group_tasks.setdefault(chat_id, {})
    started = 0
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "emoji"))
            group_tasks[chat_id][bot.id] = task
            started += 1
    await update.message.reply_text(f"🔄 Emoji loop started — {started} bots running parallel!")

@only_sudo
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
    await update.message.reply_text("⏹ Loop stopped in this GC.")

@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(group_tasks.keys()):
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
    for chat_id in list(spam_tasks.keys()):
        for task in spam_tasks[chat_id].values():
            task.cancel()
        spam_tasks[chat_id] = {}
    await update.message.reply_text("⏹ All loops + spam stopped.")

@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bots = all_bots()
    msg = f"📊 Total bots: {len(bots)} (1 master + {len(worker_bots)} workers)\n\n"
    msg += "🔄 Active GC Loops:\n"
    for chat_id, tasks in group_tasks.items():
        active = sum(1 for t in tasks.values() if not t.done())
        msg += f"  Chat {chat_id}: {active} bots\n"
    msg += "\n💥 Active Spam:\n"
    for chat_id, tasks in spam_tasks.items():
        active = sum(1 for t in tasks.values() if not t.done())
        msg += f"  Chat {chat_id}: {active} bots\n"
    await update.message.reply_text(msg or "No active loops.")

# --- SUDO ---
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid)
        save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid)
            save_sudo()
            await update.message.reply_text(f"🗑 {uid} removed from sudo.")

@only_sudo
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 SUDO USERS:\n" + "\n".join(map(str, SUDO_USERS)))

# --- Slide / Spam / Swipe ---
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slide_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🎯 Target slide added.")

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slide_targets.discard(uid)
        await update.message.reply_text("🛑 Target slide stopped.")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("💥 Slide spam started.")

@only_sudo
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.discard(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🛑 Slide spam stopped.")

@only_sudo
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /swipe <name>")
    swipe_mode[update.message.chat_id] = " ".join(context.args)
    await update.message.reply_text(f"⚡ Swipe mode ON: {swipe_mode[update.message.chat_id]}")

@only_sudo
async def stopswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    swipe_mode.pop(update.message.chat_id, None)
    await update.message.reply_text("🛑 Swipe mode stopped.")

# --- Auto Replies (master bot hi reply karega) ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.message.from_user.id
    chat_id = update.message.chat_id
    if uid in slide_targets:
        for text in RAID_TEXTS:
            await update.message.reply_text(text)
    if uid in slidespam_targets:
        for text in RAID_TEXTS:
            await update.message.reply_text(text)
    if chat_id in swipe_mode:
        for text in RAID_TEXTS:
            await update.message.reply_text(f"{swipe_mode[chat_id]} {text}")

# --- GC Spam (sab bots parallel chalte hain) ---
@only_sudo
async def gcspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    texts = [" ".join(context.args)] if context.args else RAID_TEXTS
    bots = all_bots()
    spam_tasks.setdefault(chat_id, {})
    started = 0
    for bot in bots:
        if bot.id not in spam_tasks[chat_id]:
            task = asyncio.create_task(spam_loop_fn(bot, chat_id, texts))
            spam_tasks[chat_id][bot.id] = task
            started += 1
    if started:
        await update.message.reply_text(f"💥 Spam started — {started} bots running parallel!")
    else:
        await update.message.reply_text("⚠️ All bots already spamming in this GC.")

@only_sudo
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id].values():
            task.cancel()
        spam_tasks[chat_id] = {}
        await update.message.reply_text("🛑 Spam stopped in this GC.")
    else:
        await update.message.reply_text("⚠️ No spam running in this GC.")

# ---------------------------
# BUILD MASTER APP (with all command handlers)
# ---------------------------
def build_master_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))
    app.add_handler(CommandHandler("targetslide", targetslide))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("slidespam", slidespam))
    app.add_handler(CommandHandler("stopslidespam", stopslidespam))
    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("stopswipe", stopswipe))
    app.add_handler(CommandHandler("gcspam", gcspam))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    return app

# ---------------------------
# RUN ALL
# ---------------------------
async def run_all_bots():
    global master_app, worker_bots

    # Master bot setup
    print(f"[*] Starting MASTER bot (token index 0)...")
    master_app = build_master_app(MASTER_TOKEN)
    await master_app.initialize()
    await master_app.start()
    await master_app.updater.start_polling()
    print(f"[✓] Master bot started: {master_app.bot.id}")

    # Worker bots — sirf Bot object, koi Application nahi
    # Yeh bots tasks execute karte hain, updates receive nahi karte
    for i, token in enumerate(TOKENS[1:], start=1):
        if not token.strip():
            continue
        try:
            bot = Bot(token=token)
            # Bot ko initialize karein
            me = await bot.get_me()
            worker_bots.append(bot)
            print(f"[✓] Worker bot {i} started: {me.id} (@{me.username})")
        except Exception as e:
            print(f"[✗] Worker bot {i} failed: {e}")

    total = 1 + len(worker_bots)
    print(f"\n🚀 All bots ready! 1 master + {len(worker_bots)} workers = {total} total")
    print("Master bot handles commands. All bots run tasks in parallel.\n")

    # Forever chalo
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_all_bots())
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
