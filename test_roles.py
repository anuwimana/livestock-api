import os
import requests
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv('SUPABASE_URL')
KEY = os.getenv('SUPABASE_KEY')
API = 'http://127.0.0.1:8000/api'


def login(email, password):
    r = requests.post(
        f'{URL}/auth/v1/token?grant_type=password',
        headers={'apikey': KEY},
        json={'email': email, 'password': password},
    )
    r.raise_for_status()
    return {'Authorization': f"Bearer {r.json()['access_token']}"}


def show(label, r):
    print(f'{label} -> {r.status_code} {r.text[:120]}')


farmer = login('farmer@test.com', 'Test12345!')
vet = login('vet@test.com', 'Test12345!')
good = {'animal': 1, 'drug': 'Test drug', 'treat_date': '2026-11-18'}
bad = {'animal': 1, 'treat_date': '2026-11-18'}

show('1 Farmer adds treatment', requests.post(f'{API}/treatments/', json=good, headers=farmer))
show('2 Vet adds treatment   ', requests.post(f'{API}/treatments/', json=good, headers=vet))
show('3 Vet bad input        ', requests.post(f'{API}/treatments/', json=bad, headers=vet))
show('4 Missing animal       ', requests.get(f'{API}/animals/999/', headers=vet))
show('5 No token             ', requests.post(f'{API}/treatments/', json=good))