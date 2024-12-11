from django.contrib import admin
from .models import Parcel, ParcelBatch, Delivery

admin.site.register(Parcel)
admin.site.register(ParcelBatch)
admin.site.register(Delivery)
