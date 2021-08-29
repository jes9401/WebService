from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
# from .forms import AudioForm
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
import time
import datetime
import json
import os
import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
import io
import pymongo, gridfs
from bson import ObjectId
from keras.models import model_from_json
from scipy import fftpack
from numpy.fft import *
from sklearn.preprocessing import StandardScaler
from dateutil.parser import parse
import matplotlib.pylab as plt
from io import StringIO,BytesIO
from PIL import Image
import random
from django.core import serializers
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)



def br_home(request):
    return render(request, 'br/home.html',{'title': 'home'})

def test(request):
    start_time = datetime.datetime.now()
    t = chek()
    t.start_date = start_time
    t.end_date = start_time + datetime.timedelta(minutes=1)
    t.save()
    return JsonResponse(start_time, safe=False, json_dumps_params={'ensure_ascii': False}) # json으로 응답


@csrf_exempt
def exercise1(request):
    if request.method == 'POST':
        time_now = datetime.datetime.now()
        end_time = time_now
        csv_time = time_now - datetime.timedelta(minutes=1)
        start_time = end_time - datetime.timedelta(minutes=1)


        # 실시간 데이터일 경우
        # while True:
        #     try:
        #         print(count,"번째")
        #         count+=1
        #         client = MongoClient('23.96.118.170', 27017)
        #         db = client['test']
        #         collection = db['result']

        #         start = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        #         end = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        #         res = collection.find({'Time':{'$gt':start,'$lt':end}})
        #         test_data = pd.DataFrame(res)
        #         if len(test_data) == 0:
        #             continue

        #         else:
        #             time_list = list(test_data['Time'])
        #             start_temp = datetime.datetime.strptime(time_list[0], '%Y-%m-%dT%H:%M:%S.%fZ') - datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
        #             end_temp = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ') - datetime.datetime.strptime(time_list[-1], '%Y-%m-%dT%H:%M:%S.%fZ')
        #             if start_temp >5 or end_time>5:
        #                 continue
        #             else:
        #                 id_temp = 0
        #                 time_temp = 0
        #                 test_data = test_data.iloc[:len(test_data)-(len(test_data)%50),:]
        #                 id_list = list(test_data['id'])
        #                 time_list = list(test_data['Time'])

        #                 count = 0
        #                 n = 0
        #                 for i in range(len(id_list)):
        #                     time_list[i] = count
        #                     if count == 49:
        #                         id_list[i] = n
        #                         n+=1
        #                         count=0
        #                     else:
        #                         id_list[i] =n
        #                         count+=1

        #                 test_data['id'] = id_list
        #                 test_data['Time'] = time_list
        #                 id_unique = list(test_data['id'].unique())
        #                 break
        #     except Exception as e:
        #         print(e)


        # 비실시간, 테스트용으로 넣어둔 코드
        test_data = pd.read_csv('/home/jes9401/Web/myweb/br/test.csv')
        id_temp = 0
        time_temp = 0
        test_data = test_data.iloc[:len(test_data)-(len(test_data)%50),:]

        id_list = list(test_data['id'])
        time_list = list(test_data['Time'])

        count = 0
        n = 0
        for i in range(len(id_list)):
            time_list[i] = count
            if count == 49:
                id_list[i] = n
                n+=1
                count=0
            else:
                id_list[i] =n
                count+=1

        test_data['id'] = id_list
        test_data['Time'] = time_list
        id_unique = list(test_data['id'].unique())
        # 여기까지


        dt=0.02
        def jerk_signal(signal):
                return np.array([(signal[i+1]-signal[i])/dt for i in range(len(signal)-1)])
        test_dt=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for v in test_data.columns[98:]:
                values=jerk_signal(temp[v].values)
                values=np.insert(values,0,0)
                temp.loc[:,v+'_dt']=values
            test_dt.append(temp)
        test_data=pd.concat(test_dt)



        def fourier_transform_one_signal(t_signal):
            complex_f_signal= fftpack.fft(t_signal)
            amplitude_f_signal=np.abs(complex_f_signal)
            return amplitude_f_signal
        fft_t=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for i in test_data.columns[98:]:
                temp[i]=fourier_transform_one_signal(temp[i].values)
            fft_t.append(temp)
        test_data=pd.concat(fft_t)
        scaler = StandardScaler()
        test_data.iloc[:,98:] = scaler.fit_transform(test_data.iloc[:,98:])
        test_data = test_data.iloc[:,2:]
        test_x = np.array(test_data).reshape(-1,50,108)

        result = {}

        # 모델 객체 생성
        t = TwoHand0()
        t.username = request.user.username
        t.start_time = start_time
        t.end_time = end_time


        ## model 1##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_A/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_A/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        # submission= pd.read_csv('/home/jes9401/Web/myweb/br/predModel/test_submission.csv')
        # submission.iloc[:,1:]= pred
        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred

        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.a_motion = 'a_standard'
        elif max(v1,v2,v3) == v2:
            t.a_motion = 'a_fake1'
        else:
            t.a_motion = 'a_fake2'
        t.a_value = max(v1,v2,v3)
        ######################################################

        ## model 2##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_V/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_V/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        # submission= pd.read_csv('/home/jes9401/Web/myweb/br/predModel/test_submission.csv')
        # submission.iloc[:,1:]= pred
        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{csv_time}.csv',index=False)


        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.v_motion = 'v_standard'
        elif max(v1,v2,v3) == v2:
            t.v_motion = 'v_fake1'
        else:
            t.v_motion = 'v_fake2'
        t.v_value = max(v1,v2,v3)
        ######################################################


        ## model 3##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_R/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv0_R/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        # submission= pd.read_csv('/home/jes9401/Web/myweb/br/predModel/test_submission.csv')
        # submission.iloc[:,1:]= pred
        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100

        if max(v1,v2,v3) == v1:
            t.r_motion = 'r_standard'
        elif max(v1,v2,v3) == v2:
            t.r_motion = 'r_fake1'
        else:
            t.r_motion = 'r_fake2'
        t.r_value = max(v1,v2,v3)
        ######################################################


        if t.a_value>=90 and t.v_value>=90 and t.r_value>=90:
            m = mlops()
            m.time = start_time
            m.a_motion = t.a_motion
            m.v_motion = t.v_motion
            m.r_motion = t.r_motion
            m.exercise = "TwoHand0"
            m.save()

        t.temp = 1
        t.save()




        context={'msg':'start'}
        # return JsonResponse(post_data, safe=False, json_dumps_params={'ensure_ascii': False}) # json으로 응답
        return JsonResponse(context)
    else:
        return render(request, 'br/exercise1.html',{'title': 'exercise'})


