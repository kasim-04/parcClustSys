import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

from .models import Parcel, ParcelBatch, Delivery
from .forms import ParcelForm, DeliveryForm
from .ml import FeatureClusterLimit, ClusterLimits, BestClusteringModel


@login_required
def parcels_view(request):
    parcels = Parcel.objects.filter(is_distributed=False, user=request.user)
    context = {
        'parcels': parcels,
    }

    return render(request, 'main/parcels.html', context)


@login_required
def add_parcel_view(request):
    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.number = datetime.now().strftime('%Y%m%d%H%M%S')
            parcel.user = request.user
            parcel.save()
            return redirect('parcels')
        else:
            messages.error(request, "Ошибка. Пожалуйста, проверьте введенные данные.")
    else:
        form = ParcelForm()

    return render(request, 'main/add_parcel.html', {'form': form})


@login_required
def add_delivery_view(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            # получение данных из формы
            max_k = form.cleaned_data['max_k']
            max_cluster_size = form.cleaned_data['max_cluster_size']
            max_cluster_weight = form.cleaned_data['max_cluster_weight']
            max_cluster_volume = form.cleaned_data['max_cluster_volume']

            # получение данных из БД
            parcels = Parcel.objects.filter(is_distributed=False)
            df = pd.DataFrame(list(parcels.values()))
            if len(df) < 2:
                error_message = "В систему должно быть добавлено минимум 2 посылки"
                form = DeliveryForm()
                context = {
                    'form': form,
                    'error_message': error_message,
                }
                return render(request, 'main/add_delivery.html', context)

            # предварительная обработка данных
            locations = df[['latitude', 'longitude']].to_numpy()
            scaler = MinMaxScaler()
            scaled_locations = scaler.fit_transform(locations)
            weights = df['weight'].to_numpy()
            volumes = (df['width'] * df['length'] * df['height']).to_numpy()

            # подбор модели
            limits = ClusterLimits(
                limits=[
                    FeatureClusterLimit(X=weights, limit_value=max_cluster_weight),
                    FeatureClusterLimit(X=volumes, limit_value=max_cluster_volume)
                ],
                size_limit=max_cluster_size
            )
            best_k = None
            for k in range(2, max_k + 1):
                model = BestClusteringModel(n_clusters=k)
                labels = model.best_fit_predict(X=scaled_locations, limits=limits)
                if labels is not None:
                    best_k = k
                    break

            if best_k is None:
                error_message = "При заданных параметрах не удалось распределить посылки"
                form = DeliveryForm()
                context = {
                    'form': form,
                    'error_message': error_message,
                }
                return render(request, 'main/add_delivery.html', context)

            # транзакция
            with transaction.atomic():
                # 1. Сделать запись в таблицу ParcelBatch
                parcel_batch = ParcelBatch.objects.create(
                    number=datetime.now().strftime('%Y%m%d%H%M%S'),
                    user=request.user,  # Передаем объект User
                    k=best_k,
                    max_cluster_size=max_cluster_size,
                    weight=max_cluster_weight,
                    volume=max_cluster_volume
                )

                # 3. Создать записи в таблице Delivery
                deliveries = []
                for parcel_id, group in zip(df['id'], labels):
                    parcel = Parcel.objects.get(id=parcel_id)
                    delivery = Delivery(
                        parcel_batch=parcel_batch,  # Передаем объект ParcelBatch
                        parcel=parcel,
                        group=group
                    )
                    deliveries.append(delivery)

                # Сохранить все записи в таблице Delivery
                Delivery.objects.bulk_create(deliveries)

                # 4. Обновить статус посылок на is_distributed = True
                parcel_ids = df['id'].tolist()
                Parcel.objects.filter(id__in=parcel_ids).update(is_distributed=True)

            return redirect('report', batch_number=parcel_batch.number)
        else:
            messages.error(request, "Ошибка. Пожалуйста, проверьте введенные данные.")
    else:
        form = DeliveryForm()

    return render(request, 'main/add_delivery.html', {'form': form})


@login_required
def reports_view(request):
    parcel_batches = ParcelBatch.objects.filter(user=request.user)
    context = {
        'parcel_batches': parcel_batches,
    }

    return render(request, 'main/reports.html', context)


@login_required
def report_view(request, batch_number):
    parcel_batch = get_object_or_404(ParcelBatch, number=batch_number)
    groups = parcel_batch.delivery_set.all().values_list('group', flat=True).distinct()
    deliveries_by_group = {group: parcel_batch.delivery_set.filter(group=group) for group in groups}
    context = {
        'parcel_batch': parcel_batch,
        'deliveries_by_group': deliveries_by_group,
    }
    return render(request, 'main/report.html', context)
