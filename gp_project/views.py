from django.shortcuts import render
from .forms import PredictForm
import os

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier


def index(request):
    ### Veri Yükleme
    csv_measurements = os.path.join( os.getcwd(),'datasets','measurements.csv')
    df_measurements = pd.read_csv(csv_measurements, parse_dates=['measurement_time'])
    df_measurements = df_measurements.sort_values(by=['measurement_time'], ascending=[True])

    csv_failures = os.path.join( os.getcwd(),'datasets','failures.csv')
    df_failures = pd.read_csv(csv_failures, parse_dates=['failure_time'])
    df_failures = df_failures.sort_values(by=['failure_time'], ascending=[True])

    ### Veri Birleştirme
    df_combined = pd.merge_asof(
        df_measurements,
        df_failures,
        left_on='measurement_time',
        right_on='failure_time',
        by='gadget_id',
        direction='forward',
    )

    ### Sütun Ekleme
    df_combined['time_to_fail'] = df_combined['failure_time'] - df_combined['measurement_time']
    df_combined['fail_in_1h'] = np.where(df_combined['time_to_fail'] < pd.Timedelta(hours=1), 1, 0)

    ### Ölçüleri Düzenleme
    df_combined = df_combined.reset_index(drop=True)
    df_combined = df_combined.sort_values(by=['gadget_id', 'measurement_time'], ascending=[True, True])

    df_combined['temperature_6h_std'] = df_combined.groupby('gadget_id')['temperature'].rolling(6).std(
        ddof=0).reset_index(drop=True)
    df_combined['pressure_6h_mean'] = df_combined.groupby('gadget_id')['pressure'].rolling(6).mean().reset_index(
        drop=True)

    ### Eğitim ve Test Kümesi Oluşturma
    X = ['vibration_y', 'pressure_6h_mean', 'temperature_6h_std']
    y = 'fail_in_1h'
    cols = X + [y]

    df_to_split = df_combined.copy()
    df_to_split = df_to_split.dropna(subset=cols)
    df_to_split = df_to_split.drop(['Unnamed: 10', 'Unnamed: 11'], axis=1)
    df_to_split = df_to_split.reset_index(drop=True)

    df_train = df_to_split[df_to_split['gadget_id'].isin([1, 2, 3, 4,5,6])].reset_index(drop=True).copy()


    """print(f"Training data: {df_train.shape}")
    print(f"Test data: {df_test.shape}")"""

    ### Tahmin parametreleri
    w0 = 1
    w1 = 33

    ### Random Forest
    random_forest = RandomForestClassifier(
        min_samples_leaf=7,
        random_state=45,
        n_estimators=50,
        class_weight={0: w0, 1: w1}
    )
    random_forest.fit(df_train[X], df_train[y])
    """
    df_test['random_forest'] = random_forest.predict(df_test[X])
    cm = confusion_matrix(df_test['fail_in_1h'], df_test['random_forest'])

    print("------------------------------")
    print("Random Forest:")
    print(classification_report(df_test['fail_in_1h'], df_test['random_forest']))
    print("CM:\n ", cm)
    """
    """temp
    temp2 = 0
    temp3 = 0"""
    context = {}
    if request.method == "POST":
        form = PredictForm(request.POST)
        if form.is_valid():
            vibration = form.cleaned_data.get("vibration_y")
            pressure = form.cleaned_data.get("pressure_6h_mean")
            temperature = form.cleaned_data.get("temperature_6h_std")
            predict = random_forest.predict([[vibration, pressure, temperature]])
            if predict == 1:
                message = 'Your machine may break in 1 hour. You must maintain your machine immediately!'
            else:
                message = 'Your machine may \"not\" break within 1 hour. But still, be careful.'

            context = {
                'form': form,
                'message': message,
                'predict' : predict
            }
    else:
        form = PredictForm()
    context['form'] = form



    return render(request,'index.html',context)

def about(request):
    return render(request,"about.html")

