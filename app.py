import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_access_token():
    url = 'https://icd.who.int/icdapi/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('ICD_CLIENT_ID'),
        'client_secret': os.getenv('ICD_CLIENT_SECRET')
    }
    try:
        # ⚠️ Temporário: ignora verificação SSL
        response = requests.post(url, data=data, verify=False)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.SSLError as e:
        return jsonify({
            "error": "Erro de SSL - verificação de certificado falhou.",
            "detalhes": str(e)
        }), 500
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Erro ao conectar à API da OMS para obter o token.",
            "detalhes": str(e)
        }), 500

@app.route('/')
def home():
    return jsonify({"message": "ICD API is alive!"})

@app.route('/icd')
def fetch_icd():
    token = get_access_token()
    if isinstance(token, tuple):  # token com erro
        return token

    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://id.who.int/icd/release/11/2023-01/mms'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Erro ao buscar dados da classificação ICD.",
            "detalhes": str(e)
        }), 500

@app.route('/icd/search/<string:term>')
def search_icd(term):
    token = get_access_token()
    if isinstance(token, tuple):  # token com erro
        return token

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://id.who.int/icd/release/11/2023-01/mms/search?q={term}&linearization=foundation'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Erro ao buscar resultados para o termo ICD.",
            "detalhes": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
