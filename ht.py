import asyncio
import random
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
MASTER_TOKEN = '8659773632:AAEnaj52bBhIaCt8FmKOusj7rZe3KDWYyQ0' 
OWNER_ID = 7137631428

SLAVE_TOKENS = [
    '7764099980:AAEt40LoM9rh4ogJJj5Ah8_bPblRGi0cffo',
    '8495105827:AAFkiPHgfT52dwihu7suQm2bFXZ1_of3DSQ',
    '8092434944:AAF76vSaCV2NkxoxlD_K_xdIKNrpxjv9chM',
    '8797747665:AAHt8MXIGzunaPBnDqSalqEMZCA9qomzaWA',
    '8798458261:AAHIrA2mGeKqmt2No4Kuxq_dO-_aMy6z7dI',
    '8457478362:AAE0Qs23-B1IXQ2D-BbUTulQkB4BfL2VKAY',
    '7977971867:AAG37K95HoyCCqFkl0qhSn8jeJkvPoAN084',
    '7694149155:AAGlFM-PqK4AREp4sBKzcYzdIfLllniLAgc',
    '8286081053:AAEWaWfFoo2pu2m0gm_bMxsXOFhoc3pvUmU',
    '8381854695:AAF6E8XHTbCQFFV5QzWNL0C8idP16fptJCs',
    '8565169021:AAE1ApkyASWZfzEMpGAFLnndpOA5vgjIAXM',
    '8572636779:AAH2MpBfw5plZjzSMaeyHrgx-J4A1lpG-uY',
    '8589509969:AAFLC_D0rr2yrDAHxnT0B6qUJimnAnHqqr4',
    '8489187122:AAE2nOf8HoZO2DmozWvO9Y4EfbZYA2ILLGQ',
    '8150893952:AAF5xpJRqhOfoRgBH8BKfQfdP9OI17ta4KA',
    '8287179107:AAH0tS4z7uQy-w6mWBjOp1l9BzHL-KS3QXU'

]
# =========================================================

state = {
    "delay": 2.0,
    "nc_speed": 1.2,
    "tasks": {},
    "run_flags": {}, # Har chat ke liye alag stop flag
    "sudo": set()
}

worker_bots = [Bot(token=t) for t in SLAVE_TOKENS]
all_bots = [Bot(token=MASTER_TOKEN)] + worker_bots

MIX_EMOJIS = ["⚡", "🔥", "🌀", "✨", "💎", "🌟", "🧿", "🚀", "⚔️", "👑", "👺"]
HEARTS = ["❤️", "💖", "💝", "💗", "💓", "💘", "💌", "💟"]

def make_aesthetic(text):
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                            "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵")
    return text.translate(mapping)

def is_sudo(user_id):
    return user_id == OWNER_ID or user_id in state["sudo"]

async def force_stop(cid):
    state["run_flags"][cid] = False # Flag off karo
    if cid in state["tasks"]:
        for t in state["tasks"][cid]:
            if not t.done():
                t.cancel()
        await asyncio.sleep(0.5) # Background cleanup ke liye waqt
        state["tasks"][cid] = []

# --- CORE TURBO FUNCTIONS (WITH FLAG CHECK) ---

async def dynamic_spam_loop(cid, txt):
    state["run_flags"][cid] = True
    try:
        while state["run_flags"].get(cid, False): # Har loop cycle pe check karega
            for b in all_bots:
                if not state["run_flags"].get(cid, False): break # Beech mein stop check
                try:
                    await b.send_message(chat_id=cid, text=txt)
                    await asyncio.sleep(0.05) 
                except: continue
            
            # Delay phase mein bhi stop check
            wait_time = state["delay"]
            while wait_time > 0 and state["run_flags"].get(cid, False):
                await asyncio.sleep(0.1)
                wait_time -= 0.1
    except asyncio.CancelledError: pass

async def turbo_nc_loop(bot_inst, cid, name, mode, offset):
    state["run_flags"][cid] = True
    try:
        await asyncio.sleep(offset)
        while state["run_flags"].get(cid, False):
            emo = random.choice(HEARTS if mode == 'heart' else MIX_EMOJIS)
            try:
                await bot_inst.set_chat_title(chat_id=cid, title=f"{emo} {name} {emo}")
            except: pass
            await asyncio.sleep(state["nc_speed"])
    except: pass

