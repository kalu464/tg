import asyncio, json, os, random, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
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

"8127451836:AAEtOmTDQ1xDq6z4Pt7RKTxe3wB8YkL7dSE",
    ]

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
with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)

def save_sudo():
    with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)

group_tasks = {}         
slide_targets = set()    
slidespam_targets = set()
swipe_mode = {}
apps, bots = [], []
delay = 1
spam_tasks = {}  # chat_id -> bot.id -> task
spam_delay = 1   # fixed 1s delay for /gcspam

logging.basicConfig(level=logging.INFO)

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
# LOOP FUNCTION
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    i = 0
    while True:
        try:
            if mode == "raid":
                text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            else:
                text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"[WARN] Bot error in chat {chat_id}: {e}")
            await asyncio.sleep(2)

# ---------------------------
# COMMANDS
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
        "/delay <sec>\n"
        "/status\n"
        "/gcspam <text>\n"
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
    if not context.args: return await update.message.reply_text("⚠️ Usage: /gcnc <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raid"))
            group_tasks[chat_id][bot.id] = task
    await update.message.reply_text("🔄 GC name loop started with raid texts.")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "emoji"))
            group_tasks[chat_id][bot.id] = task
    await update.message.reply_text("🔄 Emoji loop started with all bots.")

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
    await update.message.reply_text("⏹ All loops stopped.")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args: return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = max(0.5, float(context.args[0]))
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except: await update.message.reply_text("⚠️ Invalid number.")

@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Active Loops:\n"
    for chat_id, tasks in group_tasks.items():
        msg += f"Chat {chat_id}: {len(tasks)} bots running\n"
    await update.message.reply_text(msg)

# --- SUDO ---
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid); save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid); save_sudo()
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
    if not context.args: return await update.message.reply_text("⚠️ Usage: /swipe <name>")
    swipe_mode[update.message.chat_id] = " ".join(context.args)
    await update.message.reply_text(f"⚡ Swipe mode ON with name: {swipe_mode[update.message.chat_id]}")

@only_sudo
async def stopswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    swipe_mode.pop(update.message.chat_id, None)
    await update.message.reply_text("🛑 Swipe mode stopped.")

# --- Auto Replies ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid, chat_id = update.message.from_user.id, update.message.chat_id
    if uid in slide_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if uid in slidespam_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if chat_id in swipe_mode:
        for text in RAID_TEXTS: await update.message.reply_text(f"{swipe_mode[chat_id]} {text}")

# --- GC Spam ---
@only_sudo
async def gcspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    texts = [" ".join(context.args)] if context.args else RAID_TEXTS

    spam_tasks.setdefault(chat_id, {})
    started = 0

    for bot in bots:
        if bot.id not in spam_tasks[chat_id]:
            async def spam_loop(bot_instance):
                i = 0
                while True:
                    try:
                        await bot_instance.send_message(chat_id, texts[i % len(texts)])
                        i += 1
                        await asyncio.sleep(spam_delay)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        print(f"[WARN] Spam error in chat {chat_id}, bot {bot_instance.id}: {e}")
                        await asyncio.sleep(1)

            task = asyncio.create_task(spam_loop(bot))
            spam_tasks[chat_id][bot.id] = task
            started += 1

    if started:
        await update.message.reply_text(f"💥 Spam started with {started} bots!")
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
# BUILD APP & RUN
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay_cmd))
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

async def run_all_bots():
    global apps, bots
    for token in TOKENS:
        if token.strip():
            try:
                app = build_app(token)
                apps.append(app); bots.append(app.bot)
            except Exception as e:
                print("Failed building app:", e)

    for app in apps:
        try:
            await app.initialize(); await app.start(); await app.updater.start_polling()
        except Exception as e:
            print("Failed starting app:", e)

    print("Bot is running (all bots started).")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_bots())
