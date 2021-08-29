from django.db import models
from django.conf import settings
import os.path

class chek(models.Model):
    start_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    end_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)


class TwoHand0(models.Model):
    username = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    end_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    a_motion = models.CharField(max_length=50,default="")
    v_motion = models.CharField(max_length=50,default="")
    r_motion = models.CharField(max_length=50,default="")
    a_value = models.FloatField(default=0)
    v_value = models.FloatField(default=0)
    r_value = models.FloatField(default=0)
    temp = models.IntegerField(default=0)


class TwoHand1(models.Model):
    username = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    end_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    a_motion = models.CharField(max_length=50,default="")
    v_motion = models.CharField(max_length=50,default="")
    r_motion = models.CharField(max_length=50,default="")
    a_value = models.FloatField(default=0)
    v_value = models.FloatField(default=0)
    r_value = models.FloatField(default=0)
    temp = models.IntegerField(default=0)


class TwoHand2(models.Model):
    username = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    end_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    a_motion = models.CharField(max_length=50,default="")
    v_motion = models.CharField(max_length=50,default="")
    r_motion = models.CharField(max_length=50,default="")
    a_value = models.FloatField(default=0)
    v_value = models.FloatField(default=0)
    r_value = models.FloatField(default=0)
    temp = models.IntegerField(default=0)


class mlops(models.Model):
    start_time = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    a_motion = models.CharField(max_length=50,default="")
    v_motion = models.CharField(max_length=50,default="")
    r_motion = models.CharField(max_length=50,default="")
    exercise = models.CharField(max_length=50,default="")