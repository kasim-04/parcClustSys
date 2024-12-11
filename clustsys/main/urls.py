from django.urls import path
from .views import parcels_view, add_parcel_view, add_delivery_view, reports_view, report_view

urlpatterns = [
    path('', parcels_view, name='parcels'),
    path('add_parcel/', add_parcel_view, name='add_parcel'),
    path('add_delivery/', add_delivery_view, name='add_delivery'),
    path('reports/', reports_view, name='reports'),
    path('report/<str:batch_number>/', report_view, name='report'),
]