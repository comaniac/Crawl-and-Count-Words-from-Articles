#! /usr/bin/python

from crlweblib import crawl_news

target_page = "http://edition.cnn.com/WORLD/asiapcf/archive/"
database = crawl_news(target_page)
from operator import itemgetter
database.sort(key = itemgetter(1, 0), reverse = True)

for word in database:
	print word
