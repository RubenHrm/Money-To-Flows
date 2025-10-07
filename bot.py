import os
import sqlite3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# CONFIG
TOKEN = os.getenv("TOKEN")
ADMIN_USERNAME = "@RUBENHRM777"
ACHAT_LINK = "https://sgzxfbtn.mychariow.shop/prd_8ind83"
SEUIL_RECOMPENSE = 5
DB_FILE = "data.db"

if not TOKEN:
    raise RuntimeError("La variable d'environnement TOKEN n'est pas définie. Ajoute-la sur Render.")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Base SQLite (simple)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            parrain_id INTEGER,
            filleuls INTEGER DEFAULT 0,
            acheteurs INTEGER DEFAULT 0,
            recompense INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_user(user_id, username, parrain_id=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, parrain_id) VALUES (?, ?, ?)",
              (user_id, username, parrain_id))
    if parrain_id:
        c.execute("UPDATE users SET filleuls = filleuls + 1 WHERE user_id = ?", (parrain_id,))
    conn.commit()
    conn.close()

def count_acheteurs_of_parrain(parrain_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # On considère qu'un filleul est "acheteur" si son champ acheteurs > 0
    c.execute("SELECT COUNT(*) FROM users WHERE parrain_id = ? AND acheteurs > 0", (parrain_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    ref = args[0] if args else None
    parrain_id = None

    if ref and ref.startswith("ref_"):
        try:
            parrain_id = int(ref.split("ref_")[1])
            if parrain_id == user.id:
                parrain_id = None
        except:
            parrain_id = None

    if not get_user(user.id):
        add_user(user.id, user.username or user.full_name, parrain_id)
        if parrain_id:
            try:
                await context.bot.send_message(chat_id=parrain_id,
                                               text=f"🎉 Nouveau filleul ! @{user.username or user.first_name} s'est inscrit grâce à ton lien.")
            except Exception:
                pass

    await update.message.reply_text(
        f"👋 Bienvenue {user.first_name} !\n\n"
        "🎓 Pack Formations Business 2026\n\n"
        "Commandes :\n"
        "/achat  /parrainage  /dashboard  /recompense  /aide"
    )

async def achat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🛍️ Lien officiel :\n{ACHAT_LINK}")

async def parrainage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not get_user(user.id):
        add_user(user.id, user.username or user.full_name)
    lien = f"https://t.me/{context.bot.username}?start=ref_{user.id}"
    await update.message.reply_text(f"💸 Ton lien de parrainage :\n{lien}")

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = get_user(user.id)
    if not row:
        await update.message.reply_text("Aucune donnée. Fais /start pour t'inscrire.")
        return
    filleuls = row[3] or 0
    acheteurs = count_acheteurs_of_parrain(user.id)
    statut = "✅ Éligible" if acheteurs >= SEUIL_RECOMPENSE else "❌ Non éligible"
    await update.message.reply_text(
        f"📊 TON DASHBOARD\n\n👥 Filleuls : {filleuls}\n🛒 Acheteurs : {acheteurs}\n🏆 Statut : {statut}"
    )

async def recompense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    acheteurs = count_acheteurs_of_parrain(user.id)
    if acheteurs < SEUIL_RECOMPENSE:
        await update.message.reply_text(f"Tu as {acheteurs} filleuls acheteurs. Il t'en faut {SEUIL_RECOMPENSE}.")
    else:
        await update.message.reply_text("🎉 Félicitations ! Ta demande a été enregistrée. L'admin vérifiera et te contactera.")

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"/achat /parrainage /dashboard /recompense /aide\nSupport : {ADMIN_USERNAME}")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("achat", achat))
    app.add_handler(CommandHandler("parrainage", parrainage))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("recompense", recompense))
    app.add_handler(CommandHandler("aide", aide))
    print("🤖 Bot démarré avec succès...")
    app.run_polling()

if __name__ == "__main__":
    main()
