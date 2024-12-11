from django import forms
from .models import Parcel


class ParcelForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ['address', 'latitude', 'longitude', 'weight', 'width', 'length', 'height']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['latitude'].min_value = -90
        self.fields['latitude'].max_value = 90
        self.fields['longitude'].min_value = -180
        self.fields['longitude'].max_value = 180
        self.fields['weight'].min_value = 0.01
        self.fields['width'].min_value = 0.01
        self.fields['length'].min_value = 0.01
        self.fields['height'].min_value = 0.01


class DeliveryForm(forms.Form):
    max_k = forms.IntegerField(label='Максимальное количество курьеров', min_value=1)
    max_cluster_size = forms.IntegerField(label='Максимальный кол-во посылок в группе', min_value=1)
    max_cluster_weight = forms.DecimalField(label='Грузоподъемность транспорта (кг)', min_value=0.01)
    max_cluster_volume = forms.DecimalField(label='Вместимость транспорта (м^3)', min_value=0.01)
