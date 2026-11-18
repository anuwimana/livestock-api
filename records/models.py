from django.db import models


class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    full_name = models.TextField()
    role = models.TextField()

    class Meta:
        managed = False
        db_table = 'profiles'


class Animal(models.Model):
    id = models.BigAutoField(primary_key=True)
    ear_tag = models.TextField(unique=True)
    species = models.TextField()
    birth_date = models.DateField()
    owner = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING,
        db_column='owner_id', related_name='animals')

    class Meta:
        managed = False
        db_table = 'animals'


class Treatment(models.Model):
    id = models.BigAutoField(primary_key=True)
    animal = models.ForeignKey(
        Animal, on_delete=models.DO_NOTHING,
        db_column='animal_id', related_name='treatments')
    drug = models.TextField()
    treat_date = models.DateField()
    vet = models.ForeignKey(
        Profile, on_delete=models.DO_NOTHING,
        db_column='vet_id', related_name='given_treatments')

    class Meta:
        managed = False
        db_table = 'treatments'