@csrf_exempt
def exercise2(request):
    if request.method == 'POST':
        time_now = datetime.datetime.now()
        end_time = time_now
        csv_time = time_now - datetime.timedelta(minutes=1)
        start_time = end_time - datetime.timedelta(minutes=1)

        test_data = pd.read_csv('/home/jes9401/Web/myweb/br/test.csv')
        id_temp = 0
        time_temp = 0
        test_data = test_data.iloc[:len(test_data)-(len(test_data)%50),:]

        id_list = list(test_data['id'])
        time_list = list(test_data['Time'])

        count = 0
        n = 0
        for i in range(len(id_list)):
            time_list[i] = count
            if count == 49:
                id_list[i] = n
                n+=1
                count=0
            else:
                id_list[i] =n
                count+=1

        test_data['id'] = id_list
        test_data['Time'] = time_list
        id_unique = list(test_data['id'].unique())

        dt=0.02
        def jerk_signal(signal):
                return np.array([(signal[i+1]-signal[i])/dt for i in range(len(signal)-1)])
        test_dt=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for v in test_data.columns[98:]:
                values=jerk_signal(temp[v].values)
                values=np.insert(values,0,0)
                temp.loc[:,v+'_dt']=values
            test_dt.append(temp)
        test_data=pd.concat(test_dt)



        def fourier_transform_one_signal(t_signal):
            complex_f_signal= fftpack.fft(t_signal)
            amplitude_f_signal=np.abs(complex_f_signal)
            return amplitude_f_signal
        fft_t=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for i in test_data.columns[98:]:
                temp[i]=fourier_transform_one_signal(temp[i].values)
            fft_t.append(temp)
        test_data=pd.concat(fft_t)
        scaler = StandardScaler()
        test_data.iloc[:,98:] = scaler.fit_transform(test_data.iloc[:,98:])
        test_data = test_data.iloc[:,2:]
        test_x = np.array(test_data).reshape(-1,50,108)

        result = {}

        # 모델 객체 생성
        t = TwoHand1()
        t.username = request.user.username
        t.start_time = start_time
        t.end_time = end_time


        ## model 1##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_A/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_A/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred

        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.a_motion = 'a_standard'
        elif max(v1,v2,v3) == v2:
            t.a_motion = 'a_fake1'
        else:
            t.a_motion = 'a_fake2'
        t.a_value = max(v1,v2,v3)
        ######################################################

        ## model 2##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_V/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_V/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{csv_time}.csv',index=False)


        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.v_motion = 'v_standard'
        elif max(v1,v2,v3) == v2:
            t.v_motion = 'v_fake1'
        else:
            t.v_motion = 'v_fake2'
        t.v_value = max(v1,v2,v3)
        ######################################################


        ## model 3##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_R/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv1_R/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100

        if max(v1,v2,v3) == v1:
            t.r_motion = 'r_standard'
        elif max(v1,v2,v3) == v2:
            t.r_motion = 'r_fake1'
        else:
            t.r_motion = 'r_fake2'
        t.r_value = max(v1,v2,v3)
        ######################################################

        if t.a_value>=88 and t.v_value>=88 and t.r_value>=88:
            m = mlops()
            m.start_time = start_time
            m.a_motion = t.a_motion
            m.v_motion = t.v_motion
            m.r_motion = t.r_motion
            m.exercise = "TwoHand1"
            m.save()

        t.temp = 1
        t.save()


        context={'msg':'start'}

        return JsonResponse(context)
    else:
        return render(request, 'br/exercise2.html',{'title': 'exercise'})


