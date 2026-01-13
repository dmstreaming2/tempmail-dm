from flask import Flask, render_template, jsonify, session
import requests
import time
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clave segura para sesiones

# API de 1secmail (servicio real y gratuito)
BASE_URL = "https://www.1secmail.com/api/v1/"

@app.route('/')
def index():
    # Si ya hay un correo en la sesión, no generar otro
    if 'email' not in session:
        domains = get_domains()
        if not domains:
            return "Error: No se pudieron obtener dominios del servicio.", 500
        
        # Generar nombre único
        username = "tmp" + str(int(time.time()))[-7:]
        domain = domains[0]
        session['email'] = f"{username}@{domain}"
        session['login'] = username
        session['domain'] = domain

    return render_template('index.html', email=session['email'])

@app.route('/inbox')
def inbox():
    if 'login' not in session or 'domain' not in session:
        return jsonify([])

    try:
        url = f"{BASE_URL}?action=getMessages&login={session['login']}&domain={session['domain']}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify([])
    except Exception as e:
        print("Error al obtener el buzón:", e)
        return jsonify([])

def get_domains():
    try:
        r = requests.get(f"{BASE_URL}?action=getDomainList", timeout=5)
        if r.status_code == 200:
            return r.json()
        else:
            return ["1secmail.com"]
    except:
        return ["1secmail.com"]

if __name__ == '__main__':
    app.run(debug=True)