# --- HANDLERS ---

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id): return
    menu = f"""
⚡ 𝕄𝕒𝕚𝗇 𝕄𝕖𝗇𝕦 — ℂ𝕠𝕞𝕞𝖺𝕟𝕕𝕤
「 💎 PREMIUM CONTROL PANEL 💎 」
━━━━━━━━━━━━━━━━━━━━━━
🚀 SYSTEM CONTROL
━━━━━━━━━━━━━━━━━━━━━━
🔹 /ping — Check Online Bots
🔹 /delay [Sec] — Set Speed ({state['delay']}s)
🔹 /addsudo [ID] — Add Sudo User
🛑 /stopall — KILL EVERYTHING
━━━━━━━━━━━━━━━━━━━━━━
🌀 ANIMATION & LOOPS
━━━━━━━━━━━━━━━━━━━━━━
🔹 /heart [Name] — Heart NC ❤️
🔹 /ncemo [Name] — Emoji NC 🎭
━━━━━━━━━━━━━━━━━━━━━━
🔥 RAID & ATTACK
━━━━━━━━━━━━━━━━━━━━━━
🔹 /spam [Text] — Multi-Bot Spam
🔹 /attack [Name] — Full System Attack
━━━━━━━━━━━━━━━━━━━━━━
✨ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴛɪᴛᴀɴ ᴍᴀsᴛᴇʀ
"""
    await update.message.reply_text(menu)

async def cmd_attack(update, context):
    if not is_sudo(update.effective_user.id): return
    cid = update.effective_chat.id
    target = make_aesthetic(" ".join(context.args) or "TARGET")
    await force_stop(cid)
    
    state["run_flags"][cid] = True
    new_tasks = [asyncio.create_task(turbo_nc_loop(b, cid, target, 'emo', i*0.8)) for i, b in enumerate(all_bots)]
    new_tasks.append(asyncio.create_task(dynamic_spam_loop(cid, f"⚔️ {target} ⚔️")))
    state["tasks"][cid] = new_tasks
    await update.message.reply_text("⚔️ **ULTRA ATTACK INITIALIZED!**")

async def cmd_stop(update, context):
    if is_sudo(update.effective_user.id):
        await force_stop(update.effective_chat.id)
        await update.message.reply_text("🛑 **SYSTEM KILLED: Spam & NC Stopped.**")

async def cmd_spam(update, context):
    if not is_sudo(update.effective_user.id): return
    cid = update.effective_chat.id
    txt = " ".join(context.args) or "TITAN ON TOP"
    state["run_flags"][cid] = True
    t = asyncio.create_task(dynamic_spam_loop(cid, txt))
    state["tasks"].setdefault(cid, []).append(t)
    await update.message.reply_text("🚀 **Spam Started!**")

# --- OTHER COMMANDS ---
async def cmd_ping(u,c): await u.message.reply_text(f"🚀 {len(all_bots)} Bots Online!")
async def cmd_delay(u,c): 
    if is_sudo(u.effective_user.id) and c.args: 
        state["delay"] = float(c.args[0])
        await u.message.reply_text(f"✅ Delay: {state['delay']}s")

async def cmd_ncemo(u,c):
    if not is_sudo(u.effective_user.id): return
    cid, name = u.effective_chat.id, make_aesthetic(" ".join(c.args) or "TITAN")
    await force_stop(cid)
    state["run_flags"][cid] = True
    state["tasks"][cid] = [asyncio.create_task(turbo_nc_loop(b, cid, name, 'emo', i*0.8)) for i, b in enumerate(all_bots)]
    await u.message.reply_text("🎭 **Emoji NC Active!**")

async def cmd_heart(u,c):
    if not is_sudo(u.effective_user.id): return
    cid, name = u.effective_chat.id, make_aesthetic(" ".join(c.args) or "TITAN")
    await force_stop(cid)
    state["run_flags"][cid] = True
    state["tasks"][cid] = [asyncio.create_task(turbo_nc_loop(b, cid, name, 'heart', i*0.8)) for i, b in enumerate(all_bots)]
    await u.message.reply_text("❤️ **Heart NC Active!**")

# --- MAIN ---
def main():
    app = Application.builder().token(MASTER_TOKEN).build()
    app.add_handler(CommandHandler(["start", "help"], start_menu))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("delay", cmd_delay))
    app.add_handler(CommandHandler("attack", cmd_attack))
    app.add_handler(CommandHandler("stopall", cmd_stop))
    app.add_handler(CommandHandler("stopnc", cmd_stop))
    app.add_handler(CommandHandler("ncemo", cmd_ncemo))
    app.add_handler(CommandHandler("heart", cmd_heart))
    app.add_handler(CommandHandler("spam", cmd_spam))
    app.add_handler(CommandHandler("addsudo", lambda u,c: state["sudo"].add(int(c.args[0])) if u.effective_user.id == OWNER_ID else None))

    print(f"💎 TITAN FINAL FIXED! Bots: {len(all_bots)}")
    app.run_polling()

if __name__ == '__main__': main()