@csrf_exempt
def exercise3(request):
    if request.method == 'POST':
        time_now = datetime.datetime.now()
        end_time = time_now
        csv_time = time_now - datetime.timedelta(minutes=1)
        start_time = end_time - datetime.timedelta(minutes=1)


        test_data = pd.read_csv('/home/jes9401/Web/myweb/br/test.csv')
        id_temp = 0
        time_temp = 0
        test_data = test_data.iloc[:len(test_data)-(len(test_data)%50),:]

        id_list = list(test_data['id'])
        time_list = list(test_data['Time'])

        count = 0
        n = 0
        for i in range(len(id_list)):
            time_list[i] = count
            if count == 49:
                id_list[i] = n
                n+=1
                count=0
            else:
                id_list[i] =n
                count+=1

        test_data['id'] = id_list
        test_data['Time'] = time_list
        id_unique = list(test_data['id'].unique())

        dt=0.02
        def jerk_signal(signal):
                return np.array([(signal[i+1]-signal[i])/dt for i in range(len(signal)-1)])
        test_dt=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for v in test_data.columns[98:]:
                values=jerk_signal(temp[v].values)
                values=np.insert(values,0,0)
                temp.loc[:,v+'_dt']=values
            test_dt.append(temp)
        test_data=pd.concat(test_dt)



        def fourier_transform_one_signal(t_signal):
            complex_f_signal= fftpack.fft(t_signal)
            amplitude_f_signal=np.abs(complex_f_signal)
            return amplitude_f_signal
        fft_t=[]
        for i in test_data['id'].unique():
            temp=test_data.loc[test_data['id']==i]
            for i in test_data.columns[98:]:
                temp[i]=fourier_transform_one_signal(temp[i].values)
            fft_t.append(temp)
        test_data=pd.concat(fft_t)
        scaler = StandardScaler()
        test_data.iloc[:,98:] = scaler.fit_transform(test_data.iloc[:,98:])
        test_data = test_data.iloc[:,2:]
        test_x = np.array(test_data).reshape(-1,50,108)

        result = {}

        # 모델 객체 생성
        t = TwoHand2()
        t.username = request.user.username
        t.start_time = start_time
        t.end_time = end_time


        ## model 1##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_A/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_A/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred

        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.a_motion = 'a_standard'
        elif max(v1,v2,v3) == v2:
            t.a_motion = 'a_fake1'
        else:
            t.a_motion = 'a_fake2'
        t.a_value = max(v1,v2,v3)
        ######################################################

        ## model 2##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_V/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_V/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{csv_time}.csv',index=False)


        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100
        if max(v1,v2,v3) == v1:
            t.v_motion = 'v_standard'
        elif max(v1,v2,v3) == v2:
            t.v_motion = 'v_fake1'
        else:
            t.v_motion = 'v_fake2'
        t.v_value = max(v1,v2,v3)
        ######################################################


        ## model 3##############################################
        preds = []
        for i in range(5):
            json_file = open(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_R/classification_model{i+1}.json', "r")
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            loaded_model.load_weights(f'/home/jes9401/Web/myweb/br/predModel/twohand_lv2_R/classification_model{i+1}.h5')
            loaded_model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
            pred = loaded_model.predict(test_x)
            preds.append(pred)
        pred = np.mean(preds, axis=0)

        submission = pd.DataFrame(columns=['id','standard','fake1','fake2'])
        for i in range(len(id_unique)):
            submission.loc[i] = [id_unique[i],0,0,0]
        submission.iloc[:,1:] = pred
        submission.to_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{csv_time}.csv',index=False)

        v1 = sum(list(submission['standard'])) /len(list(submission['standard']))
        v2 = sum(list(submission['fake1'])) /len(list(submission['fake1']))
        v3 = sum(list(submission['fake2'])) /len(list(submission['fake2']))
        v1 = round(v1, 2) * 100
        v2 = round(v2, 2) * 100
        v3 = round(v3, 2) * 100

        if max(v1,v2,v3) == v1:
            t.r_motion = 'r_standard'
        elif max(v1,v2,v3) == v2:
            t.r_motion = 'r_fake1'
        else:
            t.r_motion = 'r_fake2'
        t.r_value = max(v1,v2,v3)
        ######################################################

        if t.a_value>=90 and t.v_value>=90 and t.r_value>=90:
            m = mlops()
            m.time = start_time
            m.a_motion = t.a_motion
            m.v_motion = t.v_motion
            m.r_motion = t.r_motion
            m.exercise = "TwoHand2"
            m.save()

        t.temp = 1
        t.save()


        context={'msg':'start'}

        return JsonResponse(context)
    else:
        return render(request, 'br/exercise3.html',{'title': 'exercise'})


def dashboard(request):
    if request.method == 'GET':
        user = request.user.username
        t0 = TwoHand0.objects.filter(username=user).order_by('start_time')
        t1 = TwoHand1.objects.filter(username=user).order_by('start_time')
        t2 = TwoHand2.objects.filter(username=user).order_by('start_time')

        t0_len = len(t0)
        t1_len = len(t1)
        t2_len = len(t2)

        return render(request, 'br/dashboard.html',{'title':'dashboard','t0':t0,'t1':t1,'t2':t2,'t0_exercise':'양 팔 옆으로 밀기',
        't1_exercise':'양 팔 위로 밀기','t2_exercise':'양 팔 앞으로 밀기',
        't0_len':t0_len,'t1_len':t1_len,'t2_len':t2_len})
    else:
        context={'msg':'start'}
        return JsonResponse(context)

@csrf_exempt
def temp(request):
    if request.method == 'GET':
        t0 = TwoHand0.objects.filter(username=request.user.username).order_by('start_time').last()
        t1 = TwoHand1.objects.filter(username=request.user.username).order_by('start_time').last()
        t2 = TwoHand2.objects.filter(username=request.user.username).order_by('start_time').last()

        t0_time = t0.start_time
        t1_time = t1.start_time
        t2_time = t2.start_time
        time_temp = max(t0_time,t1_time,t2_time)
        if time_temp == t0_time:
            c_time = str(t0_time)
            exercise = '양 팔 옆으로 밀기'
            df_a = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{c_time}.csv')
            df_v = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{c_time}.csv')
            df_r = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{c_time}.csv')
        elif time_temp == t1_time:
            c_time = str(t1_time)
            exercise = '양 팔 위로 밀기'
            df_a = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{c_time}.csv')
            df_v = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{c_time}.csv')
            df_r = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{c_time}.csv')
        else:
            c_time = str(t2_time)
            exercise = '양 팔 앞으로 밀기'
            df_a = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{c_time}.csv')
            df_v = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{c_time}.csv')
            df_r = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{c_time}.csv')

        a_standard = sum(list(df_a['standard'])) /len(list(df_a['standard']))
        a_standard = int(round(a_standard, 2) * 100)
        a_fake1 = sum(list(df_a['fake1'])) /len(list(df_a['fake1']))
        a_fake1 = int(round(a_fake1,2)*100)
        a_fake2 = sum(list(df_a['fake2'])) /len(list(df_a['fake2']))
        a_fake2 = int(round(a_fake2,2)*100)

        v_standard = sum(list(df_v['standard'])) /len(list(df_v['standard']))
        v_standard = int(round(v_standard, 2) * 100)
        v_fake1 = sum(list(df_v['fake1'])) /len(list(df_v['fake1']))
        v_fake1 = int(round(v_fake1,2)*100)
        v_fake2 = sum(list(df_v['fake2'])) /len(list(df_v['fake2']))
        v_fake2 = int(round(v_fake2,2)*100)

        r_standard = sum(list(df_r['standard'])) /len(list(df_r['standard']))
        r_standard = int(round(r_standard, 2) * 100)
        r_fake1 = sum(list(df_r['fake1'])) /len(list(df_r['fake1']))
        r_fake1 = int(round(r_fake1,2)*100)
        r_fake2 = sum(list(df_r['fake2'])) /len(list(df_r['fake2']))
        r_fake2 = int(round(r_fake2,2)*100)

        if a_standard>=80:
            a_color ='green'
        elif a_standard>=40:
            a_color = 'yellow'
        else:
            a_color = 'red'

        if v_standard>=80:
            v_color ='green'
        elif v_standard>=40:
            v_color = 'yellow'
        else:
            v_color = 'red'

        if r_standard>=80:
            r_color ='green'
        elif r_standard>=40:
            r_color = 'yellow'
        else:
            r_color = 'red'

        color_list =[a_color,v_color,r_color]
        g_count = 0
        y_count = 0
        r_count = 0
        for c in color_list:
            if c =="green":
                g_count+=1
            elif c == "yellow":
                y_count+=1
            elif c == "red":
                r_count+=1



        a_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 팔이\n살짝 내려갔어요", "잘하셨지만 팔을\n조금 더 올려주세요",
                  "잘하셨는데 팔이\n많이 내려갔어요", "잘하셨지만 팔을\n확실하게 올려주세요",
                 "팔이 살짝\n내려갔어요","팔을 살짝\n올려주세요",
                  "팔이 많이\n내려갔어요","팔을 확실하게\n올려주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        v_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 속도가\n조금 느렸어요", "잘하셨지만 조금만\n더 빠르게 움직여주세요",
                  "잘하셨는데 속도가\n많이 느렸어요", "잘하셨지만 더\n빠르게 움직여주세요",
                 "속도가 조금 느렸어요","조금만 더 빠르게\n움직여주세요",
                  "속도가 많이\n느렸어요","더 빠르게\n움직여주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        r_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 팔이\n살짝 굽혀졌네요", "잘하셨지만 팔을\n조금만 더 뻗어주세요",
                  "잘하셨는데 팔이\n많이 굽혀졌어요", "잘하셨지만 팔을\n확실하게 뻗어주세요",
                 "팔이 살짝\n굽혀졌네요","팔을 조금만\n더 뻗어주세요",
                  "팔이 많이\n굽혀졌어요","팔을 확실하게\n뻗어주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        if a_standard>=80:
            a_text = a_list[random.randint(0,2)]
        elif a_standard>=60:
            if a_fake1>=a_fake2:
                a_text = a_list[random.randint(3,4)]
            else:
                a_text = a_list[random.randint(5,6)]
        elif a_standard>=40:
            if a_fake1>=a_fake2:
                a_text = a_list[random.randint(7,8)]
            else:
                a_text = a_list[random.randint(9,10)]
        else:
            a_text = a_list[11]


        if v_standard>=80:
            v_text = v_list[random.randint(0,2)]
        elif v_standard>=60:
            if v_fake1>=v_fake2:
                v_text = v_list[random.randint(3,4)]
            else:
                v_text = v_list[random.randint(5,6)]
        elif v_standard>=40:
            if v_fake1>=v_fake2:
                v_text = v_list[random.randint(7,8)]
            else:
                v_text = v_list[random.randint(9,10)]
        else:
            v_text = v_list[11]


        if r_standard>=80:
            r_text = r_list[random.randint(0,2)]
        elif r_standard>=60:
            if r_fake1>=r_fake2:
                r_text = r_list[random.randint(3,4)]
            else:
                r_text = r_list[random.randint(5,6)]
        elif r_standard>=40:
            if r_fake1>=r_fake2:
                r_text = r_list[random.randint(7,8)]
            else:
                r_text = r_list[random.randint(9,10)]
        else:
            r_text = r_list[11]


        total_standard = (a_standard+v_standard+r_standard)//3

        total_list = ["완벽한 동작입니다","굉장해요!",
        "잘 따라오고 있어요",
        "조금만 더 힘내봅시다","조금 아쉽네요",
        "동작이 많이 어려우셨나요?","노력이 필요해요"
        ]
        if g_count==3:
            total_text = total_list[random.randint(0,1)]
        elif g_count==2:
            total_text = total_list[2]
        elif g_count==1:
            total_text = total_list[random.randint(3,4)]
        else:
            total_text= total_list[random.randint(5,6)]



        label_num_dic = {'standard':3,'fake2':1,'fake1':2}


        def l_n(df):
            max_label = []
            label_num = []
            columns_list = list(df.columns)[1:]
            for index,row in df.iterrows():
                max_label.append(columns_list[list(row[1:]).index(max(row[1:]))])
            for i in range(len(max_label)):
                label_num.append(label_num_dic[max_label[i]])
            df['max label'] = max_label
            df['label num'] = label_num
            return df

        df_a = l_n(df_a)
        df_v = l_n(df_v)
        df_r = l_n(df_r)

        def plt_to_html(df):
            fig = plt.figure()
            plt.plot(df['id'],df['label num'])
            plt.yticks(df['label num'],df['max label'])
            imgdata = StringIO()
            fig.savefig(imgdata, format='svg',bbox_inches='tight')
            imgdata.seek(0)
            data = imgdata.getvalue()
            plt.close()
            return data

        # def plt_to_html2(df):
        #     fig = plt.figure()

        #     # df를 list로 만들어 plot 화
        #     id = df.iloc[:,0].tolist()
        #     standard = df.iloc[:,1].tolist()
        #     fake1 = df.iloc[:,2].tolist()
        #     fake2 = df.iloc[:,3].tolist()
        #     std_fake1_bottom = np.add(standard,fake1)
        #     fake1_fake2_bottom = np.add(std_fake1_bottom,fake2)
        #     plt.bar(id, standard , color = 'green')
        #     plt.bar(id, fake1, bottom=standard , color = 'orange')
        #     plt.bar(id, fake2, bottom=std_fake1_bottom, color = 'red')


        #     imgdata = StringIO()
        #     # fig1 = mpld3.fig_to_html(plt,template_type='general')
        #     # plt.close(plt)
        #     fig.savefig(imgdata, format='svg',bbox_inches='tight')
        #     imgdata.seek(0)
        #     data2 = imgdata.getvalue()

        #     plt.close()
        #     return data2
        def plt_to_html2(df):
            fig = plt.figure()
            # df를 list로 만들어 plot 화
            id = df.iloc[:,0].tolist()
            std = df.iloc[:,1].tolist()
            fake1 = df.iloc[:,2].tolist()
            fake2 = df.iloc[:,3].tolist()
            std_fake1_bottom = np.add(std,fake1)
            fake1_fake2_bottom = np.add(std_fake1_bottom,fake2)
            plt.bar(id, std , color = 'green', label='standard' )
            plt.bar(id, fake1, bottom=std , color = 'orange', label='fake1')
            plt.bar(id, fake2, bottom=std_fake1_bottom, color = 'red', label='fake2')
            plt.xlabel('Time')
            plt.ylabel('Accuracy')
            plt.legend()

            imgdata = StringIO()
            fig.savefig(imgdata, format='svg',bbox_inches='tight')
            imgdata.seek(0)
            data2 = imgdata.getvalue()
            plt.close()
            return data2



        a_graph = plt_to_html(df_a)
        a_graph2 = plt_to_html2(df_a)
        v_graph = plt_to_html(df_v)
        v_graph2 = plt_to_html2(df_v)
        r_graph = plt_to_html(df_r)
        r_graph2 = plt_to_html2(df_r)

        def round_value(df):
            s_list = list(df['standard'])
            s_list = list(map(lambda x:round(x,3),s_list))
            df['standard'] = s_list

            f1_list = list(df['fake1'])
            f1_list = list(map(lambda x:round(x,3),f1_list))
            df['fake1'] = f1_list

            f2_list = list(df['fake2'])
            f2_list = list(map(lambda x:round(x,3),f2_list))
            df['fake2'] = f2_list
            return df
        df_a = round_value(df_a)
        df_v = round_value(df_v)
        df_r = round_value(df_r)

        a_json_records = df_a.reset_index().to_json(orient ='records')
        data_a = []
        data_a = json.loads(a_json_records)
        a_data = {'d1': data_a}

        v_json_records = df_v.reset_index().to_json(orient ='records')
        data_v = []
        data_v = json.loads(v_json_records)
        v_data = {'d2': data_v}

        r_json_records = df_r.reset_index().to_json(orient ='records')
        data_r = []
        data_r = json.loads(r_json_records)
        r_data = {'d3': data_r}

        # return HttpResponse(geeks_object)
        # return JsonResponse(t_data, safe=False, json_dumps_params={'ensure_ascii': False}) # json으로 응답
        return render(request, 'br/temp.html',{'title':'result','exercise':exercise,'a_color':a_color,'v_color':v_color,'r_color':r_color,
        'a_standard':a_standard,'v_standard':v_standard,'r_standard':r_standard,
        'a_graph':a_graph,'a_graph2':a_graph2,'v_graph':v_graph,'v_graph2':v_graph2,'r_graph':r_graph,'r_graph2':r_graph2,
        'a_text':a_text,'v_text':v_text,'r_text':r_text,'total_text':total_text,'total_standard':total_standard,'d1':data_a,'d2':data_v,'d3':data_r})
    else:
        context={'msg':'start'}
        return JsonResponse(context)


def temp2(request,exercise,username,postid):
    if request.method == 'GET':
        if exercise=="양 팔 옆으로 밀기":
            tt = TwoHand0.objects.filter(username=username,id=postid).last()
        elif exercise=="양 팔 위로 밀기":
            tt = TwoHand1.objects.filter(username=username,id=postid).last()
        elif exercise=="양 팔 앞으로 밀기":
            tt = TwoHand2.objects.filter(username=username,id=postid).last()

        time_temp = tt.start_time

        c_time = str(time_temp)
        df_a = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_a_{c_time}.csv')
        df_v = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_v_{c_time}.csv')
        df_r = pd.read_csv(f'/home/jes9401/Web/myweb/br/result/{request.user.username}_r_{c_time}.csv')


        a_standard = sum(list(df_a['standard'])) /len(list(df_a['standard']))
        a_standard = int(round(a_standard, 2) * 100)
        a_fake1 = sum(list(df_a['fake1'])) /len(list(df_a['fake1']))
        a_fake1 = int(round(a_fake1,2)*100)
        a_fake2 = sum(list(df_a['fake2'])) /len(list(df_a['fake2']))
        a_fake2 = int(round(a_fake2,2)*100)

        v_standard = sum(list(df_v['standard'])) /len(list(df_v['standard']))
        v_standard = int(round(v_standard, 2) * 100)
        v_fake1 = sum(list(df_v['fake1'])) /len(list(df_v['fake1']))
        v_fake1 = int(round(v_fake1,2)*100)
        v_fake2 = sum(list(df_v['fake2'])) /len(list(df_v['fake2']))
        v_fake2 = int(round(v_fake2,2)*100)

        r_standard = sum(list(df_r['standard'])) /len(list(df_r['standard']))
        r_standard = int(round(r_standard, 2) * 100)
        r_fake1 = sum(list(df_r['fake1'])) /len(list(df_r['fake1']))
        r_fake1 = int(round(r_fake1,2)*100)
        r_fake2 = sum(list(df_r['fake2'])) /len(list(df_r['fake2']))
        r_fake2 = int(round(r_fake2,2)*100)

        if a_standard>=80:
            a_color ='green'
        elif a_standard>=40:
            a_color = 'yellow'
        else:
            a_color = 'red'

        if v_standard>=80:
            v_color ='green'
        elif v_standard>=40:
            v_color = 'yellow'
        else:
            v_color = 'red'

        if r_standard>=80:
            r_color ='green'
        elif r_standard>=40:
            r_color = 'yellow'
        else:
            r_color = 'red'


        a_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 팔이\n살짝 내려갔어요", "잘하셨지만 팔을\n조금 더 올려주세요",
                  "잘하셨는데 팔이\n많이 내려갔어요", "잘하셨지만 팔을\n확실하게 올려주세요",
                 "팔이 살짝\n내려갔어요","팔을 살짝\n올려주세요",
                  "팔이 많이\n내려갔어요","팔을 확실하게\n올려주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        v_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 속도가\n조금 느렸어요", "잘하셨지만 조금만\n더 빠르게 움직여주세요",
                  "잘하셨는데 속도가\n많이 느렸어요", "잘하셨지만 더\n빠르게 움직여주세요",
                 "속도가 조금 느렸어요","조금만 더 빠르게\n움직여주세요",
                  "속도가 많이\n느렸어요","더 빠르게\n움직여주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        r_list = ["정확해요","딱 맞아요","잘했어요",
                  "잘했지만 팔이\n살짝 굽혀졌네요", "잘하셨지만 팔을\n조금만 더 뻗어주세요",
                  "잘하셨는데 팔이\n많이 굽혀졌어요", "잘하셨지만 팔을\n확실하게 뻗어주세요",
                 "팔이 살짝\n굽혀졌네요","팔을 조금만\n더 뻗어주세요",
                  "팔이 많이\n굽혀졌어요","팔을 확실하게\n뻗어주세요",
                 "많이 어려우셨나요?\n동작을 잘 따라해주세요"]
        if a_standard>=80:
            a_text = a_list[random.randint(0,2)]
        elif a_standard>=60:
            if a_fake1>=a_fake2:
                a_text = a_list[random.randint(3,4)]
            else:
                a_text = a_list[random.randint(5,6)]
        elif a_standard>=40:
            if a_fake1>=a_fake2:
                a_text = a_list[random.randint(7,8)]
            else:
                a_text = a_list[random.randint(9,10)]
        else:
            a_text = a_list[11]


        if v_standard>=80:
            v_text = v_list[random.randint(0,2)]
        elif v_standard>=60:
            if v_fake1>=v_fake2:
                v_text = v_list[random.randint(3,4)]
            else:
                v_text = v_list[random.randint(5,6)]
        elif v_standard>=40:
            if v_fake1>=v_fake2:
                v_text = v_list[random.randint(7,8)]
            else:
                v_text = v_list[random.randint(9,10)]
        else:
            v_text = v_list[11]


        if r_standard>=80:
            r_text = r_list[random.randint(0,2)]
        elif r_standard>=60:
            if r_fake1>=r_fake2:
                r_text = r_list[random.randint(3,4)]
            else:
                r_text = r_list[random.randint(5,6)]
        elif r_standard>=40:
            if r_fake1>=r_fake2:
                r_text = r_list[random.randint(7,8)]
            else:
                r_text = r_list[random.randint(9,10)]
        else:
            r_text = r_list[11]


        total_standard = (a_standard+v_standard+r_standard)//3

        total_list = ["완벽한 동작입니다","굉장해요!",
        "잘 따라오고 있어요",
        "조금만 더 힘내봅시다","조금 아쉽네요",
        "동작이 많이 어려우셨나요?","노력이 필요해요"
        ]
        if total_standard>=80:
            total_text = total_list[random.randint(0,1)]
        elif total_standard>=60:
            total_text = total_list[2]
        elif total_standard>=40:
            total_text = total_list[random.randint(3,4)]
        else:
            total_text= total_list[random.randint(5,6)]

        label_num_dic = {'standard':3,'fake2':1,'fake1':2}


        def l_n(df):
            max_label = []
            label_num = []
            columns_list = list(df.columns)[1:]
            for index,row in df.iterrows():
                max_label.append(columns_list[list(row[1:]).index(max(row[1:]))])
            for i in range(len(max_label)):
                label_num.append(label_num_dic[max_label[i]])
            df['max label'] = max_label
            df['label num'] = label_num
            return df

        df_a = l_n(df_a)
        df_v = l_n(df_v)
        df_r = l_n(df_r)

        def plt_to_html(df):
            fig = plt.figure()
            plt.plot(df['id'],df['label num'])
            plt.yticks(df['label num'],df['max label'])
            imgdata = StringIO()
            fig.savefig(imgdata, format='svg',bbox_inches='tight')
            imgdata.seek(0)
            data = imgdata.getvalue()
            plt.close()
            return data

        # def plt_to_html2(df):
        #     fig = plt.figure()

        #     # df를 list로 만들어 plot 화
        #     id = df.iloc[:,0].tolist()
        #     standard = df.iloc[:,1].tolist()
        #     fake1 = df.iloc[:,2].tolist()
        #     fake2 = df.iloc[:,3].tolist()
        #     std_fake1_bottom = np.add(standard,fake1)
        #     fake1_fake2_bottom = np.add(std_fake1_bottom,fake2)
        #     plt.bar(id, standard , color = 'green')
        #     plt.bar(id, fake1, bottom=standard , color = 'orange')
        #     plt.bar(id, fake2, bottom=std_fake1_bottom, color = 'red')


        #     imgdata = StringIO()
        #     # fig1 = mpld3.fig_to_html(plt,template_type='general')
        #     # plt.close(plt)
        #     fig.savefig(imgdata, format='svg',bbox_inches='tight')
        #     imgdata.seek(0)
        #     data2 = imgdata.getvalue()

        #     plt.close()
        #     return data2
        def plt_to_html2(df):
            fig = plt.figure()
            # df를 list로 만들어 plot 화
            id = df.iloc[:,0].tolist()
            std = df.iloc[:,1].tolist()
            fake1 = df.iloc[:,2].tolist()
            fake2 = df.iloc[:,3].tolist()
            std_fake1_bottom = np.add(std,fake1)
            fake1_fake2_bottom = np.add(std_fake1_bottom,fake2)
            plt.bar(id, std , color = 'green', label='standard' )
            plt.bar(id, fake1, bottom=std , color = 'orange', label='fake1')
            plt.bar(id, fake2, bottom=std_fake1_bottom, color = 'red', label='fake2')
            plt.xlabel('Time')
            plt.ylabel('Accuracy')
            plt.legend()

            imgdata = StringIO()
            fig.savefig(imgdata, format='svg',bbox_inches='tight')
            imgdata.seek(0)
            data2 = imgdata.getvalue()
            plt.close()
            return data2



        a_graph = plt_to_html(df_a)
        a_graph2 = plt_to_html2(df_a)
        v_graph = plt_to_html(df_v)
        v_graph2 = plt_to_html2(df_v)
        r_graph = plt_to_html(df_r)
        r_graph2 = plt_to_html2(df_r)

        def round_value(df):
            s_list = list(df['standard'])
            s_list = list(map(lambda x:round(x,3),s_list))
            df['standard'] = s_list

            f1_list = list(df['fake1'])
            f1_list = list(map(lambda x:round(x,3),f1_list))
            df['fake1'] = f1_list

            f2_list = list(df['fake2'])
            f2_list = list(map(lambda x:round(x,3),f2_list))
            df['fake2'] = f2_list
            return df
        df_a = round_value(df_a)
        df_v = round_value(df_v)
        df_r = round_value(df_r)

        a_json_records = df_a.reset_index().to_json(orient ='records')
        data_a = []
        data_a = json.loads(a_json_records)
        a_data = {'d1': data_a}

        v_json_records = df_v.reset_index().to_json(orient ='records')
        data_v = []
        data_v = json.loads(v_json_records)
        v_data = {'d2': data_v}

        r_json_records = df_r.reset_index().to_json(orient ='records')
        data_r = []
        data_r = json.loads(r_json_records)
        r_data = {'d3': data_r}

        # return HttpResponse(geeks_object)
        # return JsonResponse(t_data, safe=False, json_dumps_params={'ensure_ascii': False}) # json으로 응답
        return render(request, 'br/temp.html',{'title':'result','exercise':exercise,'a_color':a_color,'v_color':v_color,'r_color':r_color,
        'a_standard':a_standard,'v_standard':v_standard,'r_standard':r_standard,
        'a_graph':a_graph,'a_graph2':a_graph2,'v_graph':v_graph,'v_graph2':v_graph2,'r_graph':r_graph,'r_graph2':r_graph2,
        'a_text':a_text,'v_text':v_text,'r_text':r_text,'total_text':total_text,'total_standard':total_standard,'d1':data_a,'d2':data_v,'d3':data_r})
    else:
        context={'msg':'start'}
        return JsonResponse(context)


def getmlops(request):
    # m = mlops.objects.all()
    # m_list = serializers.serialize('json', m)
    # return HttpResponse(m_list,content_type="text/json-comment-filtered") # json으로 응답
    m = mlops.objects.all()
    m_data = {}
    for i in range(len(m)):
        m_temp = {}
        m_temp['start_time'] = m[i].start_time
        m_temp['a_motion'] = m[i].a_motion
        m_temp['v_motion'] = m[i].v_motion
        m_temp['r_motion'] = m[i].r_motion
        m_temp['exercise'] = m[i].exercise

        if m_temp['a_motion'] == "fake1":
            m_temp['a_motion'] ="A10"
        elif m_temp['a_motion'] == "fake2":
            m_temp['a_motion'] ="A20"

        if m_temp['v_motion'] == "fake1":
            m_temp['v_motion']  ="V4"
        elif m_temp['v_motion'] == "fake2":
            m_temp['v_motion'] = "v5"

        if m_temp['r_motion'] == "fake1":
            m_temp['r_motion'] = "R60"
        elif m_temp['r_motion'] == "fake2":
            m_temp['r_motion'] = "R80"

        m_data[i] = m_temp
    return JsonResponse(m_data,safe=False,json_dumps_params={'ensure_ascii': False})

