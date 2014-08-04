#! /usr/bin/python
import sys

# Get the source of the web page
def get_page(url):
	try:
		import urllib
		return urllib.urlopen(url).read()
	except:
		return None

# Get all report titles of the page
# Return: title_list
def get_title(page):
	title_list = []
	start_pos = 0
	while True:
		start_pos = page.find("<item><title>", start_pos)
		if start_pos == -1:
			break

		start_pos += len("<item><title>")
		end_pos = page.find("</title>", start_pos)
		url = page[start_pos : end_pos]
		title_list.append(url)		
		end_pos += len("</title>")

	return title_list
		
# Delete all punctuations in given string
def del_punct(in_str):	
	import re
	return re.findall(r"[\w]+", in_str)

# Lookup keyword from database
def lookup(database, keyword):
	for a_word in database:
		if a_word[0] == keyword:
			return a_word
	return None

# Statistic
def keyword_freq(in_list):
	database = []
	for a_title in in_list:
		for a_word in a_title:
			entry = lookup(database, a_word)
			if entry:
				entry[1] += 1
			else:
				database.append([a_word, 1])
	return database

####################################

def crawl_news(seed):
	tocrawl = []
	database = []

	import nltk
	stopwords = nltk.corpus.stopwords.words('english')
	content = fetch_cnn_news_link(get_page(seed))
	union(tocrawl, get_all_links(content))
	total_article = len(tocrawl)
	print "Ready for parsing " + str(len(tocrawl)) + " articles"
	sys.stdout.flush()
	error_cnt = 0

	while tocrawl:
		sub_link = tocrawl.pop()
		article = fetch_cnn_news_article(sub_link)
		if article == "":
			#print "Error when fetching " + str(sub_link)
			#print "\t--> Try again..."
			#sys.stdout.flush()
			article = fetch_cnn_news_article(sub_link)
			if article == "":
			#	print "\t--> Failed."
				error_cnt += 1
				continue
			#else:
			#	print "\t--> Successed."
			#sys.stdout.flush()
		add_article_to_db(database, stopwords, article)
		if len(tocrawl) % 10 == 0:
			sys.stdout.write(str(int(((total_article - len(tocrawl)) / float(total_article)) * 100)) + "%...")
			sys.stdout.flush()
	print "Fetching compeleted, failed " + str(error_cnt) + " / " + str(total_article) + " article(s)"
	return database

def fetch_cnn_news_link(content):
	start_pos = content.find("<!--default list of articles-->")
	end_pos = content.find("<!--/list of articles-->", start_pos + 1)
	return content[start_pos:end_pos]

def fetch_cnn_news_article(sub_link):
	domain = "http://edition.cnn.com"
	link = domain + str(sub_link)
	content = get_page(link)
	if content == None:
		return ""
	article = ""

	cur_pos = 0
	while True:
		start_pos = content.find('<p class="cnn_storypgraphtxt cnn_storypgraph', cur_pos)
		if start_pos == -1:
			break
		start_pos = content.find('>', start_pos) + 1
		end_pos = content.find('</p>', start_pos)
		if content[start_pos] != '<':
			article += str(content[start_pos:end_pos]) + " "
		cur_pos = end_pos + 4
	return article

def add_article_to_db(database, stopwords, article):
	# Remove HTML tags
	cur_pos = 0
	new_article = ""
	while True:
		skip_pos = article.find("<", cur_pos)
		if skip_pos == -1:
			new_article += article[cur_pos:]
			break
		new_article += article[cur_pos:skip_pos] + " "
		
		cur_pos = article.find(">", skip_pos) + 1
		end_pos = article.find("</", skip_pos)
		new_article += article[cur_pos:skip_pos] + " "
		cur_pos = article.find(">", end_pos) + 1

	# Split words
	split_list = " ,!?-'\"()"
	temp_list = new_article.split(split_list[0])
	
	for one_sep in split_list[1:]:
		temp_src = one_sep.join(temp_list)
		temp_list = temp_src.split(one_sep)

	# Process words
	content = [w for w in temp_list if w.lower() not in stopwords]

	# Add words to database
	for a_word in content:
		add_word_to_db(database, a_word)
	return database
	
def take_word(word):
	if word == "" or len(word) == 1:
		return False

	for ch in word:
		if ch.isdigit():
			return False
	return True

def add_word_to_db(database, word):
	if not take_word(word):
		return database

	word = word.lower()
	word = word.strip()		
	entry = lookup(database, word)
	if entry:
		entry[1] += 1
	else:
		database.append([word, 1])		
	return database	

def union(a, b):
	for e in b:
		if e not in a:
			a.append(e)

def get_all_links(page):
	links = []
	while True:
		url, endpos = get_next_target(page)
		if url:
			links.append(url)
			page = page[endpos:]
		else:
			break
	return links

def get_next_target(page):
	start_link = page.find('<a href=')
	if start_link == -1:
		return None, 0
	start_quote = page.find('"', start_link)
	end_quote = page.find('"', start_quote + 1)
	url = page[start_quote + 1:end_quote]
	return url, end_quote

