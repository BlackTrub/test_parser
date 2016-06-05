#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class ProxyModel(models.Model):
	proxy_addres = models.CharField(max_length=19)
	proxy_port = models.IntegerField()
	proxy_login = models.CharField(max_length=20, default='')
	proxy_password = models.CharField(max_length=50, default='')


class UrlModel(models.Model):
	url_addres = models.CharField(max_length=100)


class DataModel(models.Model):
	data_value = models.TextField()
