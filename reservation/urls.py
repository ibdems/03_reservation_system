from django.urls import path, include
from .views import *
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('ressources/', RessourceListView.as_view(), name='ressource'),
    path('detail_reservation/<uid>/', DetailRessourcView.as_view(), name='detail_reservation'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('mesreservations/', ReservationListView.as_view(), name='mesreservations'),
    path('cancelReservation/<uid>/', cancelReservation, name='cancelReservation'),
    path('updateReservation/', update_reservation, name='update_reservation')
]
