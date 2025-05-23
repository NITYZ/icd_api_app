import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def get_access_token():
    url = 'https://icd.who.int/icdapi/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('ICD_CLIENT_ID'),
        'client_secret': os.getenv('ICD_CLIENT_SECRET')
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

@app.route('/')
def home():
    return jsonify({"message": "ICD API is alive!"})

@app.route('/icd')
def fetch_icd():
    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('https://id.who.int/icd/release/11/2023-01/mms', headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
