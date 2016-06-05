#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
from queue import Queue, Empty
from grab import Grab
from time import sleep
from models import UrlModel, ProxyModel, DataModel


def proxyParser():
	#  Add urls from the databases
	urls_data = UrlModel.objects.all()
	urls = []
	for url in urls_data:
		urls.append(url.url_addres)

	#  Add proxy from the databases
	proxy_data = ProxyModel.objects.all()
	proxy_list = []
	for proxy in proxy_data:
		proxy_list.append([proxy.proxy_addres + ':' + str(proxy.proxy_port), 
						   proxy.proxy_login + ':' + proxy.proxy_password])

	#  Append URL in queue
	queue_url = Queue()
	for url in urls:
		queue_url.put(url)

	#  Create threads
	threads = [MyThread(queue_url, proxy[0], proxy[1]) for proxy in proxy_list if checkProxy(proxy[0], proxy[1])]
	for thread in threads:
		thread.start()

	correct_time = threading.Thread(target=correctTimeThread, args=(threads, queue_url,))
	correct_time.start()

	for thread in threads:
		thread.join()
	correct_time.join()


def correctTimeThread(threads, queue):
	while not queue.empty():
		count = 0
		for thread in threads:
			count += thread.count
		for thread in threads:
			if thread.count > count/len(threads):
				thread.must_wait = True


def checkProxy(proxy, proxy_userpwd, url='https://www.google.ru/'):
	if proxy:
		try:
			g = Grab()
			g.setup(proxy=proxy, proxy_userpwd=proxy_userpwd)
			g.go(url)
			return 1
		except Exception:
			return 0


class MyThread(threading.Thread):
	def __init__(self, queue, proxy, proxy_userpwd):
		super(MyThread, self).__init__()
		self.proxy = proxy
		self.proxy_userpwd = proxy_userpwd
		self.must_wait = False
		self.queue = queue
		self.demon = True
		self.grab_obj = Grab()
		self.grab_obj.setup(proxy=self.proxy, proxy_userpwd=self.proxy_userpwd)
		self.count = 0
		self.sleep_time = 2.5

	def actionURL(self, url):
		self.count += 1
		self.grab_obj.go(url)
		#  Add data from URL to DataModel
		DataModel.objects.create(data_value=self.grab_obj.response.unicode_body())

	def run(self):
		while True:
			if self.must_wait:
				sleep(self.sleep_time)
				self.must_wait = False
			try:
				task = self.queue.get(False)
				self.actionURL(task)
				self.queue.task_done()
			#  Empty attribute class queue
			except Empty:
				break
			#  If task is not completed, add task to queue
			except Exception:
				self.queue.task_done()
				self.queue.put(task, block=False)

		self.queue.join()


if __name__ == '__main__':
	proxyParser()