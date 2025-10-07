import os
import sqlite3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN")
ADMIN_USERNAME = "@RUBENHRM777"
ACHAT_LINK = "https://sgzxfbtn.mychariow.shop/prd_8ind83"
SEUIL_RECOMPENSE = 5
DB_FILE = "data.db"

if not TOKEN:
    raise RuntimeError("TOKEN manquant ! Ajoute-le dans Render > Environment Variables.")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- BASE DE DONNÉES ---
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
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, parrain_id) VALUES (?, ?, ?)",
        (user_id, username, parrain_id)
    )
    if parrain_id:
        c.execute("UPDATE users SET filleuls = filleuls + 1 WHERE user_id = ?", (parrain_id,))
    conn.commit()
    conn.close()

# --- COMMANDES ---
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
                await context.bot.send_message(
                    chat_id=parrain_id,
                    text=f"🎉 Nouveau filleul ! @{user.username or user.first_name} s'est inscrit grâce à ton lien."
                )
            except Exception:
                pass

    msg = (
        f"👋 Bienvenue {user.first_name} !\n\n"
        "🎓 Programme *Pack Formations Business 2026*\n\n"
        "Commandes utiles :\n"
        "/achat – Acheter le produit\n"
        "/parrainage – Obtenir ton lien\n"
        "/dashboard – Voir tes statistiques\n"
        "/recompense – Vérifier ta récompense\n"
        "/aide – Aide"
    )
    await update.message.reply_text(msg)

async def achat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🛍️ Voici ton lien d'achat :\n{ACHAT_LINK}")

async def parrainage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not get_user(user.id):
        add_user(user.id, user.username or user.full_name)
    lien = f"https://t.me/{context.bot.username}?start=ref_{user.id}"
    await update.message.reply_text(
        f"💸 Ton lien de parrainage :\n{lien}\n\n"
        "Partage-le et gagne dès que tes filleuls achètent !"
    )

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = get_user(user.id)
    if not row:
        await update.message.reply_text("Tu n'es pas encore enregistré. Fais /start pour commencer.")
        return
    filleuls, acheteurs = row[3], row[4]
    statut = "✅ Éligible" if acheteurs >= SEUIL_RECOMPENSE else "❌ Non éligible"
    await update.message.reply_text(
        f"📊 TON TABLEAU DE BORD\n\n"
        f"👥 Filleuls : {filleuls}\n"
        f"🛒 Acheteurs : {acheteurs}\n"
        f"🏆 Statut : {statut}"
    )

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 Commandes disponibles :\n"
        "/achat /parrainage /dashboard /recompense /aide\n\n"
        f"Support : {ADMIN_USERNAME}"
    )

# --- LANCEMENT DU BOT ---
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("achat", achat))
    app.add_handler(CommandHandler("parrainage", parrainage))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("aide", aide))
    print("🤖 Bot démarré avec succès...")
    app.run_polling()

if __name__ == "__main__":
    main()
