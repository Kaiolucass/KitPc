from flask import Flask, make_response
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>O SITE ESTÁ VIVO!</h1><p>Se você está vendo isso, o problema é a conexão com o Banco de Dados ou Firebase.</p>"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)