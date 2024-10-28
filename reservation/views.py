from collections.abc import Sequence
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from reservation.forms import ReservationForm
from reservation.models import Disponibilite, Reservation, Ressource
from django.utils import timezone

# Create your views here.
class IndexView(TemplateView):
    template_name = 'reservation/index.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['is_active'] = 'index'
        context['ressources'] = Ressource.objects.all().count()
        context['reservations'] = Reservation.objects.all().count()
        return context


class RessourceListView(ListView):
    model = Ressource
    template_name = 'reservation/ressources.html'
    context_object_name = 'ressources'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['is_active'] = 'reservation'
        return context
    
    def get_ordering(self) -> Sequence[str]:
        return '-available'
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = Ressource.objects.all().prefetch_related('condition', 'equipement')
        search_ressource = self.request.GET.get('search_ressource', '')
        available = self.request.GET.get('available')

        if search_ressource:
            queryset = queryset.filter(name__icontains=search_ressource)
        
        if available:
            queryset = queryset.filter(available=True)
        
        return queryset
    
       


class DetailRessourcView(DetailView):
    model = Ressource
    template_name = 'reservation/detail_ressource.html'
    context_object_name = 'ressource'
    pk_url_kwarg = 'uid'

    def get_object(self):
        return Ressource.objects.select_related('user').prefetch_related('reservation_ressource', 'condition', 'equipement').get(
            uid=self.kwargs.get('uid')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        context['form'] = ReservationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ReservationForm(request.POST)
        disponibilite_id = request.POST.get('disponibilite_id')
        disponibilite = get_object_or_404(Disponibilite, id=disponibilite_id)
        self.object = self.get_object()  

        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.ressource = self.object
            reservation.start_time = form.cleaned_data['start_time']
            reservation.end_time = form.cleaned_data['end_time']

            if reservation.start_time >= disponibilite.start_date and reservation.end_time <= disponibilite.end_date:
                reservation.save()
                messages.success(request, "Votre réservation a été effectuée avec succès.")
            else:
                messages.error(request, "Les dates ne sont pas dans la plage de disponibilité.")
            return redirect('detail_reservation', uid=self.object.uid)
        else:
            messages.error(request, "Échec lors de la réservation.")
            print(form.errors)
            return redirect('detail_reservation', uid=self.object.uid)

class ContactView(TemplateView):
    template_name = 'reservation/contact.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['is_active'] = 'contact'
        return context


class ReservationListView(ListView):
    template_name = 'reservation/mesreservation.html'
    context_object_name = 'reservations'
    model = Reservation

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        user = self.request.user
        queryset = Reservation.objects.filter(user = user).select_related('ressource')

        statut_filter = self.request.GET.get('status_trie')
    
        if statut_filter == 'confirme':
            queryset = queryset.filter(status='Confirmé')
        elif statut_filter == 'attente':
            queryset = queryset.filter(status='En attente')
        elif statut_filter == 'annule':
            queryset = queryset.filter(status='Annulé')
       
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['is_active'] = 'mesreservation'
        context['now'] = timezone.now()
        context['status_trie'] = self.request.GET.get('statut_trie')
        return context

def update_reservation(request, *args, **kwargs):
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if reservation_id and start_time and end_time:
            reservation = get_object_or_404(Reservation, id=reservation_id)
            
            disponibilites = reservation.ressource.disponibilite.filter(
                start_date__lte=start_time, end_date__gte=end_time
            )
            
            if not disponibilites.exists():
                messages.error(request, "Les nouvelles dates ne sont pas disponibles.")
                return redirect('mesreservations')
            
            reservation.start_time = start_time
            reservation.end_time = end_time
            reservation.save()
            
            messages.success(request, "Votre modification a été effectuée avec succès.")
            return redirect('mesreservations')
        else:
            messages.error(request, "Veuillez fournir toutes les informations requises.")
            return redirect('mesreservations')
    return redirect('mesreservations')

def cancelReservation(request, uid):
    reservation = get_object_or_404(Reservation, uid=uid)
    reservation.status = 'Annulé'
    reservation.save()
    messages.success(request, "Votre reservation a ete annuler avec success")
    return redirect('mesreservations')


    