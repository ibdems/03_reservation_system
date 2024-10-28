from typing import Iterable
from django.db import models
from django.utils import timezone
from django.forms import ValidationError
import uuid


# Create your models here.

class Ressource(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=200)
    user = models.ForeignKey('users.user', on_delete=models.CASCADE, related_name='ressource')
    description = models.TextField()
    capacity = models.IntegerField()
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='image/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    adresse = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name




class Disponibilite(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    ressource = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='disponibilite')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reserved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Disponibilte de {self.ressource.name} de {self.start_date} a {self.end_date}"
    
    def clean(self) -> None:
        if self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'La date de fin ne doit pas etre superieur a la date de fin'})
        return super().clean()

class Reservation(models.Model):
    status_reservation = {
        'Confirmé' : 'Confirmé',
        'En attente' : 'En attente',
        'Annulé' : 'Annulé',
        'Terminé' : 'Terminé'
    }
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reservation_user')
    ressource = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='reservation_ressource')
    start_time = models.DateTimeField(verbose_name='Date de debut')
    end_time = models.DateTimeField(verbose_name='Date de Fin')
    status = models.CharField(max_length=15, choices=status_reservation, default='En attente')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return f"Reservation de {self.user.first_name} pour {self.ressource.name}"
    
    def clean(self) -> None:
        if self.start_time >= self.end_time:
            raise ValidationError({'start_time': 'La date de debut doit etre inferieur a la date de fin'})
        return super().clean()
    
    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        if self.end_time > timezone.now():
            self.status = 'Terminé'
        return super().save(force_insert, force_update, using, update_fields)
    
class Condition(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=255)
    ressource = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='condition')

class Equipement(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True)
    name= models.CharField(max_length=255, unique=True)
    ressource = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='equipement')
