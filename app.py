from flask import Flask, render_template, request, jsonify
import openai
import os
import sys

app = Flask(__name__)

# Vérifie que la clé OpenAI est définie
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La variable d'environnement OPENAI_API_KEY n'est pas définie!")

# Initialise le client OpenAI
openai.api_key = api_key

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
        return jsonify({'question': question, 'answer': answer})
    except Exception as e:
        return jsonify({'question': question, 'answer': f"❌ Erreur lors de la requête : {str(e)}"})

# --- Serveur local pour Windows ---
if __name__ == '__main__':
    if sys.platform.startswith("win"):
        print("Mode développement Windows : lancement avec Flask")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from waitress import serve
        print("Mode production Linux/macOS : lancement avec Waitress")
        serve(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
