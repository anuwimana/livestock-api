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
    return r.json()['access_token']


def get_animals(label, token=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    r = requests.get(f'{API}/animals/', headers=headers)
    print(label, '->', r.status_code)


get_animals('No token')
get_animals('Farmer', login('farmer@test.com', 'Test12345!'))
get_animals('Vet', login('vet@test.com', 'Test12345!'))