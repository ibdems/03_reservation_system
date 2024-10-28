from typing import Any
from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpRequest
from .models import Disponibilite, Equipement, Reservation, Ressource, Condition
# Register your models here.
@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display =  ['name', 'user', 'description', 'capacity', 'available']
    exclude = ['uid', 'user', 'created_at']

    def save_model(self, request: HttpRequest, obj, form: ModelForm, change: bool) -> None:
        obj.user = request.user
        return super().save_model(request, obj, form, change)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj and obj.user != request.user or request.user.is_superuser == False:
            return False
        return super().has_view_permission(request, obj)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['ressource', 'user','start_time', 'end_time', 'status']
    exclude = ['uid', 'user', 'created_at']

    def save_model(self, request: HttpRequest, obj, form: ModelForm, change: bool) -> None:
        obj.user = request.user
        return super().save_model(request, obj, form, change)

@admin.register(Disponibilite)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ['ressource', 'start_date', 'end_date']
    exclude = ['uid']

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        query = super().get_queryset(request)
        if request.user.is_superuser:
            return query
        return query.filter(ressource__user=request.user)
    
    def save_model(self, request: HttpRequest, obj: Any, form: ModelForm, change: bool) -> None:
        obj.clean()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ressource' and not request.user.is_superuser:
            kwargs['queryset'] = Ressource.objects.filter(user=request.user)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ['name', 'ressource']
    fields = ['ressource', 'name']

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['name', 'ressource']
    fields = ['ressource', 'name']


