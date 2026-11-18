import uuid

from rest_framework.test import APITestCase

from .auth import SupabaseUser
from .models import Animal, Profile, Treatment


class LivestockApiTests(APITestCase):
    def setUp(self):
        self.farmer = Profile.objects.create(
            id=uuid.uuid4(), full_name='Farmer', role='farmer')
        self.vet = Profile.objects.create(
            id=uuid.uuid4(), full_name='Vet', role='vet')
        self.animal = Animal.objects.create(
            ear_tag='RW-001', species='cattle',
            birth_date='2021-03-10', owner=self.farmer)

    def login_as(self, profile):
        self.client.force_authenticate(user=SupabaseUser(profile))

    def treatment_data(self, **extra):
        data = {'animal': self.animal.id, 'drug': 'Penicillin',
                'treat_date': '2026-01-15'}
        data.update(extra)
        return data

    # 1. Success: farmer creates an animal, owner comes from the token
    def test_farmer_creates_animal(self):
        self.login_as(self.farmer)
        response = self.client.post('/api/animals/', {
            'ear_tag': 'RW-002', 'species': 'goat',
            'birth_date': '2023-01-01'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Animal.objects.get(ear_tag='RW-002').owner_id, self.farmer.id)

    # 2. Bad input: duplicate ear tag
    def test_duplicate_ear_tag_returns_400(self):
        self.login_as(self.farmer)
        response = self.client.post('/api/animals/', {
            'ear_tag': 'RW-001', 'species': 'cattle',
            'birth_date': '2022-01-01'})
        self.assertEqual(response.status_code, 400)

    # 3. Wrong role: farmer cannot add a treatment
    def test_farmer_cannot_add_treatment(self):
        self.login_as(self.farmer)
        response = self.client.post('/api/treatments/', self.treatment_data())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Treatment.objects.count(), 0)

    # 4. Success: vet adds a treatment, vet comes from the token
    def test_vet_adds_treatment(self):
        self.login_as(self.vet)
        response = self.client.post('/api/treatments/', self.treatment_data())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Treatment.objects.get().vet_id, self.vet.id)

    # 5. Bad input: vet forgets the drug
    def test_vet_bad_input_returns_400(self):
        self.login_as(self.vet)
        data = self.treatment_data()
        del data['drug']
        response = self.client.post('/api/treatments/', data)
        self.assertEqual(response.status_code, 400)

    # 6. Missing record
    def test_missing_animal_returns_404(self):
        self.login_as(self.vet)
        response = self.client.get('/api/animals/999/')
        self.assertEqual(response.status_code, 404)

    # 7. No token
    def test_no_token_returns_401(self):
        response = self.client.get('/api/animals/')
        self.assertEqual(response.status_code, 401)

    # 8. A farmer sees only their own animals
    def test_farmer_sees_only_own_animals(self):
        other = Profile.objects.create(
            id=uuid.uuid4(), full_name='Other', role='farmer')
        Animal.objects.create(
            ear_tag='RW-099', species='pig',
            birth_date='2024-01-01', owner=other)
        self.login_as(self.farmer)
        response = self.client.get('/api/animals/')
        self.assertEqual(response.status_code, 200)
        tags = [a['ear_tag'] for a in response.data['results']]
        self.assertEqual(tags, ['RW-001'])
