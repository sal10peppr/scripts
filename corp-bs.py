# script to parse randomly generated corporate bullshit and identify keyword frequencies
# url http://cbsg.sourceforge.net/cgi-bin/live

from urlparse import urlparse as quote_plus

import requests
from bs4 import BeautifulSoup
from itertools import combinations
from json import loads
from traceback import print_exc
import operator

class Main:

	def network_call(self, url):
		print "[GET] {0}".format(url)
		r = requests.get(url);
		return r.text

	def parse(self, html_text):
		soup = BeautifulSoup(html_text, "html.parser")
		return soup.find_all("li")

	def build_dict(self, soup_items_list, d):
		skip_list = ['the', 'a', 'and', 'our', 'of', 'to', 'an', 'on','as', 'is', 'while', 'in', 'about', 'across', 'can', 'this', 'there', 'by']
		for item in soup_items_list:
			item = str(item.get_text())
			words = item.split()
			for word in words:
				if word.upper() not in (w.upper() for w in skip_list):
					d[word] = d.get(word,0) + 1
		return d


if __name__ == "__main__":
	try:
		main = Main()
		built_dict = {}
		for i in range(0,5):
			all_html = main.network_call('http://cbsg.sourceforge.net/cgi-bin/live')
			parsed = main.parse(all_html)
			built_dict = main.build_dict(parsed, built_dict)
			

		sorted_dict = sorted(built_dict.items(), key=operator.itemgetter(1), reverse=True)
		print sorted_dict
		print str(len(sorted_dict)) + ' items '
		
		
	except Exception as e:
		print_exc()