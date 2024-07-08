
from django.urls import path, include

from .views import *
from . import views


urlpatterns = [
    path('contact-fsf/', ContactFormApiView.as_view(), name='cont_form_data'),
    path('event-fst/', EventApiView.as_view(), name='cont_form_data'),
    path('client-data/', ClientApiView.as_view(), name='client_data_list'),
    path('client-data/<slug:slug>/', ClientApiView.as_view(), name='client_data_detail'),

]