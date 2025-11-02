import sqlite3

# Connexion à la base
conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

# Lire les conversations
cursor.execute("SELECT id, user_question, bot_answer, created_at FROM conversations ORDER BY id DESC")

rows = cursor.fetchall()

if not rows:
    print("⚠️ Aucune donnée trouvée dans la base.")
else:
    print("\n📘 Conversations enregistrées :\n")
    for row in rows:
        print(f"🆔 {row[0]} | 🧍‍♂️ {row[1]}\n🤖 {row[2]}\n📅 {row[3]}\n{'-'*60}")

conn.close()
