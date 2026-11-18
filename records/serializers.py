from rest_framework import serializers
from .models import Animal, Treatment


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'ear_tag', 'species', 'birth_date', 'owner']
        extra_kwargs = {'owner': {'required': False}}


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['id', 'animal', 'drug', 'treat_date', 'vet']
        read_only_fields = ['vet']