from flask import Flask, render_template, request, jsonify
import openai
import os
import sys
import sqlite3

app = Flask(__name__)

# --- Clé OpenAI ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La variable d'environnement OPENAI_API_KEY n'est pas définie!")
openai.api_key = api_key

# --- Base SQLite ---


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "chat.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            bot_answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_conversation(question, answer):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO conversations (user_question, bot_answer) VALUES (?, ?)', (question, answer))
        conn.commit()
        conn.close()
        print("💾 Conversation sauvegardée avec succès !")
    except Exception as e:
        print("❌ Erreur d’enregistrement dans la base :", e)


# Initialise la base au démarrage
init_db()

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question', '').strip()
    if not question:
        return jsonify({'question': question, 'answer': "❌ Veuillez poser une question."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant utile et poli."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content

        # Sauvegarde dans la base
        save_conversation(question, answer)

        return jsonify({'question': question, 'answer': answer})

    except Exception as e:
        return jsonify({'question': question, 'answer': f"❌ Erreur lors de la requête : {str(e)}"})

# --- Historique des conversations ---
@app.route('/history')
def history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_question, bot_answer, created_at FROM conversations ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return render_template('history.html', conversations=rows)


# --- Serveur ---
if __name__ == '__main__':
    if sys.platform.startswith("win"):
        print("Mode développement Windows : lancement avec Flask")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from waitress import serve
        print("Mode production Linux/macOS : lancement avec Waitress")
        serve(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
